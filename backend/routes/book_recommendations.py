from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import pandas as pd
from ..db import playlists_collection
from bson import ObjectId

# Create router
book_recommendations_router = APIRouter()

# Load model - this should be done once when the application starts
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample music genres - you could load these from a file or database
music_genres_df = pd.DataFrame({
    "music_genre": [
        "rock", "pop", "hip hop", "rap", "electronic", "classical", "jazz", 
        "indie", "folk", "metal", "punk", "r&b", "soul", "blues", "country",
        "alternative", "ambient", "dance", "disco", "funk", "reggae"
    ]
})

# Sample book genres - you could load these from a file or database
book_genres_df = pd.DataFrame({
    "book_genre": [
        "thriller", "mystery", "romance", "science fiction", "fantasy", 
        "historical fiction", "biography", "self-help", "horror", "adventure",
        "literary fiction", "young adult", "dystopian", "memoir", "poetry",
        "philosophy", "psychology", "crime", "drama", "comedy", "classic"
    ]
})

# Pydantic models for responses
class BookRecommendation(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = []
    google_books_id: Optional[str] = None

class BookRecommendationsResponse(BaseModel):
    music_genre: str
    mapped_book_genre: str
    recommendations: List[BookRecommendation]

# Create genre mapping
def create_genre_mapping():
    # Extract music and book genres
    music_genres = music_genres_df["music_genre"].tolist()
    book_genres = book_genres_df["book_genre"].tolist()
    
    # Encode music and book genres into embeddings
    music_embeddings = model.encode(music_genres)
    book_embeddings = model.encode(book_genres)
    
    # Calculate similarity matrix
    similarity_matrix = util.cos_sim(music_embeddings, book_embeddings)
    
    # Map music genres to book genres based on highest similarity
    mapping = {}
    for i, music_genre in enumerate(music_genres):
        max_sim_index = similarity_matrix[i].argmax()
        mapping[music_genre] = book_genres[max_sim_index]
    
    return mapping

# Initialize genre mapping
GENRE_MAPPING = create_genre_mapping()

# Function to get book recommendations from Google Books API
def get_book_recommendations(genre: str, max_results: int = 5):
    google_books_api_url = "https://www.googleapis.com/books/v1/volumes"
    
    params = {
        "q": f"subject:{genre}",
        "maxResults": max_results,
        "orderBy": "relevance"
    }
    
    try:
        response = requests.get(google_books_api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        books = []
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            
            # Extract book details
            book = BookRecommendation(
                title=volume_info.get("title", "Unknown Title"),
                author=volume_info.get("authors", ["Unknown Author"])[0] if volume_info.get("authors") else "Unknown Author",
                description=volume_info.get("description", "No description available"),
                cover_url=volume_info.get("imageLinks", {}).get("thumbnail") if "imageLinks" in volume_info else None,
                rating=volume_info.get("averageRating"),
                genres=volume_info.get("categories", []),
                google_books_id=item.get("id")
            )
            books.append(book)
        
        return books
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Google Books API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")

# Find the best matching genre from our mapping
def find_best_matching_genre(song_tags):
    if not song_tags:
        return "fiction"  # Default fallback genre
    
    # Convert tags to lowercase for better matching
    lowercase_tags = [tag.lower() for tag in song_tags]
    
    # Try direct match first
    for tag in lowercase_tags:
        if tag in GENRE_MAPPING:
            return GENRE_MAPPING[tag]
    
    # If no direct match, use embedding similarity
    tag_embeddings = model.encode(lowercase_tags)
    music_genres = list(GENRE_MAPPING.keys())
    music_genre_embeddings = model.encode(music_genres)
    
    # Find the most similar music genre for each tag
    max_similarity = -1
    best_music_genre = None
    
    for i, tag_embedding in enumerate(tag_embeddings):
        similarities = util.cos_sim(tag_embedding.reshape(1, -1), music_genre_embeddings)[0]
        max_index = similarities.argmax()
        
        if similarities[max_index] > max_similarity:
            max_similarity = similarities[max_index]
            best_music_genre = music_genres[max_index]
    
    # Return the corresponding book genre
    if best_music_genre:
        return GENRE_MAPPING[best_music_genre]
    else:
        return "fiction"  # Default fallback

# API Route to get book recommendations for a specific song
@book_recommendations_router.get("/recommendations/{song_id}", response_model=BookRecommendationsResponse)
async def get_recommendations_for_song(song_id: str, max_results: int = 5):
    try:
        # Retrieve song from MongoDB
        song = playlists_collection.find_one({"_id": ObjectId(song_id)})
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Get song tags/genres
        song_tags = song.get("tags", [])
        
        # Find the best matching book genre
        book_genre = find_best_matching_genre(song_tags)
        
        # Get the music genre that mapped to this book genre
        music_genre = next((m_genre for m_genre, b_genre in GENRE_MAPPING.items() 
                           if b_genre == book_genre and m_genre in song_tags), "Unknown")
        
        # If we couldn't find the original music genre in the song tags, just pick the first tag
        if music_genre == "Unknown" and song_tags:
            music_genre = song_tags[0]
        
        # Get book recommendations
        books = get_book_recommendations(book_genre, max_results)
        
        return BookRecommendationsResponse(
            music_genre=music_genre,
            mapped_book_genre=book_genre,
            recommendations=books
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))