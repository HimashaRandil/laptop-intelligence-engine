from sqlalchemy import Column, Integer, String, Text, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from ..core.db import Base


class Laptop(Base):
    __tablename__ = "laptops"

    id = Column(Integer, primary_key=True)
    brand = Column(String(50), nullable=False)
    model_name = Column(String(200), nullable=False)
    variant = Column(String(100))
    full_model_name = Column(String(300), nullable=False)
    product_page_url = Column(Text)
    pdf_spec_url = Column(Text, nullable=False)
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "brand", "model_name", "variant", name="unique_laptop_variant"
        ),
    )

    specifications = relationship(
        "Specification", back_populates="laptop", cascade="all, delete-orphan"
    )
    price_snapshots = relationship(
        "PriceSnapshot", back_populates="laptop", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "Review", back_populates="laptop", cascade="all, delete-orphan"
    )
    questions_answers = relationship(
        "QuestionsAnswer", back_populates="laptop", cascade="all, delete-orphan"
    )
