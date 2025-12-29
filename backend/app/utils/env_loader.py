"""
Centralized environment variable loader.
All services should use this to load from the project root .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Find project root (where .env file is located)
# This file is at: backend/app/utils/env_loader.py
# Project root is 3 levels up
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables from centralized .env file
_loaded = False

def load_env():
    """Load environment variables from centralized .env file."""
    global _loaded
    if not _loaded:
        if ENV_FILE.exists():
            load_dotenv(dotenv_path=ENV_FILE, override=False)
            _loaded = True
        else:
            print(f"Warning: .env file not found at {ENV_FILE}")
    return _loaded

def get_env(key: str, default: str = None) -> str:
    """Get environment variable with fallback to default."""
    load_env()
    return os.getenv(key, default)

# Auto-load on import
load_env()
