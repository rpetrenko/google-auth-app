from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .models import User, VerificationToken
from .database import get_db
from passlib.context import CryptContext
import os
from jose import jwt
import smtplib
from email.mime.text import MIMEText
from .vars import FRONTEND_URL, SECRET_KEY, EMAIL_HOST, EMAIL_PASSWORD, EMAIL_PORT, EMAIL_USER


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_local_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")
    return {
        "username": user.username,
        "picture": user.picture,
        "email": user.email
    }

def generate_verification_token(email: str) -> str:
    return jwt.encode({"email": email}, SECRET_KEY, algorithm="HS256")


def send_verification_email(email: str, token: str):
    frontend_url = FRONTEND_URL
    verify_link = f"{frontend_url}/verify?token={token}"
    msg = MIMEText(f"Click this link to verify your email: {verify_link}")
    msg['Subject'] = 'Verify Your Email'
    msg['From'] = EMAIL_USER
    msg['To'] = email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")