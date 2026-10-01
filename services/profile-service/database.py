import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# .env dosyasından okur; yoksa varsayılan Docker Compose ağına (mongodb) bağlanır
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "profil_db")

# MongoDB Asenkron İstemcisi (5 saniye timeout ile)
client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
database = client[DB_NAME]

# Koleksiyonlar
cv_collection = database.get_collection("cvs")
job_collection = database.get_collection("job_postings")
match_collection = database.get_collection("matches")

async def ping_database() -> bool:
    """Veritabanının ayakta olup olmadığını kontrol eder."""
    try:
        await client.admin.command('ping')
        return True
    except Exception:
        return False