from fastapi import Depends, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
import os
from sqlalchemy.orm import Session
from .models import User
from .database import get_db
from pydantic import BaseModel
from .vars import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, SCOPES

class TokenRequest(BaseModel):
    token: str


flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [GOOGLE_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=SCOPES,
    redirect_uri=GOOGLE_REDIRECT_URI  # Explicitly set redirect_uri here
)

async def verify_google_token(token_request: TokenRequest, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(
            token_request.token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        user = db.query(User).filter(User.email == idinfo['email']).first()
        if not user:
            user = User(
                username=idinfo['name'],
                picture=idinfo['picture'],
                email=idinfo['email'],
                is_verified=True
            )
        else:
            user.username = idinfo['name']
            user.picture = idinfo['picture']
        db.add(user)
        db.commit()
        db.refresh(user)
        return {
            "username": user.username,
            "picture": user.picture,
            "email": user.email
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")