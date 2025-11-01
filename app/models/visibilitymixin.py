from typing import Any, Dict, Optional, Type, TypeVar
from sqlalchemy import Column, Boolean, text, and_
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import or_
from sqlalchemy import Integer, ForeignKey
from app.schemas.user import Role

T = TypeVar("T")


class VisibilityMixin():
    """
    Mixin para control de visibilidad y acceso a recursos basado en roles.
    
    Proporciona métodos para:
    - Verificar permisos de acceso
    - Verificar propiedad de recursos
    - Realizar operaciones CRUD con validación de permisos
    - Aplicar filtros de visibilidad en queries
    """
    
    is_deleted = Column(Boolean, server_default=text('false'))
    is_visible = Column(Boolean, server_default=text('true'))
    is_paid = Column(Boolean, server_default=text('false'))
   
    
    @classmethod
    def apply_visibility_filters(cls, query, model_cls, current_user_role: Role = Role.FREE_USER, user_id: Optional[int] = None):
        """
        Aplica los filtros de visibilidad a una consulta basada en el rol del usuario.
        model_cls: La clase concreta (Post, Tag, etc.) que tiene las columnas owner_id, is_visible, etc.
        """
        # Los administradores ven todo (excepto eliminados)
        if current_user_role == Role.ADMIN:
            return query.filter(model_cls.is_deleted == False)
        
        # Usuarios autenticados
        if current_user_role in [Role.FREE_USER, Role.PAID_USER]:
            owner_condition = model_cls.owner_id == user_id if user_id else None
            public_condition = (model_cls.is_visible == True) & (model_cls.is_deleted == False)
            if current_user_role == Role.PAID_USER:
                paid_condition = (model_cls.is_visible == True) & (model_cls.is_paid == True) & (model_cls.is_deleted == False)
                conditions = [c for c in [owner_condition, public_condition, paid_condition] if c is not None]
                return query.filter(or_(*conditions))
            # Usuario gratuito
            conditions = [c for c in [owner_condition, public_condition] if c is not None]
            return query.filter(or_(*conditions))
        
        # No autenticados
        return query.filter(
            model_cls.is_visible == True,
            model_cls.is_paid == False,
            model_cls.is_deleted == False
        )
    
    def has_permission(self, current_user_role: Role, user_id: Optional[int] = None) -> bool:
        """
        Verifica si el usuario actual tiene permiso para ver/editar este recurso.
        
        Args:
            current_user_role: Rol del usuario actual
            user_id: ID del usuario actual (opcional, para verificar propiedad)
            
        Returns:
            bool: True si el usuario tiene permiso, False en caso contrario
        """
        # Recurso eliminado, solo visible para administradores
        if self.is_deleted:
            return current_user_role == Role.ADMIN
            
        # Administradores pueden ver/editar todo
        if current_user_role == Role.ADMIN:
            return True
            
        # El propietario siempre puede ver/editar sus recursos
        if user_id and self.owner_id == user_id:
            return True
            
        # Recurso privado, solo para el propietario
        if not self.is_visible:
            return False
            
        # Recurso de pago, solo para usuarios con suscripción
        if self.is_paid and current_user_role != Role.PAID_USER:
            return False
            
        # Recurso público y visible
        return True
    
    def is_owner(self, user_id: int) -> bool:
        """
        Verifica si el usuario es el propietario del recurso.
        
        Args:
            user_id: ID del usuario a verificar
            
        Returns:
            bool: True si el usuario es el propietario
        """
        return hasattr(self, 'owner_id') and self.owner_id == user_id
    
    def can_modify(self, current_user_role: Role, user_id: int) -> bool:
        """
        Verifica si el usuario puede modificar este recurso.
        Los administradores y propietarios pueden modificar.
        
        Args:
            current_user_role: Rol del usuario actual
            user_id: ID del usuario actual
            
        Returns:
            bool: True si el usuario puede modificar el recurso
        """
        return current_user_role == Role.ADMIN or self.is_owner(user_id)
    
    def verify_ownership(self, user_id: int, custom_message: Optional[str] = None) -> None:
        """
        Verifica que el usuario sea el propietario del recurso.
        Lanza PermissionError si no lo es.
        
        Args:
            user_id: ID del usuario a verificar
            custom_message: Mensaje personalizado de error (opcional)
            
        Raises:
            PermissionError: Si el usuario no es el propietario
        """
        if not self.is_owner(user_id):
            message = custom_message or f"Solo el propietario puede realizar esta acción"
            raise PermissionError(message)
    
    @classmethod
    async def update_with_ownership(
        cls: Type[T],
        db: AsyncSession,
        resource_id: int,
        current_user_id: int,
        update_data: dict,
        allow_admin: bool = True
    ) -> Optional[T]:
        """
        Actualiza un recurso verificando que el usuario es el dueño.
        
        Args:
            db: Sesión de base de datos
            resource_id: ID del recurso a actualizar
            current_user_id: ID del usuario actual
            update_data: Diccionario con los datos a actualizar
            allow_admin: Si True, permite a los admins modificar (default: True)
            
        Returns:
            Recurso actualizado o None si no existe
            
        Raises:
            PermissionError: Si el usuario no tiene permisos
        """
        resource = await cls.get_by_id(db, resource_id)
        if not resource:
            return None
        
        # Verificar propiedad
        resource.verify_ownership(current_user_id, 
            f"Solo el propietario puede modificar este {cls.__name__.lower()}")
        
        # Actualizar el recurso
        return await cls.update(db, resource_id, **update_data)
    
    @classmethod
    async def soft_delete_with_ownership(
        cls: Type[T],
        db: AsyncSession,
        resource_id: int,
        current_user_id: int,
        allow_admin: bool = True
    ) -> Optional[T]:
        """
        Realiza soft delete de un recurso verificando que el usuario es el dueño.
        
        Args:
            db: Sesión de base de datos
            resource_id: ID del recurso a eliminar
            current_user_id: ID del usuario actual
            allow_admin: Si True, permite a los admins eliminar (default: True)
            
        Returns:
            Recurso eliminado o None si no existe
            
        Raises:
            PermissionError: Si el usuario no tiene permisos
        """
        resource = await cls.get_by_id(db, resource_id)
        if not resource:
            return None
        
        # Verificar propiedad
        resource.verify_ownership(current_user_id,
            f"Solo el propietario puede eliminar este {cls.__name__.lower()}")
        
        return await cls.delete(db, resource_id)
    
    @classmethod
    async def restore_with_ownership(
        cls: Type[T],
        db: AsyncSession,
        resource_id: int,
        current_user_id: int,
        allow_admin: bool = True
    ) -> Optional[T]:
        """
        Restaura un recurso eliminado verificando que el usuario es el dueño.
        
        Args:
            db: Sesión de base de datos
            resource_id: ID del recurso a restaurar
            current_user_id: ID del usuario actual
            allow_admin: Si True, permite a los admins restaurar (default: True)
            
        Returns:
            Recurso restaurado o None si no existe
            
        Raises:
            PermissionError: Si el usuario no tiene permisos
        """
        resource = await cls.get_by_id(db, resource_id)
        if not resource:
            return None
        
        # Verificar propiedad
        resource.verify_ownership(current_user_id,
            f"Solo el propietario puede restaurar este {cls.__name__.lower()}")
        
        return await cls.restore(db, resource_id)