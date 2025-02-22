from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .auth import verify_google_token, flow, TokenRequest
from .auth_local import authenticate_local_user, get_password_hash, generate_verification_token, send_verification_email
from sqlalchemy.orm import Session
from .models import User, VerificationToken
from .database import get_db, Base, engine
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
import os
import logging
import smtplib
from email.mime.text import MIMEText
from .vars import FRONTEND_URL, EMAIL_HOST, EMAIL_PASSWORD, EMAIL_PORT, EMAIL_USER


logger = logging.getLogger(__name__)

app = FastAPI()

origins = [ FRONTEND_URL ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

def send_google_verification_notice(email: str):
    msg = MIMEText("Your account has been verified using your Google login. You can ignore any previous email verification links sent.")
    msg['Subject'] = 'Account Verified via Google'
    msg['From'] = EMAIL_USER
    msg['To'] = email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logger.error(f"Failed to send Google verification notice: {str(e)}")

@app.get("/auth/google/login")
async def google_login():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        # redirect_uri=GOOGLE_REDIRECT_URI  # Explicitly pass redirect_uri
    )
    return RedirectResponse(authorization_url)

@app.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    flow.fetch_token(code=code)
    credentials = flow.credentials
    idinfo = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        os.getenv("GOOGLE_CLIENT_ID")
    )
    
    user = db.query(User).filter(User.email == idinfo['email']).first()
    if not user:
        user = User(
            username=idinfo['name'],
            picture=idinfo['picture'],
            email=idinfo['email'],
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # User exists (e.g., signed up with email/password)
        if not user.is_verified:
            user.is_verified = True
            # Delete any existing verification token
            verification = db.query(VerificationToken).filter(VerificationToken.email == user.email).first()
            if verification:
                db.delete(verification)
            db.commit()
            send_google_verification_notice(user.email)
    
    frontend_url = f"{FRONTEND_URL}?token={credentials.id_token}"
    return RedirectResponse(frontend_url)

@app.post("/auth/google")
async def google_auth(token_request: TokenRequest, db: Session = Depends(get_db)):
    user_data = await verify_google_token(token_request, db)
    return user_data

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/local")
async def local_login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user_data = await authenticate_local_user(login_request.email, login_request.password, db)
    return user_data

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register")
async def register_user(register_request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == register_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(register_request.password)
    user = User(
        username=register_request.username,
        email=register_request.email,
        hashed_password=hashed_password,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = generate_verification_token(register_request.email)
    verification = VerificationToken(token=token, email=register_request.email, user_id=user.id)
    db.add(verification)
    db.commit()
    
    send_verification_email(register_request.email, token)
    return {"message": "Verification email sent. Please check your inbox."}

@app.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    verification = db.query(VerificationToken).filter(VerificationToken.token == token).first()
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    user = db.query(User).filter(User.id == verification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    db.delete(verification)
    db.commit()
    
    return {"message": "Email verified successfully. You can now log in."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}