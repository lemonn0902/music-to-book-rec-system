from fastapi import APIRouter, HTTPException
import requests
import os
from pydantic import BaseModel
from typing import Optional, List

lastfm_router = APIRouter()

# Load Last.fm API key from environment variable
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", "514ea2a2dfd55e40eedd9fbbe80a6a74")  # Dev fallback
LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"

# Pydantic model for response
class TrackMetadata(BaseModel):
    name: str
    artist: str
    album: Optional[str] = None
    listeners: Optional[int] = None
    playcount: Optional[int] = None
    tags: Optional[List[str]] = []
    url: Optional[str] = None

# Function to fetch track metadata
def get_track_metadata(artist: str, track: str) -> TrackMetadata:
    params = {
        "method": "track.getInfo",
        "api_key": LASTFM_API_KEY,
        "artist": artist,
        "track": track,
        "format": "json"
    }
    try:
        response = requests.get(LASTFM_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        track_info = data.get("track", {})
        if not track_info:
            raise HTTPException(status_code=404, detail="Track not found")

        return TrackMetadata(
            name=track_info.get("name", "Unknown"),
            artist=track_info.get("artist", {}).get("name", "Unknown"),
            album=track_info.get("album", {}).get("title"),
            listeners=int(track_info.get("listeners", 0)) if track_info.get("listeners") else None,
            playcount=int(track_info.get("playcount", 0)) if track_info.get("playcount") else None,
            tags=[tag["name"] for tag in track_info.get("toptags", {}).get("tag", [])] if "toptags" in track_info else [],
            url=track_info.get("url")
        )
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Error contacting Last.fm API")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

# API Route to fetch metadata
@lastfm_router.get("/track_metadata/", response_model=TrackMetadata)
async def track_metadata(artist: str, track: str):
    return get_track_metadata(artist, track)
