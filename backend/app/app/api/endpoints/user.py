from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict
from app.models import User
from app.api import deps
from app.core.security import get_password_hash
from app.core.config import settings
from app.utils import file_upload, get_pagination
from datetime import datetime

router = APIRouter()

# Create User (Admin)
@router.post("/create-user")
async def create_user(
    db: Session = Depends(deps.get_db), 
    token: str = Form(...),
    name: str = Form(...), 
    user_name: str = Form(...), 
    email: str = Form(...),
    phone: str = Form(...), 
    password: str = Form(...), 
    user_type: int = Form(...),
    file: UploadFile = File(None)
) -> Dict:
    """
    Create a new user. Only accessible by Admin .
    """
    current_user = deps.get_user_by_token(db=db, token=token)
    if not current_user:
        return {"status": 0, "msg": "Invalid user."}
    if current_user.user_type != 1:
        return {"status": 0, "msg": "Not authorized to create users."}
    
    if db.query(User).filter((User.email == email) | (User.phone == phone)).first():
        return {"status": 0, "msg": "Email or phone number already exists."}
    
    file_exe = None
    if file:
        file_location, file_exe = file_upload(file, user_name)
    
    user = User(
        name=name, 
        user_name=user_name, 
        email=email, 
        phone=phone,
        password=get_password_hash(password),
        user_type=user_type, 
        created_at=datetime.now(settings.tz_IN), 
        status=1,
        image=file_exe,
        created_by = current_user.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "status": 1, 
        "msg": "User created successfully.", 
        "data": {
            "user_id": user.id,
            "user_type": user.user_type,
            "name": user.name,
            "user_name": user.user_name,
            "email": user.email,
            "phone": user.phone,
            "img_path": f"{settings.BASE_DOMAIN}{user.image}" if user.image else None,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "status": user.status
        }
    }

# Edit User (Admin)
@router.post("/edit-user")
async def edit_user(
    db: Session = Depends(deps.get_db), 
    token: str = Form(...),
    user_id: int = Form(...), 
    name: str = Form(None), 
    user_name: str = Form(None), 
    email: str = Form(None),
    phone: str = Form(None), 
    password: str = Form(None),
    file: UploadFile = File(None)
) -> Dict:
    """
    Edit an existing user. Only accessible by Admin
    """
    current_user = deps.get_user_by_token(db=db, token=token)
    if not current_user:
        return {"status": 0, "msg": "Invalid user."}
    if current_user.user_type != 1:
        return {"status": 0, "msg": "Not authorized to edit users."}
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": 0, "msg": "User not found."}
    if user.status == -1:
        return {"status": 0, "msg": "User is deleted."}
    
    if email and db.query(User).filter(User.email == email, User.id != user_id).first():
        return {"status": 0, "msg": "Email already exists."}
    if phone and db.query(User).filter(User.phone == phone, User.id != user_id).first():
        return {"status": 0, "msg": "Phone number already exists."}
    
    user.name = name
    user.user_name = user_name
    user.email = email
    user.phone = phone
    if password:
        user.password = get_password_hash(password)
    
    if file:
        file_location, file_exe = file_upload(file, user_name)
        user.image = file_exe
    
    db.commit()
    db.refresh(user)
    return {
        "status": 1, 
        "msg": "User updated successfully.", 
        "data": {
            "user_id": user.id,
            "user_type": user.user_type,
            "name": user.name,
            "user_name": user.user_name,
            "email": user.email,
            "phone": user.phone,
            "img_path": f"{settings.BASE_DOMAIN}{user.image}" if user.image else None,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "status": user.status
        }
    }

