import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from backend.src.utils.logger.logging import logger as logging

# Load .env file from the root directory
logging.info("Loading environment variables from .env file")
load_dotenv()

logging.info("Setting up database connection")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logging.error("DATABASE_URL environment variable not set")
    raise ValueError("DATABASE_URL environment variable not set")

logging.info(f"Using database URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

logging.info("Creating database session")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logging.info("Defining base class for models")
Base = declarative_base()
