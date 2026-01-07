"""
Startup Validation for Tax-Ease API v2

CRITICAL: Application MUST NOT start if any check fails.
This prevents insecure or misconfigured deployments.

These checks enforce INV-A013, INV-A014, REDIS-001.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
import redis
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from backend.app.services.state_machine import verify_state_machine_completeness


def validate_jwt_secret() -> None:
    """
    Validate JWT secret is strong enough.
    
    RULE: JWT_SECRET must be at least 32 characters.
    
    Raises: SystemExit if invalid
    """
    jwt_secret = os.getenv("JWT_SECRET", "")
    
    if not jwt_secret or jwt_secret == "your-secret-key-min-32-chars-long":
        print("❌ FATAL: JWT_SECRET is not set or using default value")
        print("   Set JWT_SECRET environment variable to a strong random string (min 32 chars)")
        sys.exit(1)
    
    if len(jwt_secret) < 32:
        print(f"❌ FATAL: JWT_SECRET is too short ({len(jwt_secret)} chars, minimum 32 required)")
        print("   Generate a strong secret: openssl rand -hex 32")
        sys.exit(1)
    
    print(f"✅ JWT_SECRET validated (length: {len(jwt_secret)} chars)")


def validate_encryption_key() -> None:
    """
    Validate file encryption key.
    
    RULE: ENCRYPTION_KEY or FILE_ENCRYPTION_KEY must be set and >= 32 bytes.
    
    Raises: SystemExit if invalid
    """
    key = os.getenv("ENCRYPTION_KEY") or os.getenv("FILE_ENCRYPTION_KEY")
    
    if not key:
        print("❌ FATAL: ENCRYPTION_KEY or FILE_ENCRYPTION_KEY not set")
        print("   Set ENCRYPTION_KEY environment variable for file encryption")
        sys.exit(1)
    
    if len(key.encode()) < 32:
        print(f"❌ FATAL: Encryption key too short ({len(key.encode())} bytes, minimum 32 required)")
        sys.exit(1)
    
    print(f"✅ Encryption key validated (length: {len(key.encode())} bytes)")


def validate_redis_connection() -> None:
    """
    Validate Redis is available and responsive.
    
    RULE: Redis MUST be available for authentication to work.
    Application cannot start without Redis.
    
    Raises: SystemExit if Redis unavailable
    """
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    
    try:
        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=5,
            socket_timeout=5,
            decode_responses=True
        )
        
        # Test connection
        response = client.ping()
        if not response:
            raise Exception("Redis PING failed")
        
        # Test set/get
        test_key = "__startup_test__"
        client.setex(test_key, 10, "test")
        value = client.get(test_key)
        client.delete(test_key)
        
        if value != "test":
            raise Exception("Redis set/get test failed")
        
        print(f"✅ Redis connection validated ({redis_host}:{redis_port})")
        
    except redis.RedisError as e:
        print(f"❌ FATAL: Redis connection failed: {e}")
        print(f"   Host: {redis_host}:{redis_port}")
        print("   Redis is REQUIRED for authentication (token blacklist, OTP storage, rate limiting)")
        print("   Start Redis: redis-server")
        sys.exit(1)
    except Exception as e:
        print(f"❌ FATAL: Redis validation failed: {e}")
        sys.exit(1)


def validate_database_connection() -> None:
    """
    Validate PostgreSQL database is available.
    
    Raises: SystemExit if database unavailable
    """
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        # Construct from components
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "CA_Project")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "")
        
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Convert async URL to sync URL for testing
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")
    
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row[0] != 1:
                raise Exception("Database query test failed")
        
        print(f"✅ Database connection validated")
        
    except Exception as e:
        print(f"❌ FATAL: Database connection failed: {e}")
        print("   Check DATABASE_URL or DB_* environment variables")
        sys.exit(1)


def validate_storage_path() -> None:
    """
    Validate storage path exists and is writable.
    
    RULE: STORAGE_PATH must exist and be writable for document encryption.
    
    Raises: SystemExit if storage path invalid
    """
    storage_path = os.getenv("STORAGE_PATH", "./storage/uploads")
    
    # Convert to absolute path
    storage_path = os.path.abspath(storage_path)
    
    # Create if doesn't exist
    try:
        Path(storage_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ FATAL: Cannot create storage directory: {e}")
        print(f"   Path: {storage_path}")
        sys.exit(1)
    
    # Test writability
    test_file = Path(storage_path) / "__startup_test__.tmp"
    try:
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        print(f"❌ FATAL: Storage directory not writable: {e}")
        print(f"   Path: {storage_path}")
        sys.exit(1)
    
    print(f"✅ Storage path validated ({storage_path})")


def validate_state_machines() -> None:
    """
    Validate state machine definitions are complete.
    
    RULE: State machines must be correctly defined.
    
    Raises: SystemExit if state machines invalid
    """
    try:
        verify_state_machine_completeness()
        print("✅ State machines validated")
    except Exception as e:
        print(f"❌ FATAL: State machine validation failed: {e}")
        sys.exit(1)


def validate_environment() -> None:
    """
    Validate critical environment variables are set.
    
    Raises: SystemExit if any required variable missing
    """
    required_vars = [
        "JWT_SECRET",
        "DB_NAME",
        "DB_USER",
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ FATAL: Required environment variables not set: {', '.join(missing)}")
        print("   Create .env file with all required variables")
        sys.exit(1)
    
    print("✅ Required environment variables validated")


def run_all_startup_checks() -> None:
    """
    Run all startup validation checks.
    
    This function is called from main.py during application startup.
    If ANY check fails, the application will NOT start.
    
    This enforces:
    - INV-A013: redis.ping() = false → application.startup = FAIL
    - INV-A014: JWT_SECRET.length < 32 → application.startup = FAIL
    - REDIS-001: Application cannot start without Redis
    """
    print("\n" + "="*70)
    print("🔒 TAX-EASE API V2 - STARTUP VALIDATION")
    print("="*70 + "\n")
    
    print("Running startup checks...")
    print("-" * 70)
    
    try:
        validate_environment()
        validate_jwt_secret()
        validate_encryption_key()
        validate_redis_connection()
        validate_database_connection()
        validate_storage_path()
        validate_state_machines()
        
        print("-" * 70)
        print("\n✅ All startup checks passed")
        print("🚀 Application is ready to start\n")
        print("="*70 + "\n")
        
    except SystemExit:
        print("-" * 70)
        print("\n❌ Startup validation FAILED")
        print("🛑 Application will NOT start")
        print("\nFix the errors above and try again.\n")
        print("="*70 + "\n")
        raise


# ============================================================================
# RUNTIME HEALTH CHECKS
# ============================================================================

def check_redis_health() -> tuple[bool, Optional[str]]:
    """
    Check Redis health during runtime.
    
    Returns: (is_healthy, error_message)
    """
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    
    try:
        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=2,
            socket_timeout=2,
            decode_responses=True
        )
        
        response = client.ping()
        if not response:
            return False, "Redis PING failed"
        
        return True, None
        
    except Exception as e:
        return False, str(e)


def check_database_health() -> tuple[bool, Optional[str]]:
    """
    Check database health during runtime.
    
    Returns: (is_healthy, error_message)
    """
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "CA_Project")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "")
        
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    # Allow running startup checks independently
    run_all_startup_checks()
