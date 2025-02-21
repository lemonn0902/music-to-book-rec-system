import logging
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from jose import JWTError, jwt
from jose import exceptions as jose_exceptions
import os
from dotenv import load_dotenv
from backend.db import users_collection, playlists_collection



load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SECRET_KEY = os.getenv("SECRET_KEY", "$1230902_1698")  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # Token expiry time

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

from fastapi import HTTPException

def verify_access_token(token: str):
    logger.debug(f"Verifying token: {token[:10]}...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token valid for user: {payload.get('sub')}")
        return payload
    except jose_exceptions.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jose.exceptions.JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication error")