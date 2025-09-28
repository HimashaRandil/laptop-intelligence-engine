# backend/scripts/test_individual_tools.py
import sys
import os
from pathlib import Path

from backend.src.app.core.db import SessionLocal
from ai_services.src.services.langchain_tools import get_laptop_tools


def test_individual_tools():
    """Test each tool individually to make sure they work"""
    db = SessionLocal()

    try:
        print("Getting laptop tools...")
        tools = get_laptop_tools()
        print(f"Found {len(tools)} tools: {[tool.name for tool in tools]}")

        # Test 1: Budget Search Tool
        print("\n" + "=" * 50)
        print("TEST 1: Budget Search Tool")
        print("=" * 50)

        budget_tool = next(
            (tool for tool in tools if tool.name == "search_laptops_by_budget"), None
        )
        if budget_tool:
            try:
                result = budget_tool._run(min_price=500, max_price=1500, db=db)
                print("SUCCESS - Budget tool result:")
                print(result[:300] + "..." if len(result) > 300 else result)
            except Exception as e:
                print(f"ERROR in budget tool: {e}")
        else:
            print("ERROR: Budget tool not found")

        # Test 2: Review Search Tool
        print("\n" + "=" * 50)
        print("TEST 2: Review Search Tool")
        print("=" * 50)

        review_tool = next(
            (tool for tool in tools if tool.name == "search_reviews"), None
        )
        if review_tool:
            try:
                result = review_tool._run(query="battery", limit=2, db=db)
                print("SUCCESS - Review tool result:")
                print(result[:300] + "..." if len(result) > 300 else result)
            except Exception as e:
                print(f"ERROR in review tool: {e}")
        else:
            print("ERROR: Review tool not found")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_individual_tools()
