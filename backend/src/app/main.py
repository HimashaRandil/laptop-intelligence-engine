# backend/src/app/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
import time
from backend.src.app.core.db import SessionLocal, Base, engine
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.app.models.views import LaptopReviewSummary, LaptopLatestPrice
from backend.src.utils.logger.logging import logger as logging
from backend.src.app.schemas.laptop import (
    Laptop as LaptopSchema,
    LaptopSimple,
    SpecificationBase,
    PriceSnapshotBase,
    ReviewBase,
    QuestionsAnswerBase,
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Laptop Intelligence Engine API",
    description="Compare laptop specifications, prices, and reviews",
    version="1.0.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",  # Add this temporarily for testing
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Laptop Intelligence Engine API",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


# Health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to test database connection
        laptop_count = db.query(Laptop).count()
        return {
            "status": "healthy",
            "database": "connected",
            "laptop_count": laptop_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Get all laptops (simple view)
@app.get("/laptops", response_model=List[LaptopSimple])
def get_laptops(
    brand: Optional[str] = Query(None, description="Filter by brand (Lenovo, HP)"),
    db: Session = Depends(get_db),
):
    """Get list of all laptops with basic info and latest pricing/rating."""

    # This single, efficient query joins the main table with our two views
    query = (
        db.query(Laptop, LaptopLatestPrice, LaptopReviewSummary)
        .outerjoin(LaptopLatestPrice, Laptop.id == LaptopLatestPrice.laptop_id)
        .outerjoin(LaptopReviewSummary, Laptop.id == LaptopReviewSummary.laptop_id)
    )

    if brand:
        query = query.filter(Laptop.brand.ilike(f"%{brand}%"))

    results = query.all()

    # Combine the results into our Pydantic schema
    laptops_with_details = []
    for laptop, price_info, review_info in results:
        laptop_data = laptop.__dict__
        laptop_data["latest_price"] = price_info.price if price_info else None
        laptop_data["availability"] = (
            price_info.availability_status if price_info else None
        )
        laptop_data["average_rating"] = (
            review_info.average_rating if review_info else None
        )
        laptop_data["review_count"] = review_info.total_reviews if review_info else None
        laptops_with_details.append(LaptopSimple(**laptop_data))

    return laptops_with_details


# Get detailed laptop information
@app.get("/laptops/{laptop_id}", response_model=LaptopSchema)
def get_laptop(laptop_id: int, db: Session = Depends(get_db)):
    """Get complete laptop details including specifications, pricing history, and reviews."""
    laptop = (
        db.query(Laptop)
        .options(
            selectinload(Laptop.specifications),
            selectinload(Laptop.price_snapshots),
            selectinload(Laptop.reviews),
        )
        .filter(Laptop.id == laptop_id)
        .first()
    )

    if not laptop:
        logging.warning(f"Laptop not found for ID {laptop_id}")
        raise HTTPException(status_code=404, detail="Laptop not found")

    return laptop


# Get only specifications for a laptop
@app.get("/laptops/{laptop_id}/specifications", response_model=List[SpecificationBase])
def get_laptop_specifications(
    laptop_id: int,
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """Get specifications for a specific laptop, optionally filtered by category."""
    # Verify laptop exists
    laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if not laptop:
        logging.warning(f"Laptop not found for ID {laptop_id}")
        raise HTTPException(status_code=404, detail="Laptop not found")

    query = db.query(Specification).filter(Specification.laptop_id == laptop_id)

    if category:
        query = query.filter(Specification.category.ilike(f"%{category}%"))

    specifications = query.all()
    return specifications


# Get pricing history for a laptop
@app.get("/laptops/{laptop_id}/prices", response_model=List[PriceSnapshotBase])
def get_laptop_prices(
    laptop_id: int,
    limit: int = Query(10, description="Number of price snapshots to return"),
    db: Session = Depends(get_db),
):
    """Get pricing history for a specific laptop."""
    # Verify laptop exists
    laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if not laptop:
        logging.warning(f"Laptop not found for ID {laptop_id}")
        raise HTTPException(status_code=404, detail="Laptop not found")

    price_snapshots = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.laptop_id == laptop_id)
        .order_by(PriceSnapshot.scraped_at.desc())
        .limit(limit)
        .all()
    )

    return price_snapshots


# Get reviews for a laptop
@app.get("/laptops/{laptop_id}/reviews", response_model=List[ReviewBase])
def get_laptop_reviews(
    laptop_id: int,
    min_rating: Optional[int] = Query(
        None, ge=1, le=5, description="Minimum rating filter"
    ),
    limit: int = Query(10, description="Number of reviews to return"),
    db: Session = Depends(get_db),
):
    """Get reviews for a specific laptop."""
    # Verify laptop exists
    laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if not laptop:
        logging.warning(f"Laptop not found for ID {laptop_id}")
        raise HTTPException(status_code=404, detail="Laptop not found")

    query = db.query(Review).filter(Review.laptop_id == laptop_id)

    if min_rating:
        query = query.filter(Review.rating >= min_rating)

    reviews = query.order_by(Review.scraped_at.desc()).limit(limit).all()
    return reviews


# Compare multiple laptops
@app.get("/laptops/compare", response_model=List[LaptopSchema])
def compare_laptops(
    ids: str = Query(..., description="Comma-separated laptop IDs to compare"),
    db: Session = Depends(get_db),
):
    """Compare multiple laptops side by side."""
    try:
        laptop_ids = [int(id.strip()) for id in ids.split(",")]
    except ValueError:
        logging.error(f"Invalid laptop IDs format: {ids}")
        raise HTTPException(status_code=400, detail="Invalid laptop IDs format")

    if len(laptop_ids) > 5:
        logging.warning("Attempted to compare more than 5 laptops at once")
        raise HTTPException(
            status_code=400, detail="Cannot compare more than 5 laptops at once"
        )

    laptops = (
        db.query(Laptop)
        .options(
            selectinload(Laptop.specifications),
            selectinload(Laptop.price_snapshots),
            selectinload(Laptop.reviews),
        )
        .filter(Laptop.id.in_(laptop_ids))
        .all()
    )

    if len(laptops) != len(laptop_ids):
        logging.warning(f"Some laptops not found for comparison: {laptop_ids}")
        found_ids = [laptop.id for laptop in laptops]
        missing_ids = [id for id in laptop_ids if id not in found_ids]
        raise HTTPException(status_code=404, detail=f"Laptops not found: {missing_ids}")

    return laptops


# Search specifications across laptops
@app.get("/specifications/search")
def search_specifications(
    query: str = Query(..., description="Search term for specifications"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """Search for specifications across all laptops."""
    spec_query = db.query(Specification).join(Laptop)

    # Add text search
    spec_query = spec_query.filter(
        Specification.specification_value.ilike(f"%{query}%")
    )
    if category:
        spec_query = spec_query.filter(Specification.category.ilike(f"%{category}%"))

    results = spec_query.limit(50).all()
    # Group by laptop for better organization
    grouped_results = {}
    for spec in results:
        laptop_name = spec.laptop.full_model_name
        if laptop_name not in grouped_results:
            grouped_results[laptop_name] = {
                "laptop_id": spec.laptop_id,
                "laptop_name": laptop_name,
                "specifications": [],
            }
        grouped_results[laptop_name]["specifications"].append(
            {
                "category": spec.category,
                "name": spec.specification_name,
                "value": spec.specification_value,
                "structured_value": spec.structured_value,
            }
        )
    return {"results": list(grouped_results.values())}


# Get Q&A for a laptop
@app.get("/laptops/{laptop_id}/questions", response_model=List[QuestionsAnswerBase])
def get_laptop_questions(
    laptop_id: int,
    limit: int = Query(10, description="Number of Q&A pairs to return"),
    db: Session = Depends(get_db),
):
    """Get questions and answers for a specific laptop."""
    # Verify laptop exists
    laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if not laptop:
        logging.warning(f"Laptop not found for ID {laptop_id}")
        raise HTTPException(status_code=404, detail="Laptop not found")

    questions = (
        db.query(QuestionsAnswer)
        .filter(QuestionsAnswer.laptop_id == laptop_id)
        .order_by(
            QuestionsAnswer.helpful_count.desc(), QuestionsAnswer.question_date.desc()
        )
        .limit(limit)
        .all()
    )
    return questions


# Search across all Q&A
@app.get("/questions/search")
def search_questions(
    query: str = Query(..., description="Search term in questions/answers"),
    db: Session = Depends(get_db),
):
    """Search questions and answers across all laptops."""
    results = (
        db.query(QuestionsAnswer)
        .join(Laptop)
        .filter(
            (QuestionsAnswer.question_text.ilike(f"%{query}%"))
            | (QuestionsAnswer.answer_text.ilike(f"%{query}%"))
        )
        .order_by(QuestionsAnswer.helpful_count.desc())
        .limit(20)
        .all()
    )
    # Group by laptop similar to your spec search
    grouped_results = {}
    for qa in results:
        laptop_name = qa.laptop.full_model_name
        if laptop_name not in grouped_results:
            grouped_results[laptop_name] = {
                "laptop_id": qa.laptop_id,
                "laptop_name": laptop_name,
                "questions": [],
            }
        grouped_results[laptop_name]["questions"].append(
            {
                "question": qa.question_text,
                "answer": qa.answer_text,
                "asker": qa.asker_name,
                "answerer": qa.answerer_name,
                "helpful_count": qa.helpful_count,
                "configuration": qa.configuration_summary,
            }
        )
    return {"results": list(grouped_results.values())}


# Get available categories
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all available specification categories."""
    categories = (
        db.query(Specification.category)
        .distinct()
        .order_by(Specification.category)
        .all()
    )
    return {"categories": [cat[0] for cat in categories]}


# Get available brands
@app.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    """Get all available laptop brands."""
    brands = db.query(Laptop.brand).distinct().order_by(Laptop.brand).all()
    return {"brands": [brand[0] for brand in brands]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