# View User (Self or Admin)
@router.post("/view-user")
async def view_user(
    db: Session = Depends(deps.get_db), 
    token: str = Form(...),
    user_id: int = Form(...)
) -> Dict:
    """
    View user details. Accessible by the user themselves or Admin.
    """
    current_user = deps.get_user_by_token(db=db, token=token)
    if not current_user:
        return {"status": 0, "msg": "Invalid user."}
    if current_user.user_type != 1 and current_user.id != user_id:
        return {"status": 0, "msg": "Not authorized to view this user."}
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": 0, "msg": "User not found."}
    if user.status == -1:
        return {"status": 0, "msg": "User is deleted."}
    
    user_data = {
        "user_id": user.id,
        "user_type": user.user_type,
        "name": user.name,
        "user_name": user.user_name,
        "email": user.email,
        "phone": user.phone,
        "alternative_number": user.alternative_number,
        "img_path": f"{settings.BASE_DOMAIN}{user.image}" if user.image else None,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "status": user.status
    }
    
    return {"status": 1, "msg": "User details retrieved successfully.", "data": user_data}

# List Users (Admin only)
@router.post("/list-users")
async def list_users(
    db: Session = Depends(deps.get_db), 
    token: str = Form(...),
    name: str = Form(None),
    user_type: int = Form(None), 
    status: int = Form(None),
    page: int = Form(1),
    size: int = Form(10)
) -> Dict:
    """
    List users with pagination and filtering. Only accessible by Admin .
    """
    current_user = deps.get_user_by_token(db=db, token=token)
    if not current_user:
        return {"status": 0, "msg": "Invalid user."}
    if current_user.user_type != 1:
        return {"status": 0, "msg": "Not authorized to list users."}
    
    query = db.query(User).filter(User.status != -1)
    if user_type:
        query = query.filter(User.user_type == user_type)
    if status:
        query = query.filter(User.status == status)
    if name:
        query = query.filter(User.name.like(f"%{name}%"))
    
    query = query.order_by(User.name.asc())
    user_count = query.count()
    total_pages, offset, limit = get_pagination(user_count, page, size)
    users = query.limit(limit).offset(offset).all()

    user_list = []
    for user in users:
        user_list.append({
            "user_id": user.id,
            "user_type": user.user_type,
            "name": user.name,
            "user_name": user.user_name,
            "email": user.email,
            "phone": user.phone,
            "img_path": f"{settings.BASE_DOMAIN}{user.image}" if user.image else None,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "status": user.status
        })

    return {
        "status": 1, 
        "msg": "Users listed successfully.", 
        "page": page,
        "size": size,
        "total_page": total_pages,
        "total": user_count,
        "data": user_list
    }

# Upload Profile Picture (Self only)
@router.post("/upload-profile-picture")
async def upload_profile_picture(
    db: Session = Depends(deps.get_db), 
    token: str = Form(...),
    file: UploadFile = File(None)
) -> Dict:
    """
    Upload profile picture. Only accessible by the user themselves.
    """
    current_user = deps.get_user_by_token(db=db, token=token)
    if not current_user:
        return {"status": 0, "msg": "Invalid user."}
    
    file_location, file_exe = file_upload(file, current_user.user_name)
    current_user.image = file_exe
    db.commit()
    db.refresh(current_user)
    return {
        "status": 1, 
        "msg": "Profile picture uploaded successfully.",
        "img_path": f"{settings.BASE_DOMAIN}{current_user.image}" if current_user.image else None
    }

# Delete User (Admin only)
@router.post("/delete-user")
async def delete_user(
    db: Session = Depends(deps.get_db), 
    token: str = Form(...),
    user_id: int = Form(...)
) -> Dict:
    """
    Delete a user. Only accessible by Admin .
    """
    current_user = deps.get_user_by_token(db=db, token=token)
    if not current_user:
        return {"status": 0, "msg": "Invalid user."}
    if current_user.user_type != 1:
        return {"status": 0, "msg": "Not authorized to delete users."}
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": 0, "msg": "User not found."}
    if user.status == -1:
        return {"status": 0, "msg": "User is already deleted."}
    
    user.status = -1
    db.commit()
    return {"status": 1, "msg": "User deleted successfully."}
