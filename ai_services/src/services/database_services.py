# ai_services/src/services/database_services.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text, String
from typing import List, Dict, Any, Optional, Tuple
from backend.src.utils.logger.logging import logger as logging
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer


class DatabaseService:
    """Handles structured SQL queries for laptop data"""

    @staticmethod
    def get_laptops_by_budget(
        db: Session, min_price: float = 0, max_price: float = 10000
    ) -> List[Laptop]:
        """Get laptops within budget range"""
        try:
            # Convert to float to ensure proper comparison
            min_price = float(min_price)
            max_price = float(max_price)

            # Get latest prices for each laptop
            latest_prices = db.execute(
                text(
                    """
                SELECT DISTINCT ON (laptop_id)
                    laptop_id, price
                FROM price_snapshots
                WHERE price IS NOT NULL
                ORDER BY laptop_id, scraped_at DESC
            """
                )
            ).fetchall()

            # Filter by budget
            valid_laptop_ids = [
                row.laptop_id
                for row in latest_prices
                if min_price <= float(row.price) <= max_price
            ]

            return db.query(Laptop).filter(Laptop.id.in_(valid_laptop_ids)).all()

        except Exception as e:
            logging.error(f"Error getting laptops by budget: {e}")
            return []

    @staticmethod
    def get_laptops_by_specs(db: Session, spec_filters: Dict[str, str]) -> List[Laptop]:
        """Get laptops matching specification criteria"""
        try:
            laptop_ids = set()

            for category, value in spec_filters.items():
                # Search in both specification_value and structured_value
                specs = (
                    db.query(Specification)
                    .filter(
                        and_(
                            Specification.category.ilike(f"%{category}%"),
                            or_(
                                Specification.specification_value.ilike(f"%{value}%"),
                                # Fixed: Use cast to String instead of .astext
                                Specification.structured_value.cast(String).ilike(
                                    f"%{value}%"
                                ),
                            ),
                        )
                    )
                    .all()
                )

                current_laptop_ids = {spec.laptop_id for spec in specs}

                if not laptop_ids:  # First filter
                    laptop_ids = current_laptop_ids
                else:  # Intersection with previous filters
                    laptop_ids = laptop_ids.intersection(current_laptop_ids)

            return db.query(Laptop).filter(Laptop.id.in_(laptop_ids)).all()

        except Exception as e:
            logging.error(f"Error getting laptops by specs: {e}")
            return []

    @staticmethod
    def get_laptop_summary(db: Session, laptop_id: int) -> Dict[str, Any]:
        """Get comprehensive laptop summary"""
        try:
            # Ensure laptop_id is an integer
            laptop_id = int(laptop_id)

            laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
            if not laptop:
                return {}

            # Get latest price
            latest_price = (
                db.query(PriceSnapshot)
                .filter(PriceSnapshot.laptop_id == laptop_id)
                .order_by(PriceSnapshot.scraped_at.desc())
                .first()
            )

            # Get review summary
            review_stats = db.execute(
                text(
                    """
                SELECT
                    COUNT(*) as total_reviews,
                    AVG(rating) as avg_rating,
                    COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_reviews
                FROM reviews
                WHERE laptop_id = :laptop_id
            """
                ),
                {"laptop_id": laptop_id},
            ).fetchone()

            # Get key specifications
            key_specs = (
                db.query(Specification)
                .filter(
                    and_(
                        Specification.laptop_id == laptop_id,
                        Specification.category.in_(
                            ["Processor", "Memory", "Storage", "Graphics"]
                        ),
                    )
                )
                .all()
            )

            return {
                "laptop": laptop,
                "latest_price": latest_price.price if latest_price else None,
                "availability": (
                    latest_price.availability_status if latest_price else None
                ),
                "review_count": review_stats.total_reviews if review_stats else 0,
                "avg_rating": (
                    float(review_stats.avg_rating)
                    if review_stats and review_stats.avg_rating
                    else 0
                ),
                "positive_reviews": (
                    review_stats.positive_reviews if review_stats else 0
                ),
                "key_specs": {
                    spec.category: spec.specification_value for spec in key_specs
                },
            }

        except Exception as e:
            logging.error(f"Error getting laptop summary: {e}")
            return {}

    @staticmethod
    def search_laptops_text(db: Session, query: str) -> List[Laptop]:
        """Text search across laptop names and specifications"""
        try:
            # Search in laptop names
            name_matches = (
                db.query(Laptop)
                .filter(Laptop.full_model_name.ilike(f"%{query}%"))
                .all()
            )

            # Search in specifications
            spec_matches = (
                db.query(Laptop)
                .join(Specification)
                .filter(
                    or_(
                        Specification.specification_value.ilike(f"%{query}%"),
                        Specification.specification_name.ilike(f"%{query}%"),
                    )
                )
                .distinct()
                .all()
            )

            # Combine and deduplicate
            all_matches = {laptop.id: laptop for laptop in name_matches + spec_matches}
            return list(all_matches.values())

        except Exception as e:
            logging.error(f"Error in text search: {e}")
            return []

    @staticmethod
    def get_price_trends(
        db: Session, laptop_id: int, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get price trends for a laptop"""
        try:
            trends = db.execute(
                text(
                    """
                SELECT price, availability_status, configuration_summary, scraped_at
                FROM price_snapshots
                WHERE laptop_id = :laptop_id
                AND scraped_at >= NOW() - INTERVAL ':days days'
                ORDER BY scraped_at DESC
            """
                ),
                {"laptop_id": laptop_id, "days": days},
            ).fetchall()

            return [
                {
                    "price": float(trend.price) if trend.price else None,
                    "availability": trend.availability_status,
                    "configuration": trend.configuration_summary,
                    "date": trend.scraped_at.isoformat(),
                }
                for trend in trends
            ]

        except Exception as e:
            logging.error(f"Error getting price trends: {e}")
            return []


# Global instance
database_service = DatabaseService()
