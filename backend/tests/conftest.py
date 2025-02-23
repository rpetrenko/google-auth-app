import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
import os
from dotenv import load_dotenv
from unittest.mock import MagicMock
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables for testing
load_dotenv()

# Use the test database on db_test service
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine and session for testing
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define override_get_db as a fixture returning a callable
@pytest.fixture(scope="function")
def override_get_db():
    def _get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    return _get_db

# Create a test client with overridden DB
@pytest.fixture(scope="function")
def client(override_get_db):
    logger.debug("Creating tables for test")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    logger.debug("Cleaning up after test")
    app.dependency_overrides.clear()
    logger.debug("Close client")
    client.close()
    logger.debug("Close DB connections before drop")
    engine.dispose()  # Close all connections before dropping tables

    logger.debug("Checking active connections")
    import psycopg2
    conn = psycopg2.connect(TEST_DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE datname='google_auth_db_test';")
    active_connections = cursor.fetchone()[0]
    logger.debug(f"Active connections: {active_connections}")
    conn.close()

    if active_connections > 0:
        logger.debug("Terminating all connections to google_auth_db_test")
        conn = psycopg2.connect("postgresql://postgres:postgres@db_test:5432/postgres")
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'google_auth_db_test' AND pid <> pg_backend_pid();")
        conn.close()
        
    logger.debug("Drop all tables")
    Base.metadata.drop_all(bind=engine)
    logger.debug("Get event loop")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        logger.debug("Get pending tasks")
        pending = asyncio.all_tasks(loop)
        for task in pending:
            logger.debug(f"Canceling task: {task}")
            task.cancel()
        logger.debug("Running pending tasks to completion")
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        logger.debug("Stopping event loop")
        loop.stop()
    logger.debug("Close event loop")
    loop.close()
    logger.debug("Test client cleanup complete")

# Override environment variables for testing
@pytest.fixture(autouse=True)
def set_env():
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["GOOGLE_CLIENT_ID"] = "test-client-id"
    os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
    os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/auth/google/callback"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["EMAIL_HOST"] = "smtp.gmail.com"
    os.environ["EMAIL_PORT"] = "587"
    os.environ["EMAIL_USER"] = "test@example.com"
    os.environ["EMAIL_PASSWORD"] = "test-password"
    os.environ["REACT_APP_URL"] = "http://localhost:3000"

# Mock smtplib.SMTP for email sending
@pytest.fixture(scope="function")
def mock_smtp(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs):
            pass
        def starttls(self):
            pass
        def login(self, *args, **kwargs):
            pass
        def send_message(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr("smtplib.SMTP", MockSMTP)
    return MockSMTP

# Force pytest to exit after all tests
def pytest_sessionfinish(session, exitstatus):
    logger.debug("Pytest session finished, forcing exit")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.stop()
    loop.close()
    os._exit(exitstatus)