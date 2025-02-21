import logging
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import Request, Depends
from backend.db import  playlists_collection


from fastapi.security import OAuth2PasswordBearer
from backend.models import UserCreate, UserLogin
from backend.db import users_collection
from backend.utils import hash_password, verify_password
from backend.auth import create_access_token
from datetime import timedelta
from backend.auth import verify_access_token


# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
def register_user(user: UserCreate):
    logger.debug(f"Registering user: {user}")  # Debugging
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    })
    logger.debug("User registered successfully")  # Debugging
    return {"message": "User registered successfully"}

@router.post("/login")
def login_user(request: Request, user: UserLogin):
    existing_user = users_collection.find_one({"email": user.email})
    print(f"Received login data: {user.email}, {user.password}")

    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Debugging: Check the stored password hash
    print(f"Stored hashed password: {existing_user['password']}")

    is_valid_password = verify_password(user.password, existing_user["password"])
    print(f"Password valid: {is_valid_password}")  # Debugging
    if not is_valid_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate access token
    access_token = create_access_token({"sub": user.email}, timedelta(hours=12))

    # Extract 'next' from query parameters (defaults to homepage if not provided)
    next_page = request.query_params.get("next", "/")

    # Set token in a cookie and redirect to the intended page
    response = RedirectResponse(url=next_page, status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
            )
        return payload
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
        )

@router.get("/protected")
def read_protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['sub']}, you have access to this protected route!"}



