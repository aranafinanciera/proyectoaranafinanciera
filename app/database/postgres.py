#postgres.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def probar_conexion():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        print("✅ Conexión a PostgreSQL exitosa")
    except SQLAlchemyError as e:
        print("❌ Error de conexión:", e)
