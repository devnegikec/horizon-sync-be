"""Role and Permission models for RBAC."""
import enum
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from shared.models.organization import Organization


class SystemRole(str, enum.Enum):
    """System-defined roles that exist in every organization."""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class Role(Base, UUIDMixin):
    """
    Role model - defines a set of permissions.
    """
    __tablename__ = "roles"
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Role info
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    hierarchy_level = Column(Integer, default=0)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="roles"
    )
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Role(name='{self.name}', code='{self.code}')>"


class Permission(Base, UUIDMixin):
    """
    Permission model - defines a specific action on a resource.
    """
    __tablename__ = "permissions"
    
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Permission(code='{self.code}')>"


class RolePermission(Base, UUIDMixin):
    """
    Many-to-many mapping between roles and permissions.
    """
    __tablename__ = "role_permissions"
    
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")
    
    def __repr__(self):
        return f"<RolePermission(role={self.role_id}, permission={self.permission_id})>"

