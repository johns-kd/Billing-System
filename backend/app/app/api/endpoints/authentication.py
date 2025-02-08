from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import ApiTokens, User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from datetime import datetime
from app.utils import send_mail
from sqlalchemy import or_
import random

router = APIRouter()

# Check Token
@router.post("/check-token")
async def check_token(
    *, db: Session = Depends(deps.get_db), 
    token: str = Form(...)
):
    """
    Check if the provided token is valid.
    """
    check_token = db.query(ApiTokens).filter(ApiTokens.token == token, ApiTokens.status == 1).first()
    if check_token:
        return {"status": 1, "msg": "Token is valid."}
    return {"status": 0, "msg": "Token is invalid or expired."}

# Login
@router.post("/login")
async def login(
    *, 
    db: Session = Depends(deps.get_db), 
    auth_code: str = Form(None),
    user_name: str = Form(...), 
    password: str = Form(...),
    device_id: str = Form(None), 
    device_type: str = Form(..., description="1-android,2-ios"), 
    push_id: str = Form(None),
    ip: str = Form(None), 
):
    """
    User login endpoint.
    """
    auth_text = device_id + str(user_name) if device_id else user_name
    user = deps.authenticate_user(db, username=user_name, password=password, auth_code=auth_code, 
                                  auth_text=auth_text)

    if not user:
        return {"status": 0, "msg": "Invalid username or password."}
  
    key = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                                    k=30))
    db.query(ApiTokens).filter(ApiTokens.user_id == user.id).update({'status': 0})
    add_token = ApiTokens(
        user_id=user.id, 
        token=key,
        created_at=datetime.now(settings.tz_IN),
        renewed_at=datetime.now(settings.tz_IN),
        validity=1, 
        device_type=device_type,
        device_id=device_id, 
        push_device_id=push_id,
        device_ip=ip, 
        status=1
    )
    db.add(add_token)
    db.commit()

    return {
            'status': 1, 
            'token': key, 
            'msg': 'Successfully logged in.',
            'user_type': user.user_type, 
            'user_id': user.id,
            'user_name': user.name, 
            "verify_status": user.otp_verified_status,
            "duration": 120
        }

# Logout
@router.post("/logout")
async def logout(db: Session = Depends(deps.get_db), token: str = Form(...)):
    """
    User logout endpoint.
    """
    user = deps.get_user_by_token(db=db, token=token)
    if not user:
        return {"status": 0, "msg": "Invalid user."}

    check_token = db.query(ApiTokens).\
        filter(ApiTokens.token == token, ApiTokens.status == 1).first()
    
    if check_token:
        check_token.status = -1
        db.commit()
        return {"status": 1, "msg": "Successfully logged out."}
    return {"status": 0, "msg": "Token is invalid or already logged out."}

# OTP Verification
@router.post("/otp-verification")
async def otp_verification(
    *, 
    db: Session = Depends(deps.get_db), 
    otp: str = Form(...),
    reset_key: str = Form(...), 
    verification_type: str = Form(None, description="1->credentials")
):
    """
    OTP verification endpoint.
    """
    check_user = db.query(User).filter(User.status == 1, User.reset_key == reset_key).first()
    if not check_user:
        return {"status": 0, "msg": "No user found."}

    if otp != check_user.otp:
        return {"status": 0, "msg": "OTP does not match."}

    if check_user.otp_verified_at > datetime.now():
        return {"status": 0, "msg": "OTP has expired."}

    check_user.otp_verified_status = 1
    check_user.reset_key = None
    check_user.otp = None
    db.commit()

    if verification_type != str(2):
        msg = (
            "Subject: Welcome\n\nYou are verified."
            if not verification_type
            else f"Subject: Welcome Back\n\nYour username is: {check_user.name}"
        )
        try:
            await send_mail(receiver_email=check_user.email, message=msg)
        except:
            return {"status": 0, "msg": "Cannot connect to server. Try later."}

    return {"status": 1, "msg": "Credentials sent to your email or mobile number."}

# Change Password
@router.post("/change-password")
async def change_password(
    db: Session = Depends(deps.get_db), 
    token: str = Form(...),
    old_password: str = Form(None), 
    new_password: str = Form(...),
    repeat_password: str = Form(...)
):
    """
    Change password endpoint.
    """
    user = deps.get_user_by_token(db=db, token=token)
    if not user:
        return {"status": 0, "msg": "Invalid user."}

    if not verify_password(old_password, user.password):
        return {"status": 0, "msg": "Current password is incorrect."}

    if new_password != repeat_password:
        return {"status": 0, "msg": "New password and repeat password do not match."}

    user.password = get_password_hash(new_password)
    db.commit()
    return {"status": 1, "msg": "Password successfully updated."}

# Resend OTP
@router.post("/resend-otp")
async def resend_otp(db: Session = Depends(deps.get_db), reset_key: str = Form(...)):
    """
    Resend OTP endpoint.
    """
    get_user = db.query(User).filter(User.reset_key == reset_key, User.status == 1).first()
    if not get_user:
        return {"status": 0, "msg": "User not found."}

    otp, reset, created_at, expire_time, expire_at, otp_valid_upto = deps.generate_otp()
    reset_key = reset + "@ghgkhdfkjh@trhghgu"
    otp = "123456"
    get_user.otp = otp
    get_user.reset_key = reset_key
    get_user.otp_expire_at = expire_at
    db.commit()
    msg = f"Thanks for choosing our service. Your six-digit OTP is {otp}."
    try:
        await send_mail(receiver_email=get_user.email, message=msg)
        return {
            "status": 1, 
            "msg": "OTP sent to your email.", 
            "reset_key": reset_key,
            "expire_at": expire_at, 
            "otp": otp
        }
    except:
        return {"status": 0, "msg": "Invalid email address."}

# Forgot Password
@router.post('/forgot-password')
async def forgot_password(db: Session = Depends(deps.get_db), email: str = Form(None)):
    """
    Forgot password endpoint.
    """
    user = db.query(User).filter(
        User.user_type == 1, 
        or_(User.email == email, User.phone == email, User.alternative_number == email),
        User.status == 1
    ).first()
    if not user:
        return {'status': 0, 'msg': 'Account not found.'}

    if not user.email:
        return {'status': 0,
                 'msg': "Email address not found. Contact administrator for assistance."}

    otp, reset, created_at, expire_time, expire_at, otp_valid_upto = deps.generate_otp()
    otp = "123456"
    message = f"Your OTP for resetting the password is: {otp}"
    reset_key = f'{reset}{user.id}DTEKRNSSHPT'
    user.otp = otp
    user.reset_key = reset_key
    user.otp_expire_at = expire_at
    db.commit()
    try:
        await send_mail(receiver_email=user.email, message=message)
        return {
            'status': 1, 
            'reset_key': reset_key,
            'msg': f'An OTP has been sent to {user.email}.',
            'remaining_seconds': otp_valid_upto
        }
    except Exception as e:
        print("EXCEPTION:", e)
        return {'status': 0, 'msg': 'Unable to send the email.'}

