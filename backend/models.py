from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SongMetadata(BaseModel):
    name: str
    artist: str
    album: Optional[str] = None
    listeners: Optional[int] = None
    playcount: Optional[int] = None
    tags: Optional[List[str]] = []
    url: Optional[str] = None
    created_at: datetime = datetime.now()

class SongIds(BaseModel):
    song_ids: Optional[List[str]] = None

class BookRecommendation(BaseModel):
    title: str
    author: str
    description: str
    rating: float
    url: str
    genres: List[str]
    similarity_score: float
    matching_tags: List[str]
    related_tag: str
