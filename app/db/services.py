import contextlib
from typing import AsyncIterator, Annotated
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncConnection, 
    AsyncEngine, 
    AsyncSession,
    async_sessionmaker, 
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, host: str) -> None:
        
        if self._engine is not None:
            return
            
        self._engine = create_async_engine(
            host,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,  # Enable connection pool pre-ping
            pool_size=10,  # Maximum number of connections to keep in the pool
            max_overflow=20  # Maximum number of connections to create above pool_size
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def close(self) -> None:
        
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Used for testing
    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.drop_all)


# Global instance of DatabaseSessionManager
sessionmanager = DatabaseSessionManager()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields db sessions
    """
    async with sessionmanager.session() as session:
        yield session

# Type alias for dependency injection
SessionDep = Annotated[AsyncSession, Depends(get_db)]