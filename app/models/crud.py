from typing import Any, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, lazyload
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

T = TypeVar("T")

class CRUDBase:
    """Clase base genérica para operaciones CRUD asíncronas."""

    @classmethod
    async def create(cls: Type[T], db: AsyncSession, **kwargs) -> T:
        """
        Crea una nueva instancia del modelo y la guarda en la base de datos.
        """
        try:
            instance = cls(**kwargs)
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Error al crear {cls.__name__}: {str(e)}")

    @classmethod
    async def get_by_id(
        cls: Type[T],
        db: AsyncSession,
        id: Any,
        load_type: str = "lazy"
    ) -> Optional[T]:
        """
        Obtiene un registro por ID con control del tipo de carga:
        - `lazy` (por defecto): solo la entidad.
        - `selectin`: relaciones cargadas mediante consultas separadas (eficiente para colecciones).
        - `joined`: carga todas las relaciones mediante JOINs.
        """
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
        """
        Retorna todos los registros del modelo con soporte para distintos tipos de carga.
        """
        options = cls._get_load_options(load_type)
        query = select(cls).options(*options).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    def _get_load_options(load_type: str):
        """
        Devuelve la configuración de carga según el tipo especificado.
        """
        if load_type == "selectin":
            return [selectinload("*")]
        elif load_type == "joined":
            return [joinedload("*")]
        elif load_type == "lazy":
            return [lazyload("*")]
        else:
            raise ValueError(
                f"Tipo de carga '{load_type}' no reconocido. "
                "Usa 'lazy', 'selectin' o 'joined'."
            )
