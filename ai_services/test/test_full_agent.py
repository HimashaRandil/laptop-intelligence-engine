# backend/tests/test_full_agent.py
import sys
import os
from pathlib import Path

from backend.src.app.core.db import SessionLocal
from ai_services.src.services.langgraph_agent import laptop_agent
from backend.src.utils.logger.logging import logger as logging


def test_simple_query():
    """Test the agent with one simple query first"""
    db = SessionLocal()

    try:
        print("Testing simple budget query...")
        query = "What laptops are available under $1000?"

        print(f"Query: {query}")
        print("-" * 50)

        response = laptop_agent.process_query(query, db)
        print(f"Response: {response}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(f"Simple query test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        db.close()


def test_multiple_queries():
    """Test multiple query types"""
    db = SessionLocal()

    test_queries = [
        "What laptops cost between $800 and $1200?",
        "Tell me about battery life in reviews",
        "What are the specs for laptop ID 1?",
    ]

    try:
        print("\nTesting multiple queries...")

        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {query}")
            print("=" * 60)

            try:
                response = laptop_agent.process_query(query, db)
                print(f"Response: {response[:200]}...")  # Show first 200 chars

            except Exception as e:
                print(f"ERROR: {e}")
                logging.error(f"Query {i} failed: {query} - Error: {e}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("Testing LangGraph Agent...")

    # Test simple query first
    simple_success = test_simple_query()

    if simple_success:
        print("\nSimple test passed! Testing multiple queries...")
        test_multiple_queries()
    else:
        print("\nSimple test failed. Check your configuration.")

    print("\nAgent testing completed!")
