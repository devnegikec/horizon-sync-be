"""Authentication business logic service."""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import pyotp
from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models.user import User, UserOrganizationRole, UserStatus
from shared.models.auth import RefreshToken, PasswordReset, EmailVerification
from shared.models.role import Role, RolePermission, Permission, SystemRole
from shared.models.organization import Organization, OrganizationStatus
from shared.security.password import verify_password, hash_password
from shared.utils.helpers import generate_slug
from services.auth.config import auth_settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        organization_name: str
    ) -> tuple[User, Organization]:
        """
        Register a new user and create their organization.
        
        This is for first-time signup where a user creates a new account
        and a new organization simultaneously.
        """
        # 1. Create Organization
        organization = Organization(
            name=organization_name,
            slug=generate_slug(organization_name),
            status=OrganizationStatus.ACTIVE.value,
            settings={
                "timezone": "UTC",
                "currency": "USD",
                "language": "en"
            }
        )
        self.db.add(organization)
        await self.db.flush()

        # 2. Create User
        user = User(
            organization_id=organization.id,
            email=email.lower(),
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            display_name=f"{first_name} {last_name}",
            status=UserStatus.ACTIVE.value,
            email_verified=False
        )
        self.db.add(user)
        await self.db.flush()

        # 3. Create/Get Owner Role for this organization
        owner_role = Role(
            organization_id=organization.id,
            name="Owner",
            code=SystemRole.OWNER.value,
            is_active=True,
            is_system=True,
            hierarchy_level=100
        )
        self.db.add(owner_role)
        await self.db.flush()

        # 4. Link User to Role
        user_role = UserOrganizationRole(
            user_id=user.id,
            role_id=owner_role.id
        )
        self.db.add(user_role)
        await self.db.flush()

        return user, organization
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        query = select(User).where(User.email == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def record_failed_login(self, user: User) -> None:
        """Record a failed login attempt."""
        user.failed_login_attempts += 1
        
        # Lock account after max attempts
        if user.failed_login_attempts >= auth_settings.MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=auth_settings.LOCKOUT_DURATION_MINUTES
            )
        
        await self.db.flush()
    
    async def update_last_login(self, user: User, ip_address: Optional[str]) -> None:
        """Update user's last login timestamp."""
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address
        user.failed_login_attempts = 0  # Reset on successful login
        user.locked_until = None
        await self.db.flush()
    
    async def get_user_organization_context(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> Optional[UserOrganizationRole]:
        """Get user's organization and role context."""
        query = select(UserOrganizationRole).options(
            selectinload(UserOrganizationRole.user).selectinload(User.organization),
            selectinload(UserOrganizationRole.role)
        ).join(User).where(
            UserOrganizationRole.user_id == user_id,
            User.is_active == True
        )
        
        if organization_id:
            query = query.where(User.organization_id == organization_id)
        
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_role_permissions(self, role_id: UUID) -> List[str]:
        """Get permission codes for a role."""
        query = select(Permission.code).join(
            RolePermission,
            RolePermission.permission_id == Permission.id
        ).where(
            RolePermission.role_id == role_id
        )
        
        result = await self.db.execute(query)
        return [row for row in result.scalars().all()]
    
    async def store_refresh_token(
        self,
        user_id: UUID,
        token_id: str,
        token_hash: str,
        token_family: str,
        device_info: Optional[str],
        ip_address: Optional[str],
        expires_at: datetime
    ) -> RefreshToken:
        """Store a new refresh token."""
        # Parse device info
        device_name = None
        device_type = None
        browser_info = None
        os_info = None
        
        if device_info:
            # Simple parsing - can be enhanced with user-agents library
            device_info_lower = device_info.lower()
            if 'mobile' in device_info_lower or 'android' in device_info_lower or 'iphone' in device_info_lower:
                device_type = 'mobile'
            elif 'tablet' in device_info_lower or 'ipad' in device_info_lower:
                device_type = 'tablet'
            else:
                device_type = 'desktop'
            
            # Extract browser
            browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera']
            for browser in browsers:
                if browser in device_info_lower:
                    browser_info = browser.capitalize()
                    break
            
            device_name = device_info[:100]  # Truncate
        
        refresh_token = RefreshToken(
            id=UUID(token_id) if isinstance(token_id, str) else token_id,
            user_id=user_id,
            token_hash=token_hash,
            token_family=token_family,
            device_name=device_name,
            device_type=device_type,
            browser_info=browser_info,
            os_info=os_info,
            ip_address=ip_address,
            user_agent=device_info,
            expires_at=expires_at,
        )
        
        self.db.add(refresh_token)
        await self.db.flush()
        
        # Clean up old sessions if over limit
        await self._cleanup_old_sessions(user_id)
        
        return refresh_token
    
    async def _cleanup_old_sessions(self, user_id: UUID) -> None:
        """Remove oldest sessions if over limit."""
        # Count active sessions
        count_query = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow()
        ).order_by(RefreshToken.created_at.desc())
        
        result = await self.db.execute(count_query)
        sessions = result.scalars().all()
        
        if len(sessions) > auth_settings.MAX_SESSIONS_PER_USER:
            # Revoke oldest sessions
            for session in sessions[auth_settings.MAX_SESSIONS_PER_USER:]:
                session.revoke("session_limit_exceeded")
    
    async def get_refresh_token(self, token_id: str) -> Optional[RefreshToken]:
        """Get refresh token by ID."""
        tid = UUID(token_id) if isinstance(token_id, str) else token_id
        query = select(RefreshToken).where(RefreshToken.id == tid)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def revoke_token(self, token_id: str) -> None:
        """Revoke a specific refresh token."""
        tid = UUID(token_id) if isinstance(token_id, str) else token_id
        query = update(RefreshToken).where(
            RefreshToken.id == tid
        ).values(
            revoked_at=datetime.utcnow(),
            revoked_reason="manual"
        )
        await self.db.execute(query)
    
    async def revoke_token_family(self, token_family: str) -> None:
        """Revoke all tokens in a family (possible token reuse attack)."""
        query = update(RefreshToken).where(
            RefreshToken.token_family == token_family,
            RefreshToken.revoked_at.is_(None)
        ).values(
            revoked_at=datetime.utcnow(),
            revoked_reason="token_reuse_detected"
        )
        await self.db.execute(query)
    
    async def revoke_all_user_tokens(
        self,
        user_id: UUID,
        except_token_id: Optional[str] = None
    ) -> None:
        """Revoke all refresh tokens for a user."""
        conditions = [
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        ]
        
        if except_token_id:
            conditions.append(RefreshToken.id != except_token_id)
        
        query = update(RefreshToken).where(
            and_(*conditions)
        ).values(
            revoked_at=datetime.utcnow(),
            revoked_reason="user_logout_all"
        )
        await self.db.execute(query)
    
    async def get_user_sessions(self, user_id: UUID) -> List[RefreshToken]:
        """Get all active sessions for a user."""
        query = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow()
        ).order_by(RefreshToken.last_used_at.desc().nullsfirst())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def verify_mfa_code(self, user: User, code: str) -> bool:
        """Verify MFA code (TOTP or backup code)."""
        if not user.mfa_secret:
            return False
        
        # Try TOTP first
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code, valid_window=1):
            return True
        
        # Try backup codes
        if user.mfa_backup_codes and code in user.mfa_backup_codes:
            # Remove used backup code
            user.mfa_backup_codes = [c for c in user.mfa_backup_codes if c != code]
            await self.db.flush()
            return True
        
        return False
    
    async def create_password_reset(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> PasswordReset:
        """Create a password reset token."""
        # Invalidate any existing reset tokens
        await self.db.execute(
            update(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.used_at.is_(None)
            ).values(used_at=datetime.utcnow())
        )
        
        reset = PasswordReset(
            user_id=user_id,
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        
        self.db.add(reset)
        await self.db.flush()
        
        return reset
    
    async def find_valid_password_reset(self, token: str) -> Optional[PasswordReset]:
        """Find a valid password reset by token."""
        # We need to check all tokens since we stored hashes
        query = select(PasswordReset).where(
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        resets = result.scalars().all()
        
        for reset in resets:
            if verify_password(token, reset.token_hash):
                return reset
        
        return None
    
    async def find_valid_email_verification(self, token: str) -> Optional[EmailVerification]:
        """Find a valid email verification by token."""
        query = select(EmailVerification).where(
            EmailVerification.verified_at.is_(None),
            EmailVerification.expires_at > datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        verifications = result.scalars().all()
        
        for verification in verifications:
            if verify_password(token, verification.token_hash):
                return verification
        
        return None
