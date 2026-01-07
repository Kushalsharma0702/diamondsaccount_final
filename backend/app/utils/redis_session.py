"""
Redis session management for secure authentication and session tracking.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not installed. Install with: pip install redis")

# Load .env from project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = os.getenv("REDIS_URL", None)  # For Redis Cloud/Upstash

# Session configuration
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
SESSION_PREFIX = "session:"
USER_SESSION_PREFIX = "user_session:"
TOKEN_PREFIX = "token:"

# Initialize Redis client
redis_client = None

if REDIS_AVAILABLE:
    try:
        if REDIS_URL:
            redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        else:
            redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True
            )
        # Test connection
        redis_client.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("⚠️  Falling back to in-memory session storage")
        redis_client = None
else:
    print("⚠️  Redis not available, using in-memory fallback")

# Fallback in-memory storage
_memory_sessions: Dict[str, Dict[str, Any]] = {}


def _get_key(prefix: str, key: str) -> str:
    """Generate Redis key."""
    return f"{prefix}{key}"


def set_session(session_id: str, user_data: Dict[str, Any], timeout_minutes: int = None) -> bool:
    """
    Store session data in Redis.
    
    Args:
        session_id: Unique session identifier
        user_data: User data to store (user_id, email, role, etc.)
        timeout_minutes: Session timeout in minutes (defaults to SESSION_TIMEOUT_MINUTES)
    
    Returns:
        True if successful, False otherwise
    """
    timeout = timeout_minutes or SESSION_TIMEOUT_MINUTES
    expires_at = datetime.utcnow() + timedelta(minutes=timeout)
    
    session_data = {
        **user_data,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
        "last_activity": datetime.utcnow().isoformat(),
    }
    
    if redis_client:
        try:
            key = _get_key(SESSION_PREFIX, session_id)
            redis_client.setex(
                key,
                timeout * 60,  # Convert to seconds
                json.dumps(session_data)
            )
            
            # Also store user_id -> session_id mapping for tracking
            if "user_id" in user_data:
                user_key = _get_key(USER_SESSION_PREFIX, str(user_data["user_id"]))
                redis_client.setex(
                    user_key,
                    timeout * 60,
                    session_id
                )
            
            return True
        except Exception as e:
            print(f"Redis error: {e}")
            return False
    else:
        # Fallback to memory
        _memory_sessions[session_id] = session_data
        return True


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve session data from Redis.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Session data dict or None if not found/expired
    """
    if redis_client:
        try:
            key = _get_key(SESSION_PREFIX, session_id)
            data = redis_client.get(key)
            if data:
                session_data = json.loads(data)
                # Update last activity
                session_data["last_activity"] = datetime.utcnow().isoformat()
                redis_client.setex(
                    key,
                    SESSION_TIMEOUT_MINUTES * 60,
                    json.dumps(session_data)
                )
                return session_data
            return None
        except Exception as e:
            print(f"Redis error: {e}")
            return None
    else:
        # Fallback to memory
        return _memory_sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """
    Delete session from Redis.
    
    Args:
        session_id: Session identifier
    
    Returns:
        True if deleted, False otherwise
    """
    if redis_client:
        try:
            key = _get_key(SESSION_PREFIX, session_id)
            session_data = redis_client.get(key)
            
            if session_data:
                data = json.loads(session_data)
                # Also delete user mapping
                if "user_id" in data:
                    user_key = _get_key(USER_SESSION_PREFIX, str(data["user_id"]))
                    redis_client.delete(user_key)
            
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis error: {e}")
            return False
    else:
        # Fallback to memory
        if session_id in _memory_sessions:
            del _memory_sessions[session_id]
        return True


def refresh_session(session_id: str, timeout_minutes: int = None) -> bool:
    """
    Refresh session expiry time.
    
    Args:
        session_id: Session identifier
        timeout_minutes: New timeout (defaults to SESSION_TIMEOUT_MINUTES)
    
    Returns:
        True if refreshed, False otherwise
    """
    timeout = timeout_minutes or SESSION_TIMEOUT_MINUTES
    
    if redis_client:
        try:
            key = _get_key(SESSION_PREFIX, session_id)
            data = redis_client.get(key)
            if data:
                session_data = json.loads(data)
                session_data["last_activity"] = datetime.utcnow().isoformat()
                redis_client.setex(
                    key,
                    timeout * 60,
                    json.dumps(session_data)
                )
                return True
            return False
        except Exception as e:
            print(f"Redis error: {e}")
            return False
    else:
        # Fallback - just update timestamp
        if session_id in _memory_sessions:
            _memory_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
            return True
        return False


def get_user_sessions(user_id: str) -> list[str]:
    """
    Get all active session IDs for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        List of active session IDs
    """
    if redis_client:
        try:
            user_key = _get_key(USER_SESSION_PREFIX, str(user_id))
            session_id = redis_client.get(user_key)
            if session_id:
                # Verify session still exists
                if get_session(session_id):
                    return [session_id]
            return []
        except Exception as e:
            print(f"Redis error: {e}")
            return []
    else:
        # Fallback - find sessions in memory
        sessions = []
        for sid, data in _memory_sessions.items():
            if data.get("user_id") == user_id:
                sessions.append(sid)
        return sessions


def store_token(token: str, user_data: Dict[str, Any], expires_in_seconds: int) -> bool:
    """
    Store JWT token mapping in Redis for revocation tracking.
    
    Args:
        token: JWT token string
        user_data: User data
        expires_in_seconds: Token expiry time
    
    Returns:
        True if stored successfully
    """
    if redis_client:
        try:
            # Store token hash -> user_id mapping
            token_key = _get_key(TOKEN_PREFIX, token[:50])  # Use first 50 chars as key
            redis_client.setex(
                token_key,
                expires_in_seconds,
                json.dumps(user_data)
            )
            return True
        except Exception as e:
            print(f"Redis error: {e}")
            return False
    return True  # Not critical if Redis fails


def revoke_token(token: str) -> bool:
    """
    Revoke a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        True if revoked
    """
    if redis_client:
        try:
            token_key = _get_key(TOKEN_PREFIX, token[:50])
            redis_client.delete(token_key)
            return True
        except Exception as e:
            print(f"Redis error: {e}")
            return False
    return True


def is_token_revoked(token: str) -> bool:
    """
    Check if a token is revoked.
    
    Args:
        token: JWT token string
    
    Returns:
        True if token is revoked or doesn't exist
    """
    if redis_client:
        try:
            token_key = _get_key(TOKEN_PREFIX, token[:50])
            return redis_client.exists(token_key) == 0
        except Exception as e:
            print(f"Redis error: {e}")
            return False
    return False  # Can't check in memory fallback


def get_active_sessions_count() -> int:
    """
    Get count of active sessions.
    
    Returns:
        Number of active sessions
    """
    if redis_client:
        try:
            pattern = f"{SESSION_PREFIX}*"
            return len(redis_client.keys(pattern))
        except Exception as e:
            print(f"Redis error: {e}")
            return len(_memory_sessions)
    else:
        return len(_memory_sessions)







