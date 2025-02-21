from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..models import SongMetadata
from ..db import playlists_collection
from .playlist import get_track_metadata
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# Pydantic model for song submission
class Song(BaseModel):
    title: str
    artist: str

@router.post("/")
async def add_songs(songs: List[dict]):
    try:
        added_songs = []
        for song in songs:
            # Fetch metadata from Last.fm
            metadata = get_track_metadata(song["artist"], song["title"])
            
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
            
            # Insert into MongoDB
            result = playlists_collection.insert_one(song_doc)
            song_doc["_id"] = str(result.inserted_id)
            added_songs.append(song_doc)

        return {
            "message": "Songs added successfully!",
            "count": len(added_songs),
            "songs": added_songs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/{song_id}")
async def get_song(song_id: str):
    try:
        song = playlists_collection.find_one({"_id": ObjectId(song_id)})
        if song:
            song["_id"] = str(song["_id"])
            return song
        raise HTTPException(status_code=404, detail="Song not found")
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
