from typing import Any, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, lazyload
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

T = TypeVar("T")

class CRUDBase:

    @classmethod
    async def create(cls: Type[T], db: AsyncSession, **kwargs) -> T:
        try:
            instance = cls(**kwargs)
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Error creating {cls.__name__}: {str(e)}")

    @classmethod
    async def get_by_id(
        cls: Type[T],
        db: AsyncSession,
        id: Any,
        load_type: str = "lazy"
    ) -> Optional[T]:
        options = cls._get_load_options(load_type)
        query = select(cls).options(*options).where(cls.id == id)

        try:
            result = await db.execute(query)
            return result.scalars().first()
        except NoResultFound:
            return None

    @classmethod
    async def get_all(
        cls: Type[T],
        db: AsyncSession,
        load_type: str = "lazy",
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        options = cls._get_load_options(load_type)
        query = select(cls).options(*options).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def update(
        cls: Type[T],
        db: AsyncSession,
        id: Any,
        **kwargs
    ) -> Optional[T]:
  
        try:
            instance = await cls.get_by_id(db, id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            await db.commit()
            await db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Error updating {cls.__name__}: {str(e)}")

    @classmethod
    async def hard_delete(
        cls: Type[T],
        db: AsyncSession,
        id: Any
    ) -> bool:
        try:
            instance = await cls.get_by_id(db, id)
            if not instance:
                return False
            
            await db.delete(instance)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Error deleting {cls.__name__}: {str(e)}")

    @classmethod
    async def delete(
        cls: Type[T],
        db: AsyncSession,
        id: Any
    ) -> Optional[T]:
        try:
            instance = await cls.get_by_id(db, id)
            if not instance:
                return None
            
            if not hasattr(instance, 'is_deleted'):
                raise AttributeError(f"{cls.__name__} does not have 'is_deleted' field")
            
            instance.is_deleted = True
            await db.commit()
            await db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Error soft deleting {cls.__name__}: {str(e)}")

    @classmethod
    async def restore(
        cls: Type[T],
        db: AsyncSession,
        id: Any
    ) -> Optional[T]:
        try:
            instance = await cls.get_by_id(db, id)
            if not instance:
                return None
            
            if not hasattr(instance, 'is_deleted'):
                raise AttributeError(f"{cls.__name__} does not have 'is_deleted' field")
            
            instance.is_deleted = False
            await db.commit()
            await db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Error restoring {cls.__name__}: {str(e)}")

    @staticmethod
    def _get_load_options(load_type: str):
        if load_type == "selectin":
            return [selectinload("*")]
        elif load_type == "joined":
            return [joinedload("*")]
        elif load_type == "lazy":
            return [lazyload("*")]
        else:
            raise ValueError(
                f"Load type '{load_type}' not recognized. "
                "Use 'lazy', 'selectin' or 'joined'."
            )
