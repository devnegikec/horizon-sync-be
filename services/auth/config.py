"""Auth service specific configuration."""
from shared.config import Settings, settings


class AuthSettings(Settings):
    """Auth service specific settings."""
    
    # Password reset
    PASSWORD_RESET_EXPIRE_HOURS: int = 1
    
    # Email verification
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    
    # Invitation
    INVITATION_EXPIRE_DAYS: int = 7
    
    # Login security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    
    # Session
    MAX_SESSIONS_PER_USER: int = 10
    
    # MFA
    MFA_ISSUER: str = "Horizon Sync ERP"


auth_settings = AuthSettings()
