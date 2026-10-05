import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME") or os.getenv("DATABASE_NAME", "profil_db")

client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
database = client[DB_NAME]

cv_collection = database.get_collection("cvs")
job_collection = database.get_collection("job_postings")
match_collection = database.get_collection("matches")

async def ping_database() -> bool:
    try:
        await client.admin.command('ping')
        return True
    except Exception:
        return False