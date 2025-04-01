import asyncio
from app.database.postgres import probar_conexion

if __name__ == "__main__":
    asyncio.run(probar_conexion())