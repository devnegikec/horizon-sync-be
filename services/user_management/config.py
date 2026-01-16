"""User Management service configuration."""
from shared.config import Settings, settings


class UserManagementSettings(Settings):
    """User Management service specific settings."""
    
    # Invitation
    INVITATION_EXPIRE_DAYS: int = 7
    
    # Organization
    DEFAULT_PLAN_CODE: str = "free"
    MAX_FREE_USERS: int = 5
    MAX_FREE_TEAMS: int = 3


user_management_settings = UserManagementSettings()
