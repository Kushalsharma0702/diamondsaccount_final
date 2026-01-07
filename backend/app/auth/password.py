"""Password hashing utilities."""
from passlib.context import CryptContext

# Configure bcrypt with 12 rounds (good balance of security and performance)
# Default can be 31 rounds which is extremely slow
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Explicitly set to 12 rounds (~0.3s per hash)
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
