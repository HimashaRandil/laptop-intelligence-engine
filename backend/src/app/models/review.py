from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
    ForeignKey,
    Boolean,
    Date,
)
from sqlalchemy.orm import relationship
from ..core.db import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    laptop_id = Column(
        Integer, ForeignKey("laptops.id", ondelete="CASCADE"), nullable=False
    )
    rating = Column(Integer)
    review_title = Column(Text)
    review_text = Column(Text)
    reviewer_name = Column(String(200))
    reviewer_verified = Column(Boolean, default=False)
    review_date = Column(Date)
    helpful_count = Column(Integer, default=0)
    configuration_summary = Column(Text)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    laptop = relationship("Laptop", back_populates="reviews")
