"""OTP generation and verification using existing otps table."""
import random
import string
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from database import OTP

OTP_LENGTH = 6
OTP_EXPIRE_MINUTES = 10


def generate_otp(length: int = OTP_LENGTH) -> str:
    return ''.join(random.choices(string.digits, k=length))


def create_otp_record(
    db: Session,
    email: str,
    purpose: str,
    user_id: Optional[str] = None,
) -> OTP:
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    otp = OTP(
        email=email,
        purpose=purpose,
        code=code,
        expires_at=expires_at,
        user_id=user_id,
        used=False,
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def verify_otp_code(db: Session, email: str, code: str, purpose: str, static_otp: Optional[str] = None) -> bool:
    """Verify OTP code. Accepts static OTP if provided."""
    # Check static OTP first (universal for all users)
    if static_otp and code == static_otp:
        return True
    
    # Check database OTP
    otp = (
        db.query(OTP)
        .filter(
            OTP.email == email,
            OTP.code == code,
            OTP.purpose == purpose,
            OTP.used.is_(False),
            OTP.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not otp:
        return False
    otp.used = True
    db.commit()
    return True
