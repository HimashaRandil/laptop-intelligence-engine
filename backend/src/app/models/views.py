from sqlalchemy import Table, Column, Integer, String, DECIMAL
from ..core.db import Base


# Map to the laptop_review_summary view
class LaptopReviewSummary(Base):
    __tablename__ = "laptop_review_summary"
    laptop_id = Column(Integer, primary_key=True)
    total_reviews = Column(Integer)
    average_rating = Column(DECIMAL)


# Map to the laptop_latest_prices view
class LaptopLatestPrice(Base):
    __tablename__ = "laptop_latest_prices"
    laptop_id = Column(Integer, primary_key=True)
    price = Column(DECIMAL)
    availability_status = Column(String)
