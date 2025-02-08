from datetime import datetime, timedelta
from typing import Any, Union
from passlib.context import CryptContext
from app.core.config import settings
from jose import jwt
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def get_password_hash(password:str):

    return hashlib.sha1(password.encode("utf-8")).hexdigest()

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, password: str):
    hash_password = hashlib.sha1(plain_password.encode("utf-8")).hexdigest()

    if hash_password == password:
        return True
    else:
        return False

def check_authcode(authcode: str, auth_text: str) -> Union[bool, None]:
    """
    Check if the given authcode matches the hashed auth_text.
    """
    salt = settings.SALT_KEY
    auth_text = salt + auth_text
    result = hashlib.sha1(auth_text.encode())
    
    if authcode == result.hexdigest():
        return True
    return None