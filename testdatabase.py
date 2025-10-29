import asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

async def test_db_connection():
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            # Intenta ejecutar una consulta simple
            result = await conn.execute("SELECT 1")
            print("✅ Conexión exitosa a la base de datos!")
            print(f"URL: {settings.DATABASE_URL}")
    except Exception as e:
        print("❌ Error conectando a la base de datos:")
        print(f"Error: {str(e)}")
        print(f"URL intentada: {settings.DATABASE_URL}")

if __name__ == "__main__":
    asyncio.run(test_db_connection())