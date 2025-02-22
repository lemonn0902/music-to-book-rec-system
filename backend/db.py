from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi
from pymongo.errors import ConnectionFailure
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_database():
    try:
        MONGO_URL = os.getenv("MONGO_URL")
        if not MONGO_URL:
            raise ValueError("MONGO_URL environment variable is not set")

        client = MongoClient(
            MONGO_URL,
            tlsCAFile=certifi.where(),
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,  # Increase timeout to 30 seconds
            connectTimeoutMS=30000,
            socketTimeoutMS=45000,
            retryWrites=True
        )
        
        # Test the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        db = client["music_book_db"]
        return db, client
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

# Initialize database connection
try:
    db, client = get_database()
    users_collection = db["users"]
    playlists_collection = db["playlists"]
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise