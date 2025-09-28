# ai_service/src/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os

from ai_services.src.core.database import get_db, SessionLocal
from ai_services.src.services.langgraph_agent import laptop_agent
from ai_services.src.core.config import settings
from ai_services.src.services.vector_service import vector_service

app = FastAPI(
    title="Laptop Intelligence AI Service",
    description="AI-powered chat and recommendation service for laptops",
    version="1.0.0",
    docs_url="/ai/docs",
    redoc_url="/ai/redoc",
    openapi_url="/ai/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",  # Main API service
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_vector_data():
    """Auto-populate vector database if empty"""
    try:
        stats = vector_service.get_collection_stats()
        if stats["reviews_count"] == 0 and stats["qa_count"] == 0:
            print("Vector database is empty. Initializing from SQL database...")

            db = SessionLocal()
            try:
                # Index reviews
                print("Indexing reviews...")
                vector_service.index_reviews(db)

                # Index Q&A
                print("Indexing Q&A pairs...")
                vector_service.index_qa(db)

                # Check final stats
                final_stats = vector_service.get_collection_stats()
                print("Vector database initialized successfully!")
                print(
                    f"Reviews: {final_stats['reviews_count']}, Q&A: {final_stats['qa_count']}"
                )

            finally:
                db.close()
        else:
            print(
                f"Vector database already populated: {stats['reviews_count']} reviews, {stats['qa_count']} Q&A"
            )

    except Exception as e:
        print(f"Warning: Could not initialize vector database: {e}")
        print("AI service will still work, but may have limited functionality")


@app.on_event("startup")
async def startup_event():
    """Initialize vector database on startup if needed"""
    ensure_vector_data()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    status: str = "success"


# Health check
@app.get("/ai/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Service",
        "version": "1.0.0",
        "openai_configured": bool(settings.OPENAI_API_KEY),
    }


# Chat endpoint
@app.post("/ai/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat endpoint for natural language queries about laptops
    """
    try:
        # Process the query using the LangGraph agent
        response = laptop_agent.process_query(request.message, db)

        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{hash(request.message)}"

        return ChatResponse(
            response=response, conversation_id=conversation_id, status="success"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing chat request: {str(e)}"
        )


# Recommendation endpoint
@app.post("/ai/recommend", response_model=ChatResponse)
async def recommend_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Recommendation endpoint with structured prompting
    """
    try:
        # Enhance the query with recommendation context
        enhanced_query = f"""
        Please provide laptop recommendations based on this request: {request.message}

        Include:
        - Specific laptop models with reasoning
        - Price comparisons where available
        - Key specifications that match the requirements
        - User review insights if relevant
        - Clear pros/cons for each recommendation
        """

        response = laptop_agent.process_query(enhanced_query, db)

        conversation_id = request.conversation_id or f"rec_{hash(request.message)}"

        return ChatResponse(
            response=response, conversation_id=conversation_id, status="success"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating recommendations: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
