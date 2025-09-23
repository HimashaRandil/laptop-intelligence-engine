from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import relationship
from ..core.db import Base


class QuestionsAnswer(Base):
    __tablename__ = "questions_answers"

    id = Column(Integer, primary_key=True)
    laptop_id = Column(
        Integer, ForeignKey("laptops.id", ondelete="CASCADE"), nullable=False
    )
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text)
    asker_name = Column(String(200))
    answerer_name = Column(String(200))
    question_date = Column(Date)
    answer_date = Column(Date)
    helpful_count = Column(Integer, default=0)
    configuration_summary = Column(Text)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    laptop = relationship("Laptop", back_populates="questions_answers")
