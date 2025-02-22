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

load_dotenv()  # Load environment variables from .env file

MONGO_URL = os.getenv("MONGO_URL")  
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())

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
        client.server_info()  # Checks if MongoDB is connected
        return {"status": "Connected to MongoDB"}
    except Exception as e:
        return {"error": str(e)}


# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(lastfm_router, prefix="/lastfm", tags=["LastFM"])
app.include_router(songs_router, prefix="/songs", tags=["Songs"])
app.include_router(book_recommendations_router, prefix="/api/books", tags=["Book Recommendations"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)


