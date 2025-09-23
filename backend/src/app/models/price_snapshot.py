from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
    ForeignKey,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from ..core.db import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True)
    laptop_id = Column(
        Integer, ForeignKey("laptops.id", ondelete="CASCADE"), nullable=False
    )
    price = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")
    availability_status = Column(String(50))
    shipping_info = Column(Text)
    promotion_text = Column(Text)
    configuration_summary = Column(Text)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    laptop = relationship("Laptop", back_populates="price_snapshots")
