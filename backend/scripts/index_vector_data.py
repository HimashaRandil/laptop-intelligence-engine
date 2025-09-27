import sys
import os
from pathlib import Path

from backend.src.app.core.db import SessionLocal
from backend.src.app.services.vector_service import vector_service
from backend.src.utils.logger.logging import logger as logging


def main():
    """Index all reviews and Q&A data into ChromaDB"""
    db = SessionLocal()

    try:
        logging.info("Starting vector data indexing...")

        # Get initial stats
        initial_stats = vector_service.get_collection_stats()
        logging.info(f"Initial stats: {initial_stats}")

        # Index reviews
        logging.info("Indexing reviews...")
        reviews_success = vector_service.index_reviews(db)

        # Index Q&A
        logging.info("Indexing Q&A pairs...")
        qa_success = vector_service.index_qa(db)

        # Get final stats
        final_stats = vector_service.get_collection_stats()
        logging.info(f"Final stats: {final_stats}")

        if reviews_success and qa_success:
            logging.info("Vector data indexing completed successfully!")
            logging.info("✅ Vector database populated successfully")
            logging.info(f"📊 Reviews indexed: {final_stats['reviews_count']}")
            logging.info(f"📊 Q&A pairs indexed: {final_stats['qa_count']}")
        else:
            logging.error("Some indexing operations failed")
            logging.error("❌ Indexing completed with errors")

    except Exception as e:
        logging.error(f"Error during indexing: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
