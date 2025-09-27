from typing import Dict, Any, List
from langgraph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session
import json

from .langchain_tools import get_laptop_tools
from ..config.ai_config import AIConfig


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
- search_laptops_by_budget: For price-based queries
- search_laptops_by_specs: For specification requirements
- get_laptop_summary: For detailed laptop information
- search_reviews: For user experience questions
- search_qa: For specific Q&A about features

Return a JSON object with:
{
    "tools_needed": ["tool1", "tool2"],
    "tool_params": {
        "tool1": {"param": "value"},
        "tool2": {"param": "value"}
    },
    "intent": "budget_search|spec_search|comparison|experience_question"
}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_query"]),
        ]

        response = self.llm.invoke(messages)

        try:
            analysis = json.loads(response.content)
            state["context"]["analysis"] = analysis
        except json.JSONDecodeError:
            # Fallback analysis
            state["context"]["analysis"] = {
                "tools_needed": ["search_reviews"],
                "tool_params": {"search_reviews": {"query": state["user_query"]}},
                "intent": "general_question",
            }

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
                    tool_results[tool_name] = f"Error: {str(e)}"

        state["context"]["tool_results"] = tool_results
        return state

    def _synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize final response from tool results"""
        system_prompt = """You are a helpful laptop recommendation assistant. Based on the tool results, provide a comprehensive, helpful response to the user's query.

Guidelines:
- Be specific and cite information from the tools
- Include relevant laptop models, prices, and specifications
- Mention user reviews when relevant
- Provide clear recommendations
- Keep the response conversational and helpful"""

        tool_results = state["context"]["tool_results"]
        context_text = "\n".join(
            [f"{tool}: {result}" for tool, result in tool_results.items()]
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"User Query: {state['user_query']}\n\nTool Results:\n{context_text}"
            ),
        ]

        response = self.llm.invoke(messages)
        state["final_response"] = response.content

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

        final_state = self.graph.invoke(initial_state)
        return final_state["final_response"]


# Global instance
laptop_agent = LaptopAgent()
