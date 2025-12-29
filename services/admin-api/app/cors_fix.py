"""
Test CORS configuration
"""
import asyncio
from app.core.config import settings

cors_origins = settings.CORS_ORIGINS
print(f"Raw CORS_ORIGINS: {cors_origins}")
print(f"Type: {type(cors_origins)}")

if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]
elif not isinstance(cors_origins, list):
    cors_origins = list(cors_origins)

print(f"Processed CORS_ORIGINS: {cors_origins}")

