# backend/src/app/services/langchain_tools.py
from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.src.utils.logger.logging import logger as logging
from ai_services.src.services.database_services import database_service
from ai_services.src.services.vector_service import vector_service


class BudgetSearchInput(BaseModel):
    min_price: float = Field(default=0, description="Minimum price in USD")
    max_price: float = Field(description="Maximum price in USD")


class SpecSearchInput(BaseModel):
    spec_filters: Dict[str, str] = Field(
        description="Dictionary of category: value filters"
    )


class LaptopSummaryInput(BaseModel):
    laptop_id: int = Field(description="Laptop ID to get summary for")


class VectorSearchInput(BaseModel):
    query: str = Field(description="Search query text")
    laptop_id: Optional[int] = Field(
        default=None, description="Optional laptop ID filter"
    )
    limit: int = Field(default=5, description="Maximum number of results")


class BudgetSearchTool(BaseTool):
    name: str = "search_laptops_by_budget"  # Add type annotation
    description: str = "Find laptops within a specific price range"
    args_schema: Type[BaseModel] = BudgetSearchInput  # Add type annotation

    def _run(self, min_price: float = 0, max_price: float = 10000, **kwargs) -> str:
        db = kwargs.get("db")
        if not db:
            logging.warning("Database session not available")
            return "Database session not available"

        laptops = database_service.get_laptops_by_budget(db, min_price, max_price)

        if not laptops:
            logging.warning(f"No laptops found between ${min_price} and ${max_price}")
            return f"No laptops found between ${min_price} and ${max_price}"

        result = f"Found {len(laptops)} laptops in budget ${min_price}-${max_price}:\n"
        for laptop in laptops:
            result += f"- {laptop.full_model_name} (ID: {laptop.id})\n"

        return result


class SpecSearchTool(BaseTool):
    name: str = "search_laptops_by_specs"  # Add type annotation
    description: str = "Find laptops matching specific technical specifications"
    args_schema: Type[BaseModel] = SpecSearchInput  # Add type annotation

    def _run(self, spec_filters: Dict[str, str], **kwargs) -> str:
        db = kwargs.get("db")
        if not db:
            logging.warning("Database session not available")
            return "Database session not available"

        laptops = database_service.get_laptops_by_specs(db, spec_filters)

        if not laptops:
            logging.warning(f"No laptops found matching specs: {spec_filters}")
            return f"No laptops found matching specs: {spec_filters}"

        result = f"Found {len(laptops)} laptops matching {spec_filters}:\n"
        for laptop in laptops:
            result += f"- {laptop.full_model_name} (ID: {laptop.id})\n"

        return result


class LaptopSummaryTool(BaseTool):
    name: str = "get_laptop_summary"  # Add type annotation
    description: str = (
        "Get detailed summary of a specific laptop including specs, price, and reviews"
    )
    args_schema: Type[BaseModel] = LaptopSummaryInput  # Add type annotation

    def _run(self, laptop_id: int, **kwargs) -> str:
        db = kwargs.get("db")
        if not db:
            logging.warning("Database session not available")
            return "Database session not available"

        # Add validation
        if not laptop_id or laptop_id == "":
            return "Error: Valid laptop ID is required"

        try:
            laptop_id = int(laptop_id)  # Ensure it's an integer
        except (ValueError, TypeError):
            return f"Error: Invalid laptop ID format: {laptop_id}"

        summary = database_service.get_laptop_summary(db, laptop_id)

        if not summary:
            logging.warning(f"No laptop found with ID {laptop_id}")
            return f"No laptop found with ID {laptop_id}"

        laptop = summary["laptop"]
        result = f"Laptop: {laptop.full_model_name}\n"
        result += f"Brand: {laptop.brand}\n"
        result += f"Latest Price: ${summary['latest_price']}\n"
        result += f"Availability: {summary['availability']}\n"
        result += f"Average Rating: {summary['avg_rating']:.1f} ({summary['review_count']} reviews)\n"
        result += f"Key Specs: {summary['key_specs']}\n"

        return result


class ReviewSearchTool(BaseTool):
    name: str = "search_reviews"  # Add type annotation
    description: str = (
        "Search user reviews for experience-based information about laptops"
    )
    args_schema: Type[BaseModel] = VectorSearchInput  # Add type annotation

    def _run(
        self, query: str, laptop_id: Optional[int] = None, limit: int = 5, **kwargs
    ) -> str:
        results = vector_service.search_reviews(query, laptop_id, limit)

        if not results:
            logging.warning(f"No reviews found for query: {query}")
            return f"No reviews found for query: {query}"

        result = f"Found {len(results)} relevant reviews:\n"
        for i, review in enumerate(results):
            result += f"{i+1}. {review['metadata']['laptop_name']} - Rating: {review['metadata']['rating']}\n"
            result += f"   {review['document'][:150]}...\n\n"

        return result


class QASearchTool(BaseTool):
    name: str = "search_qa"  # Add type annotation
    description: str = "Search Q&A pairs for specific questions about laptops"
    args_schema: Type[BaseModel] = VectorSearchInput  # Add type annotation

    def _run(
        self, query: str, laptop_id: Optional[int] = None, limit: int = 5, **kwargs
    ) -> str:
        results = vector_service.search_qa(query, laptop_id, limit)

        if not results:
            logging.warning(f"No Q&A found for query: {query}")
            return f"No Q&A found for query: {query}"

        result = f"Found {len(results)} relevant Q&A pairs:\n"
        for i, qa in enumerate(results):
            result += f"{i+1}. {qa['metadata']['laptop_name']}\n"
            result += f"   Q: {qa['metadata']['question'][:100]}...\n"
            result += f"   A: {qa['metadata']['answer'][:100]}...\n\n"

        return result


# Tool list for the agent
def get_laptop_tools() -> List[BaseTool]:
    return [
        BudgetSearchTool(),
        SpecSearchTool(),
        LaptopSummaryTool(),
        ReviewSearchTool(),
        QASearchTool(),
    ]
