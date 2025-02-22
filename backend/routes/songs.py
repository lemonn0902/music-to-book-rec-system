from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List
from ..models import SongMetadata
from fastapi.templating import Jinja2Templates
from bson.errors import InvalidId
import os
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..db import playlists_collection
from .playlist import get_track_metadata
from bson import ObjectId
from datetime import datetime
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory=os.path.abspath("frontend/templates"))

print("Template directory:", templates.env.loader.searchpath)

template_dir = os.path.abspath("frontend/templates")
print("Current working directory:", os.getcwd())
print("Template directory:", template_dir)
print("Template directory exists:", os.path.exists(template_dir))

router = APIRouter()

# Pydantic model for song submission
class Song(BaseModel):
    title: str
    artist: str

class SongInput(BaseModel):
    title: str
    artist: str

class SongResponse(BaseModel):
    message: str
    count: int
    songs: List[dict]


@router.post("/")
async def add_songs(songs: List[dict]):
    try:
        # Validate input
        if not songs:
            raise HTTPException(status_code=400, detail="No songs provided")
            
        logger.info(f"Received request to add {len(songs)} songs")
        added_songs = []
        
        for song in songs:
            try:
                # Validate song structure
                if not isinstance(song, dict) or 'title' not in song or 'artist' not in song:
                    raise HTTPException(
                        status_code=400, 
                        detail="Invalid song format. Each song must have 'title' and 'artist'"
                    )
                
                logger.info(f"Fetching metadata for: {song['title']} by {song['artist']}")
                
                # Fetch metadata from Last.fm with error handling
                try:
                    metadata = get_track_metadata(song["artist"], song["title"])
                except Exception as e:
                    logger.error(f"Last.fm API error for {song['title']}: {str(e)}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Error fetching Last.fm data: {str(e)}"
                    )
                
                # Prepare song document
                song_doc = {
                    "name": metadata.name,
                    "artist": metadata.artist,
                    "album": metadata.album,
                    "listeners": metadata.listeners,
                    "playcount": metadata.playcount,
                    "tags": metadata.tags,
                    "url": metadata.url,
                    "created_at": datetime.now()
                }
                
                # Insert into MongoDB with error handling
                try:
                    result = playlists_collection.insert_one(song_doc)
                    song_doc["_id"] = str(result.inserted_id)
                    added_songs.append(song_doc)
                    logger.info(f"Successfully added song: {song['title']}")
                except Exception as e:
                    logger.error(f"MongoDB error: {str(e)}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Database error: {str(e)}"
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing song {song.get('title', 'unknown')}: {str(e)}")
                continue
        
        if not added_songs:
            raise HTTPException(
                status_code=500, 
                detail="Failed to add any songs"
            )
            
        return {
            "message": "Song(s) added successfully!",
            "count": len(added_songs),
            "songs": added_songs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_songs: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/")
async def get_all_songs():
    try:
        songs = list(playlists_collection.find())
        # Convert ObjectId to string for JSON serialization
        for song in songs:
            song["_id"] = str(song["_id"])
        return {"songs": songs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/view/{song_id}", response_class=HTMLResponse)
async def view_song_recommendations(request: Request, song_id: str):
    """Render the book recommendations page for a specific song"""
    print("Rendering template: book_recommendations.html")  # Debug log
    print("Song ID:", song_id) 
    return templates.TemplateResponse("book_recommendations.html", {"request": request, "song_id": song_id})


@router.get("/{song_id}")
async def get_song(song_id: str):
    try:
        # Validate song_id
        if not ObjectId.is_valid(song_id):
            raise HTTPException(status_code=400, detail="Invalid song ID")
        
        song = playlists_collection.find_one({"_id": ObjectId(song_id)})
        if song:
            song["_id"] = str(song["_id"])
            return song
        raise HTTPException(status_code=404, detail="Song not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid song ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{song_id}")
async def delete_song(song_id: str):
    try:
        result = playlists_collection.delete_one({"_id": ObjectId(song_id)})
        if result.deleted_count:
            return {"message": "Song deleted successfully"}
        raise HTTPException(status_code=404, detail="Song not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{song_id}")
async def update_song(song_id: str, song: dict):
    try:
        result = playlists_collection.update_one(
            {"_id": ObjectId(song_id)},
            {"$set": {**song, "updated_at": datetime.now()}}
        )
        if result.modified_count:
            return {"message": "Song updated successfully"}
        raise HTTPException(status_code=404, detail="Song not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


