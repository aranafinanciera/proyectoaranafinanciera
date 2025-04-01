from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = AsyncIOMotorClient(MONGO_URI)
mongodb = client[MONGO_DB]  # <--- ESTA línea es la que debes poder importar

# Colecciones (opcional)
fraudes_collection = mongodb["fraudes_detectados"]
historial_collection = mongodb["historial_usuario"]
