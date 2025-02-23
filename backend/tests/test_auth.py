import pytest
from httpx import AsyncClient
from app.models import User, VerificationToken
from app.auth_local import get_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test registration with new user
@pytest.mark.asyncio
async def test_register_new_user(client, mock_smtp, override_get_db):
    logger.debug("Starting test_register_new_user")
    response = client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    logger.debug(f"Response received: {response.status_code} - {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json() == {"message": "Verification email sent. Please check your inbox."}

    db = next(override_get_db())
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.username == "testuser"
    assert user.is_verified is False
    token = db.query(VerificationToken).filter(VerificationToken.email == "test@example.com").first()
    assert token is not None
    logger.debug("Finished test_register_new_user")

# Test registration with existing email
@pytest.mark.asyncio
async def test_register_existing_email(client, mock_smtp, override_get_db):
    logger.debug("Starting test_register_existing_email")
    client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/register",
        json={"username": "testuser2", "email": "test@example.com", "password": "password456"}
    )
    logger.debug(f"Response received: {response.status_code} - {response.text}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}
    logger.debug("Finished test_register_existing_email")

# Test email verification
@pytest.mark.asyncio
async def test_verify_email(client, mock_smtp, override_get_db):
    logger.debug("Starting test_verify_email")
    client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    db = next(override_get_db())
    token = db.query(VerificationToken).filter(VerificationToken.email == "test@example.com").first().token

    response = client.get(f"/verify?token={token}")
    logger.debug(f"Response received: {response.status_code} - {response.text}")
    assert response.status_code == 200
    assert response.json() == {"message": "Email verified successfully. You can now log in."}

    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user.is_verified is True
    token_after = db.query(VerificationToken).filter(VerificationToken.email == "test@example.com").first()
    assert token_after is None
    logger.debug("Finished test_verify_email")

# Test login with unverified user
@pytest.mark.asyncio
async def test_login_unverified_user(client, mock_smtp, override_get_db):
    logger.debug("Starting test_login_unverified_user")
    client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/local",
        json={"email": "test@example.com", "password": "password123"}
    )
    logger.debug(f"Response received: {response.status_code} - {response.text}")
    assert response.status_code == 403
    assert response.json() == {"detail": "Please verify your email before logging in"}
    logger.debug("Finished test_login_unverified_user")

# Test login with verified user
@pytest.mark.asyncio
async def test_login_verified_user(client, mock_smtp, override_get_db):
    logger.debug("Starting test_login_verified_user")
    client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    db = next(override_get_db())
    token = db.query(VerificationToken).filter(VerificationToken.email == "test@example.com").first().token
    client.get(f"/verify?token={token}")

    response = client.post(
        "/auth/local",
        json={"email": "test@example.com", "password": "password123"}
    )
    logger.debug(f"Response received: {response.status_code} - {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["email"] == "test@example.com"
    assert "picture" in data
    logger.debug("Finished test_login_verified_user")

# Test login with wrong password
@pytest.mark.asyncio
async def test_login_wrong_password(client, mock_smtp, override_get_db):
    logger.debug("Starting test_login_wrong_password")
    client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    db = next(override_get_db())
    token = db.query(VerificationToken).filter(VerificationToken.email == "test@example.com").first().token
    client.get(f"/verify?token={token}")

    response = client.post(
        "/auth/local",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    logger.debug(f"Response received: {response.status_code} - {response.text}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}
    logger.debug("Finished test_login_wrong_password")

# Test Google login redirect (mocked)
@pytest.mark.asyncio
async def test_google_login_redirect(client, mock_smtp, monkeypatch):
    logger.debug("Starting test_google_login_redirect")
    def mock_authorization_url(*args, **kwargs):
        return ("https://accounts.google.com/o/oauth2/auth?client_id=test-client-id&...", "test-state")
    
    monkeypatch.setattr("app.auth.flow.authorization_url", mock_authorization_url)
    
    response = client.get("/auth/google/login", follow_redirects=False)  # Prevent following redirect
    logger.debug(f"Response received: {response.status_code} - {response.headers}")
    assert response.status_code == 307, f"Expected 307, got {response.status_code}: {response.text}"
    assert "https://accounts.google.com/o/oauth2/auth" in response.headers["location"]
    logger.debug("Finished test_google_login_redirect")

# Test health endpoint
@pytest.mark.asyncio
async def test_health_check(client):
    logger.debug("Starting test_health_check")
    response = client.get("/health")
    logger.debug(f"Response received: {response.status_code} - {response.text}")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    logger.debug("Finished test_health_check")