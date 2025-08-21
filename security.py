"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis
import json
import logging
from functools import wraps

from app.core.config import get_settings
from app.core.database import get_database
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Redis client for token blacklisting and session management
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None


class SecurityManager:
    """
    Centralized security management
    """
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.redis_client = redis_client
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password hashing failed"
            )
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                )
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            })
            
            encoded_jwt = jwt.encode(
                to_encode,
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
            
            # Store token metadata in Redis for session management
            if self.redis_client:
                token_data = {
                    "user_id": data.get("sub"),
                    "username": data.get("username"),
                    "created_at": datetime.utcnow().isoformat(),
                    "expires_at": expire.isoformat()
                }
                
                # Store with expiration
                self.redis_client.setex(
                    f"token:{encoded_jwt[:20]}",  # Use first 20 chars as key
                    int(expires_delta.total_seconds() if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
                    json.dumps(token_data)
                )
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation failed"
            )
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token"""
        try:
            data = {
                "sub": str(user_id),
                "type": "refresh"
            }
            
            expire = datetime.utcnow() + timedelta(days=30)  # 30 days
            data.update({"exp": expire})
            
            encoded_jwt = jwt.encode(
                data,
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
            
            # Store refresh token in Redis
            if self.redis_client:
                self.redis_client.setex(
                    f"refresh:{user_id}",
                    30 * 24 * 60 * 60,  # 30 days in seconds
                    encoded_jwt
                )
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Refresh token creation failed"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Verify token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    
    def blacklist_token(self, token: str):
        """Add token to blacklist"""
        if self.redis_client:
            try:
                # Decode token to get expiration
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False}  # Don't verify expiration for blacklisting
                )
                
                # Calculate remaining TTL
                exp = payload.get("exp")
                if exp:
                    exp_datetime = datetime.fromtimestamp(exp)
                    remaining_seconds = int((exp_datetime - datetime.utcnow()).total_seconds())
                    
                    if remaining_seconds > 0:
                        self.redis_client.setex(
                            f"blacklist:{token[:20]}",
                            remaining_seconds,
                            "1"
                        )
                
            except Exception as e:
                logger.error(f"Token blacklisting error: {e}")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        if self.redis_client:
            try:
                return self.redis_client.exists(f"blacklist:{token[:20]}") > 0
            except Exception as e:
                logger.error(f"Blacklist check error: {e}")
        return False
    
    def revoke_all_user_tokens(self, user_id: int):
        """Revoke all tokens for a user"""
        if self.redis_client:
            try:
                # Remove refresh token
                self.redis_client.delete(f"refresh:{user_id}")
                
                # Note: In a production system, you might want to maintain
                # a list of active tokens per user for mass revocation
                
            except Exception as e:
                logger.error(f"Token revocation error: {e}")


# Global security manager
security_manager = SecurityManager()

# Convenience functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return security_manager.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return security_manager.get_password_hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    return security_manager.create_access_token(data, expires_delta)


def create_refresh_token(user_id: int) -> str:
    """Create refresh token"""
    return security_manager.create_refresh_token(user_id)


# Authentication dependencies
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to verify JWT token"""
    return security_manager.verify_token(credentials.credentials)


async def get_current_user(
    db: Session = Depends(get_database),
    token_data: Dict[str, Any] = Depends(verify_token)
) -> User:
    """Get current authenticated user"""
    try:
        user_id = token_data.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Authorization decorators
def require_permissions(permissions: list):
    """Decorator to require specific permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permissions
            user_permissions = getattr(current_user, 'permissions', [])
            if not any(perm in user_permissions for perm in permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: str):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if current_user.role != role and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Rate limiting utilities
class RateLimiter:
    """
    Simple rate limiter using Redis
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or security_manager.redis_client
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int = 3600  # 1 hour window
    ) -> bool:
        """Check if request is within rate limits"""
        if not self.redis_client:
            return True  # No rate limiting if Redis unavailable
        
        try:
            current = self.redis_client.get(f"rate_limit:{key}")
            if current is None:
                # First request
                self.redis_client.setex(f"rate_limit:{key}", window, 1)
                return True
            
            if int(current) >= limit:
                return False
            
            # Increment counter
            self.redis_client.incr(f"rate_limit:{key}")
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow request if rate limiting fails


# Global rate limiter
rate_limiter = RateLimiter()


