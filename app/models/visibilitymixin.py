from typing import Any, Dict, Optional
from sqlalchemy import Column, Boolean, text, and_
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import or_
from sqlalchemy import Integer, ForeignKey
from app.schemas.user import Role


class VisibilityMixin():
   
    # Mixin para control de visibilidad y acceso a recursos basado en roles.
    
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