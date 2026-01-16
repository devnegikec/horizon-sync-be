"""Role and Permission models for RBAC."""
import enum
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Text, UniqueConstraint
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


class Role(Base, UUIDMixin, TimestampMixin):
    """
    Role model - defines a set of permissions.
    Can be system-defined or custom per organization.
    """
    __tablename__ = "roles"
    
    # Organization (null for system roles)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Role info
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Type
    is_system = Column(Boolean, default=False)  # System roles can't be deleted
    is_default = Column(Boolean, default=False)  # Assigned to new users by default
    
    # Hierarchy level (higher = more permissions)
    hierarchy_level = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="roles"
    )
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    
    # Unique constraint: code must be unique within an organization (or globally for system roles)
    __table_args__ = (
        UniqueConstraint(
            'organization_id', 'code',
            name='uq_role_org_code'
        ),
    )
    
    @property
    def permissions(self) -> List["Permission"]:
        """Get all permissions for this role."""
        return [rp.permission for rp in self.role_permissions]
    
    def __repr__(self):
        return f"<Role(name='{self.name}', code='{self.code}')>"


# Import Integer at module level
from sqlalchemy import Integer


class ResourceType(str, enum.Enum):
    """Types of resources that can be permissioned."""
    ORGANIZATION = "organization"
    USER = "user"
    ROLE = "role"
    TEAM = "team"
    LEAD = "lead"
    CONTACT = "contact"
    DEAL = "deal"
    QUOTE = "quote"
    ORDER = "order"
    TICKET = "ticket"
    PRODUCT = "product"
    INVENTORY = "inventory"
    WAREHOUSE = "warehouse"
    REPORT = "report"
    SETTING = "setting"
    SUBSCRIPTION = "subscription"
    AUDIT_LOG = "audit_log"


class ActionType(str, enum.Enum):
    """Types of actions that can be performed."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    EXPORT = "export"
    IMPORT = "import"
    ASSIGN = "assign"
    APPROVE = "approve"
    REJECT = "reject"
    ARCHIVE = "archive"
    RESTORE = "restore"


class Permission(Base, UUIDMixin, TimestampMixin):
    """
    Permission model - defines a specific action on a resource.
    Permissions are global, not per-organization.
    """
    __tablename__ = "permissions"
    
    # Permission identifier
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Resource and action
    resource = Column(Enum(ResourceType), nullable=False, index=True)
    action = Column(Enum(ActionType), nullable=False, index=True)
    
    # Grouping
    module = Column(String(50), nullable=True)  # crm, inventory, support, etc.
    category = Column(String(50), nullable=True)  # For UI grouping
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
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
    
    # Optional: conditions for when this permission applies
    conditions = Column(JSONB, nullable=True)
    # Example: {"own_records_only": true}
    
    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")
    
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    
    def __repr__(self):
        return f"<RolePermission(role={self.role_id}, permission={self.permission_id})>"