# API Key management
class APIKeyManager:
    """
    Manage API keys for external integrations
    """
    
    def __init__(self):
        self.redis_client = security_manager.redis_client
    
    def generate_api_key(self, user_id: int, name: str, permissions: list = None) -> str:
        """Generate new API key"""
        import secrets
        
        api_key = f"rag_{secrets.token_urlsafe(32)}"
        
        if self.redis_client:
            key_data = {
                "user_id": user_id,
                "name": name,
                "permissions": permissions or [],
                "created_at": datetime.utcnow().isoformat(),
                "last_used": None,
                "is_active": True
            }
            
            # Store API key data (no expiration for API keys)
            self.redis_client.set(
                f"api_key:{api_key}",
                json.dumps(key_data)
            )
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return associated data"""
        if not self.redis_client:
            return None
        
        try:
            key_data = self.redis_client.get(f"api_key:{api_key}")
            if key_data:
                data = json.loads(key_data)
                if data.get("is_active"):
                    # Update last used timestamp
                    data["last_used"] = datetime.utcnow().isoformat()
                    self.redis_client.set(
                        f"api_key:{api_key}",
                        json.dumps(data)
                    )
                    return data
            return None
            
        except Exception as e:
            logger.error(f"API key verification error: {e}")
            return None
    
    def revoke_api_key(self, api_key: str):
        """Revoke API key"""
        if self.redis_client:
            self.redis_client.delete(f"api_key:{api_key}")


# Global API key manager
api_key_manager = APIKeyManager()


# Session management
class SessionManager:
    """
    Manage user sessions
    """
    
    def __init__(self):
        self.redis_client = security_manager.redis_client
    
    async def create_session(self, user_id: int, device_info: dict = None) -> str:
        """Create new user session"""
        import uuid
        
        session_id = str(uuid.uuid4())
        
        if self.redis_client:
            session_data = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "device_info": device_info or {},
                "is_active": True
            }
            
            # Store session with 24 hour expiration
            self.redis_client.setex(
                f"session:{session_id}",
                24 * 60 * 60,
                json.dumps(session_data)
            )
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if not self.redis_client:
            return None
        
        try:
            session_data = self.redis_client.get(f"session:{session_id}")
            if session_data:
                return json.loads(session_data)
            return None
            
        except Exception as e:
            logger.error(f"Session retrieval error: {e}")
            return None
    
    async def update_session_activity(self, session_id: str):
        """Update session last activity"""
        if self.redis_client:
            try:
                session_data = await self.get_session(session_id)
                if session_data:
                    session_data["last_activity"] = datetime.utcnow().isoformat()
                    self.redis_client.setex(
                        f"session:{session_id}",
                        24 * 60 * 60,
                        json.dumps(session_data)
                    )
            except Exception as e:
                logger.error(f"Session activity update error: {e}")
    
    async def revoke_session(self, session_id: str):
        """Revoke user session"""
        if self.redis_client:
            self.redis_client.delete(f"session:{session_id}")
    
    async def get_user_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        if not self.redis_client:
            return []
        
        try:
            sessions = []
            for key in self.redis_client.scan_iter(match="session:*"):
                session_data = self.redis_client.get(key)
                if session_data:
                    data = json.loads(session_data)
                    if data.get("user_id") == user_id and data.get("is_active"):
                        sessions.append({
                            "session_id": key.split(":")[1],
                            **data
                        })
            return sessions
            
        except Exception as e:
            logger.error(f"User sessions retrieval error: {e}")
            return []


# Global session manager
session_manager = SessionManager()


# Security audit utilities
class SecurityAuditLogger:
    """
    Log security-related events for auditing
    """
    
    def __init__(self):
        self.logger = logging.getLogger("security_audit")
        handler = logging.FileHandler("security_audit.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_login_attempt(self, username: str, success: bool, ip_address: str = None):
        """Log login attempt"""
        self.logger.info(
            f"LOGIN_ATTEMPT: username={username}, success={success}, ip={ip_address}"
        )
    
    def log_token_creation(self, user_id: int, token_type: str):
        """Log token creation"""
        self.logger.info(
            f"TOKEN_CREATED: user_id={user_id}, type={token_type}"
        )
    
    def log_token_revocation(self, user_id: int, reason: str = None):
        """Log token revocation"""
        self.logger.info(
            f"TOKEN_REVOKED: user_id={user_id}, reason={reason}"
        )
    
    def log_permission_denied(self, user_id: int, resource: str, action: str):
        """Log permission denied events"""
        self.logger.warning(
            f"PERMISSION_DENIED: user_id={user_id}, resource={resource}, action={action}"
        )
    
    def log_api_key_usage(self, api_key_prefix: str, endpoint: str):
        """Log API key usage"""
        self.logger.info(
            f"API_KEY_USED: key_prefix={api_key_prefix}, endpoint={endpoint}"
        )
    
    def log_suspicious_activity(self, user_id: int, activity: str, details: dict = None):
        """Log suspicious activity"""
        self.logger.warning(
            f"SUSPICIOUS_ACTIVITY: user_id={user_id}, activity={activity}, details={details}"
        )


# Global security audit logger
security_audit = SecurityAuditLogger()


# Two-factor authentication utilities
class TwoFactorAuth:
    """
    Handle two-factor authentication
    """
    
    def __init__(self):
        self.redis_client = security_manager.redis_client
    
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret"""
        import pyotp
        return pyotp.random_base32()
    
    def generate_qr_code_url(self, email: str, secret: str) -> str:
        """Generate QR code URL for TOTP setup"""
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name="RAG User Story Generator"
        )
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    def generate_backup_codes(self, user_id: int) -> list:
        """Generate backup codes for 2FA"""
        import secrets
        
        codes = [secrets.token_hex(4) for _ in range(10)]
        
        if self.redis_client:
            # Store backup codes (hashed)
            hashed_codes = [get_password_hash(code) for code in codes]
            self.redis_client.setex(
                f"backup_codes:{user_id}",
                365 * 24 * 60 * 60,  # 1 year
                json.dumps(hashed_codes)
            )
        
        return codes
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verify and consume backup code"""
        if not self.redis_client:
            return False
        
        try:
            codes_data = self.redis_client.get(f"backup_codes:{user_id}")
            if not codes_data:
                return False
            
            hashed_codes = json.loads(codes_data)
            
            for i, hashed_code in enumerate(hashed_codes):
                if verify_password(code, hashed_code):
                    # Remove used code
                    hashed_codes.pop(i)
                    self.redis_client.setex(
                        f"backup_codes:{user_id}",
                        365 * 24 * 60 * 60,
                        json.dumps(hashed_codes)
                    )
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Backup code verification error: {e}")
            return False


# Global 2FA manager
two_factor_auth = TwoFactorAuth()


# Password policy utilities
class PasswordPolicy:
    """
    Enforce password policies
    """
    
    def __init__(self):
        self.min_length = 8
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_special_chars = True
        self.min_special_chars = 1
    
    def validate_password(self, password: str) -> tuple[bool, list]:
        """Validate password against policy"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.require_special_chars:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            special_count = sum(1 for c in password if c in special_chars)
            if special_count < self.min_special_chars:
                errors.append(f"Password must contain at least {self.min_special_chars} special character(s)")
        
        return len(errors) == 0, errors
    
    def check_common_passwords(self, password: str) -> bool:
        """Check if password is in common passwords list"""
        # In production, this would check against a comprehensive list
        common_passwords = {
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master"
        }
        return password.lower() in common_passwords
    
    def calculate_password_strength(self, password: str) -> dict:
        """Calculate password strength score"""
        score = 0
        feedback = []
        
        # Length scoring
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        else:
            feedback.append("Use at least 8 characters")
        
        # Character variety scoring
        if any(c.islower() for c in password):
            score += 10
        else:
            feedback.append("Add lowercase letters")
        
        if any(c.isupper() for c in password):
            score += 10
        else:
            feedback.append("Add uppercase letters")
        
        if any(c.isdigit() for c in password):
            score += 10
        else:
            feedback.append("Add numbers")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            score += 15
        else:
            feedback.append("Add special characters")
        
        # Complexity bonus
        char_types = sum([
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(c in special_chars for c in password)
        ])
        
        if char_types >= 3:
            score += 20
        
        # Common password penalty
        if self.check_common_passwords(password):
            score -= 30
            feedback.append("Avoid common passwords")
        
        # Determine strength level
        if score >= 80:
            strength = "Strong"
        elif score >= 60:
            strength = "Good"
        elif score >= 40:
            strength = "Fair"
        else:
            strength = "Weak"
        
        return {
            "score": max(0, min(100, score)),
            "strength": strength,
            "feedback": feedback
        }


# Global password policy
password_policy = PasswordPolicy()


# Device fingerprinting
class DeviceFingerprint:
    """
    Generate device fingerprints for security
    """
    
    @staticmethod
    def generate_fingerprint(request_headers: dict, user_agent: str = None) -> str:
        """Generate device fingerprint from request headers"""
        import hashlib
        
        # Collect fingerprinting data
        fingerprint_data = {
            "user_agent": user_agent or request_headers.get("user-agent", ""),
            "accept_language": request_headers.get("accept-language", ""),
            "accept_encoding": request_headers.get("accept-encoding", ""),
            "accept": request_headers.get("accept", ""),
        }
        
        # Create fingerprint hash
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]


# Export all security utilities
__all__ = [
    "SecurityManager",
    "security_manager",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "require_permissions",
    "require_role",
    "RateLimiter",
    "rate_limiter",
    "APIKeyManager",
    "api_key_manager",
    "SessionManager",
    "session_manager",
    "SecurityAuditLogger",
    "security_audit",
    "TwoFactorAuth",
    "two_factor_auth",
    "PasswordPolicy",
    "password_policy",
    "DeviceFingerprint"
]