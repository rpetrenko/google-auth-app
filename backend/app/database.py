from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
import time
from sqlalchemy.exc import OperationalError
from .base import Base
from .vars import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info(f"Connecting to db: {DATABASE_URL}")

def connect_with_retry(max_attempts=5, delay=5):
    attempt = 1
    while attempt <= max_attempts:
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()  # Test the connection
            logger.info("Database engine created successfully")
            return engine
        except OperationalError as e:
            logger.error(f"Connection attempt {attempt} failed: {e}")
            if attempt == max_attempts:
                raise
            time.sleep(delay)
            attempt += 1

engine = connect_with_retry()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from .models import User

# Create all tables on import
logger.info("Registering models and creating tables")
Base.metadata.create_all(bind=engine)
logger.info("Tables created successfully")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()