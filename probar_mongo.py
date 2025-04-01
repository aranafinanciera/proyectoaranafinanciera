import asyncio
from app.database.mongo import mongodb

async def probar_conexion():
    try:
        # Verificar lista de colecciones
        colecciones = await mongodb.list_collection_names()
        print("✅ Conexión a MongoDB exitosa")
        print("Colecciones:", colecciones)
    except Exception as e:
        print("❌ Error al conectar a MongoDB:", e)

if __name__ == "__main__":
    asyncio.run(probar_conexion())
