import chromadb
from chromadb.config import Settings
from fastembed import TextEmbedding
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.src.utils.logger.logging import logger as logging

from backend.src.app.config.ai_config import AIConfig
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer


class VectorService:
    def __init__(self):
        # Ensure directories exist
        AIConfig.ensure_directories()

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=AIConfig.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False),
        )

        # Initialize FastEmbed
        self.embedding_model = TextEmbedding(model_name=AIConfig.EMBEDDING_MODEL)

        # Get or create collections
        self.reviews_collection = self._get_or_create_collection(
            AIConfig.REVIEWS_COLLECTION
        )
        self.qa_collection = self._get_or_create_collection(AIConfig.QA_COLLECTION)

        logging.info("VectorService initialized successfully")

    def _get_or_create_collection(self, collection_name: str):
        """Get existing collection or create new one"""
        try:
            return self.chroma_client.get_collection(name=collection_name)
        except Exception:
            return self.chroma_client.create_collection(
                name=collection_name, metadata={"hnsw:space": "cosine"}
            )

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using FastEmbed"""
        try:
            embeddings = list(self.embedding_model.embed(texts))
            return [embedding.tolist() for embedding in embeddings]
        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            return []

    def index_reviews(self, db: Session) -> bool:
        """Index all reviews into ChromaDB"""
        try:
            # Get all reviews with laptop information
            reviews = db.query(Review).join(Laptop).all()

            if not reviews:
                logging.warning("No reviews found to index")
                return True

            # Prepare documents and metadata
            documents = []
            metadatas = []
            ids = []

            for review in reviews:
                # Combine title and text for better context
                document = (
                    f"{review.review_title or ''} {review.review_text or ''}".strip()
                )
                if not document:
                    continue

                documents.append(document)
                metadatas.append(
                    {
                        "laptop_id": review.laptop_id,
                        "laptop_name": review.laptop.full_model_name,
                        "rating": review.rating or 0,
                        "reviewer_name": review.reviewer_name or "Anonymous",
                        "configuration": review.configuration_summary or "",
                        "verified": review.reviewer_verified or False,
                        "helpful_count": review.helpful_count or 0,
                    }
                )
                ids.append(f"review_{review.id}")

            if not documents:
                logging.warning("No valid review documents to index")
                return True

            # Generate embeddings
            embeddings = self._generate_embeddings(documents)
            if not embeddings:
                logging.error("Failed to generate embeddings for reviews")
                return False

            # Add to collection
            self.reviews_collection.add(
                embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
            )

            logging.info(f"Successfully indexed {len(documents)} reviews")
            return True

        except Exception as e:
            logging.error(f"Error indexing reviews: {e}")
            return False

    def index_qa(self, db: Session) -> bool:
        """Index all Q&A pairs into ChromaDB"""
        try:
            # Get all Q&A with laptop information
            qa_pairs = db.query(QuestionsAnswer).join(Laptop).all()

            if not qa_pairs:
                logging.warning("No Q&A pairs found to index")
                return True

            # Prepare documents and metadata
            documents = []
            metadatas = []
            ids = []

            for qa in qa_pairs:
                # Combine question and answer
                document = f"Q: {qa.question_text} A: {qa.answer_text or 'No answer yet'}".strip()
                if not document:
                    continue

                documents.append(document)
                metadatas.append(
                    {
                        "laptop_id": qa.laptop_id,
                        "laptop_name": qa.laptop.full_model_name,
                        "question": qa.question_text,
                        "answer": qa.answer_text or "",
                        "asker_name": qa.asker_name or "Anonymous",
                        "answerer_name": qa.answerer_name or "Anonymous",
                        "helpful_count": qa.helpful_count or 0,
                        "configuration": qa.configuration_summary or "",
                    }
                )
                ids.append(f"qa_{qa.id}")

            if not documents:
                logging.warning("No valid Q&A documents to index")
                return True

            # Generate embeddings
            embeddings = self._generate_embeddings(documents)
            if not embeddings:
                logging.error("Failed to generate embeddings for Q&A")
                return False

            # Add to collection
            self.qa_collection.add(
                embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
            )

            logging.info(f"Successfully indexed {len(documents)} Q&A pairs")
            return True

        except Exception as e:
            logging.error(f"Error indexing Q&A: {e}")
            return False

    def search_reviews(
        self, query: str, laptop_id: Optional[int] = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Search reviews using vector similarity"""
        try:
            limit = limit or AIConfig.MAX_SEARCH_RESULTS

            # Generate query embedding
            query_embedding = self._generate_embeddings([query])
            if not query_embedding:
                return []

            # Prepare where clause for filtering
            where_clause = {}
            if laptop_id:
                where_clause["laptop_id"] = laptop_id

            # Search
            results = self.reviews_collection.query(
                query_embeddings=query_embedding,
                n_results=limit,
                where=where_clause if where_clause else None,
            )

            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append(
                    {
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )

            return formatted_results

        except Exception as e:
            logging.error(f"Error searching reviews: {e}")
            return []

    def search_qa(
        self, query: str, laptop_id: Optional[int] = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Search Q&A using vector similarity"""
        try:
            limit = limit or AIConfig.MAX_SEARCH_RESULTS

            # Generate query embedding
            query_embedding = self._generate_embeddings([query])
            if not query_embedding:
                return []

            # Prepare where clause for filtering
            where_clause = {}
            if laptop_id:
                where_clause["laptop_id"] = laptop_id

            # Search
            results = self.qa_collection.query(
                query_embeddings=query_embedding,
                n_results=limit,
                where=where_clause if where_clause else None,
            )

            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append(
                    {
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )

            return formatted_results

        except Exception as e:
            logging.error(f"Error searching Q&A: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about the collections"""
        try:
            return {
                "reviews_count": self.reviews_collection.count(),
                "qa_count": self.qa_collection.count(),
            }
        except Exception as e:
            logging.error(f"Error getting collection stats: {e}")
            return {"reviews_count": 0, "qa_count": 0}


# Global instance
vector_service = VectorService()
