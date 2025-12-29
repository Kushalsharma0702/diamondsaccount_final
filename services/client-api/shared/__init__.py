"""
Shared configuration and utilities for TaxEase microservices
"""

from .database import Database
from .auth import JWTManager, get_current_user
from .models import *
from .schemas import *
from .utils import *

__all__ = [
    "Database",
    "JWTManager", 
    "get_current_user"
]
