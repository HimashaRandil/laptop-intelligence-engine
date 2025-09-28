# backend/src/app/services/langgraph_agent.py
from typing import Dict, Any, List

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    try:
        from langgraph import StateGraph, END
    except ImportError:
        # Fallback for older versions
        from langgraph.graph.state import StateGraph
        from langgraph.graph import END

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session
import json

from backend.src.utils.logger.logging import logger as logging
from ai_services.src.services.langchain_tools import get_laptop_tools
from backend.src.app.config.ai_config import AIConfig


class AgentState(Dict):
    """State object for the agent graph"""

    messages: List[Any]
    user_query: str
    context: Dict[str, Any]
    db_session: Session
    final_response: str


class LaptopAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=AIConfig.DEFAULT_MODEL,
            temperature=AIConfig.TEMPERATURE,
            api_key=AIConfig.OPENAI_API_KEY,
        )
        self.tools = get_laptop_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}

        # Create the graph
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("analyze_query", self._analyze_query)
        graph.add_node("execute_tools", self._execute_tools)
        graph.add_node("synthesize_response", self._synthesize_response)

        # Add edges
        graph.add_edge("analyze_query", "execute_tools")
        graph.add_edge("execute_tools", "synthesize_response")
        graph.add_edge("synthesize_response", END)

        # Set entry point
        graph.set_entry_point("analyze_query")

        return graph.compile()

    def _analyze_query(self, state: AgentState) -> AgentState:
        """Analyze user query and determine which tools to use"""
        system_prompt = """You are a laptop recommendation assistant. Analyze the user query and determine which tools you need to use.

Available tools:
- search_laptops_by_budget: For price-based queries (params: min_price, max_price)
- search_laptops_by_specs: For specification requirements (params: spec_filters as dict)
- get_laptop_summary: For detailed laptop information (params: laptop_id)
- search_reviews: For user experience questions (params: query, laptop_id optional, limit)
- search_qa: For specific Q&A about features (params: query, laptop_id optional, limit)

Examples:
- "laptops under $800" -> search_laptops_by_budget
- "Intel i7 with 16GB RAM" -> search_laptops_by_specs
- "tell me about laptop ID 1" -> get_laptop_summary
- "battery life reviews" -> search_reviews
- "how to upgrade memory" -> search_qa

IMPORTANT RULES:
1. ONLY recommend laptops from our inventory
2. If our tools don't find matching laptops, say we don't have what they're looking for
3. Never recommend external laptops or brands not in our inventory
4. Stay focused on laptop-related queries only

Return a JSON object with:
{
    "tools_needed": ["tool_name"],
    "tool_params": {
        "tool_name": {"param": "value"}
    },
    "intent": "budget_search|spec_search|laptop_details|experience_question|technical_question"
}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User query: {state['user_query']}"),
        ]

        try:
            response = self.llm.invoke(messages)
            analysis = json.loads(response.content)
            state["context"]["analysis"] = analysis
        except (json.JSONDecodeError, Exception) as e:
            logging.warning(f"Failed to parse analysis, using fallback: {e}")
            # Fallback analysis based on keywords
            query_lower = state["user_query"].lower()
            if any(word in query_lower for word in ["price", "budget", "cost", "$"]):
                analysis = {
                    "tools_needed": ["search_laptops_by_budget"],
                    "tool_params": {
                        "search_laptops_by_budget": {"min_price": 0, "max_price": 2000}
                    },
                    "intent": "budget_search",
                }
            else:
                analysis = {
                    "tools_needed": ["search_reviews"],
                    "tool_params": {
                        "search_reviews": {"query": state["user_query"], "limit": 3}
                    },
                    "intent": "general_question",
                }
            state["context"]["analysis"] = analysis

        return state

    def _execute_tools(self, state: AgentState) -> AgentState:
        """Execute the determined tools"""
        analysis = state["context"]["analysis"]
        tool_results = {}

        for tool_name in analysis["tools_needed"]:
            if tool_name in self.tool_map:
                tool = self.tool_map[tool_name]
                params = analysis["tool_params"].get(tool_name, {})
                params["db"] = state["db_session"]

                try:
                    result = tool._run(**params)
                    tool_results[tool_name] = result
                except Exception as e:
                    logging.error(f"Tool {tool_name} failed: {e}")
                    tool_results[tool_name] = f"Error executing {tool_name}: {str(e)}"

        state["context"]["tool_results"] = tool_results
        return state

    def _synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize final response from tool results"""
        system_prompt = """You are a helpful laptop recommendation assistant. Based on the tool results, provide a comprehensive, helpful response to the user's query.

INVENTORY CONSTRAINT:
- NEVER recommend laptops outside our inventory
- If tools return no results, say "We don't currently have laptops matching those requirements in our inventory"

Guidelines:
- Only discuss laptops from our inventory
- Be specific and cite information from the tools
- Include relevant laptop models, prices, and specifications when available
- Mention user reviews and ratings when relevant
- Provide clear recommendations with reasoning
- Keep the response conversational and helpful
- If tool results show errors, acknowledge limitations but still try to be helpful
- If asked about features we don't have, clearly state we don't carry those models
- Focus on what we DO have available
- Use information from tools (reviews, specs, prices) for our inventory only
- Format information clearly with proper structure
- Keep responses professional and sales-focused

FORBIDDEN:
- Never mention MSI, Acer, Dell, or other brands not in our inventory
- Never suggest external retailers or competitors
- Never recommend laptops we don't sell

"""

        tool_results = state["context"]["tool_results"]
        context_text = "\n".join(
            [
                f"=== {tool.upper()} RESULTS ===\n{result}\n"
                for tool, result in tool_results.items()
            ]
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"""
User Query: {state['user_query']}

Tool Results:
{context_text}

Please provide a helpful response based on this information.
"""
            ),
        ]

        try:
            response = self.llm.invoke(messages)
            state["final_response"] = response.content
        except Exception as e:
            logging.error(f"LLM synthesis failed: {e}")
            state["final_response"] = (
                "I encountered an error processing your request. Please try again or rephrase your question."
            )

        return state

    def process_query(self, user_query: str, db_session: Session) -> str:
        """Process a user query and return a response"""
        initial_state = AgentState(
            messages=[],
            user_query=user_query,
            context={},
            db_session=db_session,
            final_response="",
        )

        try:
            final_state = self.graph.invoke(initial_state)
            return final_state["final_response"]
        except Exception as e:
            logging.error(f"Agent processing failed: {e}")
            return f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question."


# Global instance
laptop_agent = LaptopAgent()
