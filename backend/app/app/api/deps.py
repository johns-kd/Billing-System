from typing import Generator, Any, Optional
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models
import random
from sqlalchemy import or_
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from datetime import datetime, timedelta
import hashlib
from app.models import ApiTokens, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_user_by_token(db: Session, *, token: str) -> Optional[User]:
    api_token = db.query(ApiTokens).filter(
        ApiTokens.token == token, ApiTokens.status == 1
    ).first()
    if api_token:
        return db.query(User).filter(
            User.id == api_token.user_id, User.status == 1
        ).first()
    return None

def get_user_by_username(db: Session, *, username: str) -> Optional[User]:
    return db.query(models.User).filter(
        models.User.user_name == username, models.User.status == 1
    ).first()

def authenticate_user(db: Session, *, username: str, password: str,
                      auth_code: str, auth_text: str) -> Optional[User]:
    user = get_user_by_username(db, username=username)
    if not user or not user.password:
        return None
    if not security.check_authcode(auth_code, auth_text):
        return None
    if not security.verify_password(password, user.password):
        return None
    return user

def get_user_type(user_type: Any) -> str:
    if user_type == 1:
        return "Admin"
    elif user_type == 2:
        return "Customer"
    return ""

def verify_hash(hash_data: str, included_variable: str) -> bool:
    included_variable = (included_variable + settings.SALT_KEY).encode("utf-8")
    real_hash = hashlib.sha1(included_variable).hexdigest()
    return hash_data == real_hash

def check_signature(signature: str, timestamp: str, device_id: str) -> bool:
    included_variable = (device_id + timestamp + settings.SALT_KEY).encode("utf-8")
    real_hash = hashlib.sha1(included_variable).hexdigest()
    return signature == real_hash

def generate_otp() -> tuple:
    otp = random.randint(111111, 999999)
    reset_key = ''.join(random.choices(
        'qwertyuioplkjhgfdsazxcvbnm0123456789QWERTYUIOPLKJHGFDSAZXCVBNM', k=20
    ))
    created_at = datetime.now(settings.tz_IN)
    expire_time = created_at + timedelta(seconds=300)
    expire_at = expire_time.strftime("%Y-%m-%d %H:%M:%S")
    otp_valid_upto = expire_time.strftime("%d-%m-%Y %I:%M %p")
    return otp, reset_key, created_at, expire_time, expire_at, otp_valid_upto

def hms_to_seconds(time_str: str) -> int:
    return sum(int(unit) * 60 ** index for index, unit in enumerate(reversed(time_str.split(':'))))

