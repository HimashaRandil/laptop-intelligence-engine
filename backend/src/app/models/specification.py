from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..core.db import Base


class Specification(Base):
    __tablename__ = "specifications"

    id = Column(Integer, primary_key=True)
    laptop_id = Column(
        Integer, ForeignKey("laptops.id", ondelete="CASCADE"), nullable=False
    )
    category = Column(String(100), nullable=False)
    specification_name = Column(String(200), nullable=False)
    specification_value = Column(Text, nullable=False)
    unit = Column(String(20))
    structured_value = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    laptop = relationship("Laptop", back_populates="specifications")
