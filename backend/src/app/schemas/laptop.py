from pydantic import BaseModel
from datetime import date
from typing import List, Optional, Any


# A base schema for a single specification
class SpecificationBase(BaseModel):
    category: str
    specification_name: str
    specification_value: str
    structured_value: Optional[Any] = None  # For the JSON data

    class Config:
        from_attributes = True  # Replaces orm_mode in Pydantic v2


# A base schema for a single price snapshot
class PriceSnapshotBase(BaseModel):
    price: Optional[float] = None
    currency: str
    availability_status: Optional[str] = None
    configuration_summary: Optional[str] = None
    scraped_at: str

    class Config:
        from_attributes = True


# A base schema for a single review
class ReviewBase(BaseModel):
    rating: Optional[int] = None
    review_title: Optional[str] = None
    review_text: Optional[str] = None
    reviewer_name: Optional[str] = None

    class Config:
        from_attributes = True


class QuestionsAnswerBase(BaseModel):
    question_text: str
    answer_text: Optional[str] = None
    asker_name: Optional[str] = None
    answerer_name: Optional[str] = None
    question_date: Optional[date] = None
    answer_date: Optional[date] = None
    helpful_count: int = 0
    configuration_summary: Optional[str] = None

    class Config:
        from_attributes = True


# The main schema for a single laptop.
# This will be used when a user requests the full details of one laptop.
class Laptop(BaseModel):
    id: int
    brand: str
    full_model_name: str
    product_page_url: Optional[str] = None
    image_url: Optional[str] = None

    # These will be lists of the other schemas
    specifications: List[SpecificationBase] = []
    price_snapshots: List[PriceSnapshotBase] = []
    reviews: List[ReviewBase] = []
    questions_answers: List[QuestionsAnswerBase] = []

    class Config:
        from_attributes = True


# A simpler schema for the list view of all laptops
class LaptopSimple(BaseModel):
    id: int
    brand: str
    full_model_name: str
    image_url: Optional[str] = None

    # Include the most recent price from our database view
    latest_price: Optional[float] = None
    availability: Optional[str] = None

    class Config:
        from_attributes = True
