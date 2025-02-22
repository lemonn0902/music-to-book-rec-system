from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()  # Load environment variables from .env file

MONGO_URL = os.getenv("MONGO_URL")  
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where(),  tls=True, tlsAllowInvalidCertificates=True)

db = client["music_book_db"]  # Database Name
users_collection = db["users"]  # Users Collection
playlists_collection = db["playlists"] 
