from pymongo import MongoClient
import certifi
MONGO_URI = "mongodb+srv://shreya:shreya190891@cluster48366.8mwfu.mongodb.net/music_book_db?retryWrites=true&w=majority&appName=Cluster48366"


client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
print(client.list_database_names())  # Check if databases are accessible