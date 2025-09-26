"""
Database reset script - clears PriceSnapshot, Review, QuestionsAnswer tables only.
Preserves laptop and specification data.
"""

from sqlalchemy.orm import Session
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.utils.logger.logging import logger as logging


def reset_scraping_tables():
    """Reset only the scraping-related tables, preserve laptop and specification data."""
    db = SessionLocal()

    try:
        logging.info("Starting database reset for scraping tables...")
        logging.info("=" * 60)

        # Get counts before deletion
        price_count = db.query(PriceSnapshot).count()
        review_count = db.query(Review).count()
        qa_count = db.query(QuestionsAnswer).count()

        logging.info("Before reset:")
        logging.info(f"  Price snapshots: {price_count}")
        logging.info(f"  Reviews: {review_count}")
        logging.info(f"  Q&A entries: {qa_count}")

        # Delete data from scraping tables
        try:
            # Delete in order to respect foreign key constraints
            deleted_qa = db.query(QuestionsAnswer).delete()
            deleted_reviews = db.query(Review).delete()
            deleted_prices = db.query(PriceSnapshot).delete()

            # Commit the deletions
            db.commit()

            logging.info("Deleted:")
            logging.info(f"  Q&A entries: {deleted_qa}")
            logging.info(f"  Reviews: {deleted_reviews}")
            logging.info(f"  Price snapshots: {deleted_prices}")

        except Exception as e:
            db.rollback()
            raise

        # Verify deletion
        price_count_after = db.query(PriceSnapshot).count()
        review_count_after = db.query(Review).count()
        qa_count_after = db.query(QuestionsAnswer).count()

        logging.info("After reset:")
        logging.info(f"  Price snapshots: {price_count_after}")
        logging.info(f"  Reviews: {review_count_after}")
        logging.info(f"  Q&A entries: {qa_count_after}")

        # Verify laptop and specification tables are intact
        from backend.src.app.models.laptop import Laptop
        from backend.src.app.models.specification import Specification

        laptop_count = db.query(Laptop).count()
        spec_count = db.query(Specification).count()

        logging.info("Preserved tables:")
        logging.info(f"  Laptops: {laptop_count}")
        logging.info(f"  Specifications: {spec_count}")

        if laptop_count == 4 and spec_count > 0:
            logging.info(
                "✅ Database reset successful - laptop and specification data preserved"
            )
        else:
            logging.error("⚠️ Unexpected data counts - check database integrity")

        logging.info("=" * 60)
        logging.info("Database reset completed. Ready for fresh scraping.")

    except Exception as e:
        logging.error(f"Database reset failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_scraping_tables()
