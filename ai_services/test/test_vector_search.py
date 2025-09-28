# backend/scripts/test_vector_search.py
import sys
from pathlib import Path

from ai_services.src.services.vector_service import vector_service


def test_searches():
    """Test vector search functionality"""

    print("🔍 Testing Vector Search...")

    # Test review search
    print("\n--- Testing Review Search ---")
    review_results = vector_service.search_reviews("battery life performance")
    for i, result in enumerate(review_results[:3]):
        print(f"{i+1}. Distance: {result['distance']:.3f}")
        print(f"   Laptop: {result['metadata']['laptop_name']}")
        print(f"   Rating: {result['metadata']['rating']}")
        print(f"   Snippet: {result['document'][:100]}...")
        print()

    # Test Q&A search
    print("\n--- Testing Q&A Search ---")
    qa_results = vector_service.search_qa("programming development coding")
    for i, result in enumerate(qa_results[:3]):
        print(f"{i+1}. Distance: {result['distance']:.3f}")
        print(f"   Laptop: {result['metadata']['laptop_name']}")
        print(f"   Question: {result['metadata']['question'][:80]}...")
        print()

    # Test laptop-specific search
    print("\n--- Testing Laptop-Specific Search ---")
    laptop_reviews = vector_service.search_reviews("good performance", laptop_id=1)
    print(f"Found {len(laptop_reviews)} reviews for laptop ID 1")

    # Get stats
    stats = vector_service.get_collection_stats()
    print(f"\n📊 Collection Stats: {stats}")


if __name__ == "__main__":
    test_searches()
