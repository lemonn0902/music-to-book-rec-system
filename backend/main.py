from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.routes.auth import router as auth_router
from backend.routes.playlist import lastfm_router
from backend.routes.songs import router as songs_router
from backend.routes.book_recommendations import book_recommendations_router
import os
import uvicorn
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi
import logging 
from backend.db import get_database, client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

MONGO_URL = os.getenv("MONGO_URL")  
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where(), tls=True, tlsAllowInvalidCertificates=True)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set up templates directory
templates = Jinja2Templates(directory=Path("frontend/templates"))

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Home route to serve the home.html template
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home")
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/playlist-import")
def playlist_import_page(request: Request):
    return templates.TemplateResponse("playlist_import.html", {"request": request})

@app.get("/recommendations")
def recommendations_page(request: Request):
    return templates.TemplateResponse("recommendations.html", {"request": request})

@app.get("/book-recommendations")
def book_recommendations_page(request: Request):
    return templates.TemplateResponse("book_recommendations.html", {"request": request})

@app.get("/test-db")
async def test_db():
    try:
        # Test the connection
        client.admin.command('ping')
        return {"status": "Connected to MongoDB", "message": "Database connection is healthy"}
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.on_event("startup")
async def startup_db_client():
    try:
        client.admin.command('ping')
        logger.info("Connected to MongoDB at startup")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB at startup: {e}")
        raise

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        client.close()
        logger.info("Closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")



# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(lastfm_router, prefix="/lastfm", tags=["LastFM"])
app.include_router(songs_router, prefix="/songs", tags=["Songs"])
app.include_router(book_recommendations_router, prefix="/api/books", tags=["Book Recommendations"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)


