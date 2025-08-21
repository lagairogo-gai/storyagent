"""
User model for authentication and user management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles enumeration"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """
    User model for authentication and authorization
    """
    __tablename__ = "users"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    
    # Status and permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    status = Column(String(20), default=UserStatus.ACTIVE.value, nullable=False)
    
    # Security settings
    password_changed_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Two-factor authentication
    totp_secret = Column(String(32), nullable=True)
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)
    backup_codes_generated_at = Column(DateTime, nullable=True)
    
    # Preferences and settings
    preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)
    ui_theme = Column(String(20), default="light")
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Integration settings
    jira_credentials = Column(JSON, nullable=True)
    confluence_credentials = Column(JSON, nullable=True)
    sharepoint_credentials = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Additional metadata
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Analytics and tracking
    last_activity_at = Column(DateTime, nullable=True)
    session_count = Column(Integer, default=0)
    total_stories_generated = Column(Integer, default=0)
    total_documents_uploaded = Column(Integer, default=0)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by], remote_side=[id])
    updated_by_user = relationship("User", foreign_keys=[updated_by], remote_side=[id])
    
    # Reverse relationships (defined in other models)
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    documents = relationship("Document", back_populates="uploaded_by")
    user_stories = relationship("UserStory", back_populates="created_by_user")
    api_keys = relationship("APIKey", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __init__(self, **kwargs):
        # Set default preferences
        default_preferences = {
            "email_notifications": True,
            "push_notifications": False,
            "auto_save": True,
            "show_tutorials": True,
            "default_project": None,
            "items_per_page": 20
        }
        
        default_notification_settings = {
            "story_generation_complete": True,
            "document_processing_complete": True,
            "integration_errors": True,
            "system_updates": False,
            "weekly_summary": True
        }
        
        if 'preferences' not in kwargs:
            kwargs['preferences'] = default_preferences
        if 'notification_settings' not in kwargs:
            kwargs['notification_settings'] = default_notification_settings
            
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def __str__(self):
        return f"{self.full_name or self.username} ({self.email})"
    
    @property
    def display_name(self) -> str:
        """Get user's display name"""
        return self.full_name or self.username
    
    @property
    def initials(self) -> str:
        """Get user's initials"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.full_name:
            names = self.full_name.split()
            if len(names) >= 2:
                return f"{names[0][0]}{names[-1][0]}".upper()
            else:
                return names[0][0].upper()
        else:
            return self.username[0].upper()
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    @property
    def can_login(self) -> bool:
        """Check if user can login"""
        return (
            self.is_active and 
            self.status == UserStatus.ACTIVE.value and 
            not self.is_locked
        )
    
    @property
    def permissions(self) -> List[str]:
        """Get user permissions based on role"""
        role_permissions = {
            UserRole.ADMIN: [
                "user:create", "user:read", "user:update", "user:delete",
                "project:create", "project:read", "project:update", "project:delete",
                "document:create", "document:read", "document:update", "document:delete",
                "story:create", "story:read", "story:update", "story:delete",
                "integration:configure", "integration:use",
                "system:configure", "system:monitor",
                "audit:read"
            ],
            UserRole.MANAGER: [
                "user:read", "user:update",
                "project:create", "project:read", "project:update",
                "document:create", "document:read", "document:update", "document:delete",
                "story:create", "story:read", "story:update", "story:delete",
                "integration:use",
                "team:manage"
            ],
            UserRole.ANALYST: [
                "project:read", "project:update",
                "document:create", "document:read", "document:update",
                "story:create", "story:read", "story:update",
                "integration:use"
            ],
            UserRole.USER: [
                "project:read",
                "document:create", "document:read",
                "story:create", "story:read",
                "integration:use"
            ],
            UserRole.VIEWER: [
                "project:read",
                "document:read",
                "story:read"
            ]
        }
        
        base_permissions = role_permissions.get(UserRole(self.role), [])
        
        # Superusers get all permissions
        if self.is_superuser:
            all_permissions = set()
            for perms in role_permissions.values():
                all_permissions.update(perms)
            return list(all_permissions)
        
        return base_permissions
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def can_access_project(self, project) -> bool:
        """Check if user can access a specific project"""
        if self.is_superuser:
            return True
        
        # Project owners can always access
        if project.owner_id == self.id:
            return True
        
        # Check if user is a team member
        return any(member.user_id == self.id for member in project.team_members)
    
    def update_last_login(self):
        """Update last login timestamp and increment login count"""
        self.last_login_at = datetime.utcnow()
        self.login_count += 1
        self.failed_login_attempts = 0  # Reset failed attempts on successful login
    
    def record_failed_login(self):
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def unlock_account(self):
        """Unlock user account"""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def enable_2fa(self, secret: str):
        """Enable two-factor authentication"""
        self.totp_secret = secret
        self.is_2fa_enabled = True
    
    def disable_2fa(self):
        """Disable two-factor authentication"""
        self.totp_secret = None
        self.is_2fa_enabled = False
        self.backup_codes_generated_at = None
    
    def update_preferences(self, preferences: dict):
        """Update user preferences"""
        current_prefs = self.preferences or {}
        current_prefs.update(preferences)
        self.preferences = current_prefs
    
    def update_notification_settings(self, settings: dict):
        """Update notification settings"""
        current_settings = self.notification_settings or {}
        current_settings.update(settings)
        self.notification_settings = current_settings
    
    def get_integration_credentials(self, integration_type: str) -> Optional[dict]:
        """Get credentials for specific integration"""
        credentials_map = {
            "jira": self.jira_credentials,
            "confluence": self.confluence_credentials,
            "sharepoint": self.sharepoint_credentials
        }
        return credentials_map.get(integration_type)
    
    def set_integration_credentials(self, integration_type: str, credentials: dict):
        """Set credentials for specific integration"""
        if integration_type == "jira":
            self.jira_credentials = credentials
        elif integration_type == "confluence":
            self.confluence_credentials = credentials
        elif integration_type == "sharepoint":
            self.sharepoint_credentials = credentials
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "initials": self.initials,
            "phone_number": self.phone_number,
            "department": self.department,
            "job_title": self.job_title,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "status": self.status,
            "is_2fa_enabled": self.is_2fa_enabled,
            "preferences": self.preferences,
            "notification_settings": self.notification_settings,
            "ui_theme": self.ui_theme,
            "language": self.language,
            "timezone": self.timezone,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "website": self.website,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "login_count": self.login_count,
            "session_count": self.session_count,
            "total_stories_generated": self.total_stories_generated,
            "total_documents_uploaded": self.total_documents_uploaded,
            "permissions": self.permissions
        }
        
        if include_sensitive:
            data.update({
                "is_superuser": self.is_superuser,
                "failed_login_attempts": self.failed_login_attempts,
                "is_locked": self.is_locked,
                "can_login": self.can_login
            })
        
        return data


class APIKey(Base):
    """
    API Key model for external access
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Permissions and access
    permissions = Column(JSON, default=list)
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    allowed_ips = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="api_keys")
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<APIKey(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    @property
    def is_valid(self) -> bool:
        """Check if API key is valid"""
        if not self.is_active:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def record_usage(self, ip_address: str = None):
        """Record API key usage"""
        self.last_used_at = datetime.utcnow()
        self.usage_count += 1
    
    def to_dict(self) -> dict:
        """Convert API key to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "rate_limit": self.rate_limit,
            "is_active": self.is_active,
            "is_valid": self.is_valid,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    """
    Audit log model for tracking user actions
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True)
    
    # Results
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Additional data
    details = Column(JSON, nullable=True)
    changes = Column(JSON, nullable=True)  # Before/after values
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="audit_logs")
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Convert audit log to dictionary"""
        return {
            "id": self.id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "success": self.success,
            "error_message": self.error_message,
            "details": self.details,
            "changes": self.changes,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }