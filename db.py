#db.py

from pymongo import MongoClient
from config import Config
import certifi  # New import for SSL certificate handling

# Connect to MongoDB
def get_db_connection():
    # Use certifi to specify a trusted CA certificate
    client = MongoClient(Config.MONGO_URI, tlsCAFile=certifi.where())
    db = client[Config.DATABASE_NAME]  # Select the database
    return db

