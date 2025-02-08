from fastapi import APIRouter, Depends, Form, File, UploadFile
from app.api import deps
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import *
from datetime import datetime
from utils import *
from app.api.deps import *

router = APIRouter()

@router.post("/add-product")
def add_product(
    *, db: Session = Depends(deps.get_db),
    token: str = Form(...),
    tax_percentage: int = Form(...),
    available_quantity: int = Form(...),
    name: str = Form(...),
    product_code: str = Form(...),
    short_description: str = Form(None),
    img_alt: str = Form(None),
    actual_price: float = Form(...),
    price: float = Form(...),
    img_path: UploadFile = File(None),
):
    user = deps.get_user_by_token(db=db, token=token)
    if user and user.user_type == 1:        
        check_title = db.query(Products).filter(
            Products.name == name, Products.status != -1
        ).first()
        if check_title:
            return {"status": 0, "msg": "The Product Name is already available"}
        
        check_title = db.query(Products).filter(
            Products.product_code == product_code, Products.status != -1
        ).first()
        if check_title:
            return {"status": 0, "msg": "The Product Code is already available"}
        
        if img_path:
            full_file, store_file = file_upload(img_path)
            store_img_path = store_file

        add_data = Products(
            name=name,
            price=price,
            product_code=product_code,
            short_description=short_description,
            available_quantity=available_quantity,
            actual_price=actual_price,
            tax_percentage=tax_percentage,
            img_path=store_img_path if img_path else None,
            img_alt=img_alt,
            created_by=user.id,
            created_at=datetime.now(tz=settings.tz_IN),
            status=1,
        )
        db.add(add_data)
        db.commit()
        
        return {"status": 1, "msg": "Successfully new Product Added"}
    else:
        return {"status": -1, "msg": "Login Session Expired..."}

@router.post("/edit-product")
def edit_product(
    *, db: Session = Depends(deps.get_db),
    token: str = Form(...),
    product_id: int = Form(...),
    name: str = Form(...),
    product_code: str = Form(...),
    short_description: str = Form(None),
    available_quantity: str = Form(None),
    actual_price: str = Form(None),
    price: float = Form(...),
    tax_percentage: int = Form(...),
    img_path: UploadFile = File(None),
    img_alt: str = Form(None),
):
    user = deps.get_user_by_token(db=db, token=token)
    if user:      
        if user.user_type != 1:
            return {"status": -1, "msg": "You are not authorized to Edit Product"}
        get_product = db.query(Products).filter(
            Products.status != -1, Products.id == product_id
        ).first()
        if get_product:  
            check_title = db.query(Products).filter(
                Products.name == name, Products.status != -1, Products.id != get_product.id
            ).first()
            if check_title:
                return {"status": 0, "msg": "The Product Name is already available"}
            
            check_title = db.query(Products).filter(
                Products.product_code == product_code, Products.status != -1, Products.id != get_product.id
            ).first()
            if check_title:
                return {"status": 0, "msg": "The Product Code is already available"}
            
            if img_path:
                full_file, store_file = file_upload(img_path)
                store_img_path = store_file

            get_product.name = name
            get_product.price = price
            get_product.product_code = product_code
            get_product.short_description = short_description
            get_product.available_quantity = available_quantity
            get_product.actual_price = actual_price
            get_product.tax_percentage = tax_percentage
            if img_path:
                get_product.img_path = store_img_path
            get_product.img_alt = img_alt

            get_product.updated_at = datetime.now(tz=settings.tz_IN)
            
            db.commit()
                
            return {"status": 1, "msg": "Successfully Product Updated."}
        else:
            return {"status": 0, "msg": "Product Not Found"}
    else:
        return {"status": -1, "msg": "Login Session Expired..."}

@router.post("/change-product-status")
def change_product_status(
    *, db: Session = Depends(deps.get_db),
    product_id: int = Form(...),
    token: str = Form(...),
    status: int = Form(..., description="0->inactive,1->active,-1->delete")
):
    user = deps.get_user_by_token(db=db, token=token)
    if user:        
        if user.user_type != 1:
            return {"status": -1, "msg": "You are not authorized to Change Product Status"}
        get_product = db.query(Products).filter(
            Products.id == product_id, Products.status != -1
        ).first()
        if get_product:
            if status != -1:
                get_product.status = status
            else:
                get_product.status = status
                    
            db.commit()
            
            return {"status": 1, "msg": "success"}
        else:
            return {"status": 0, "msg": "Not Found"}            
    else:
        return {"status": -1, "msg": "Login Session Expired..."}

@router.post("/delete-product")
def delete_product(
    *, db: Session = Depends(deps.get_db),
    token: str = Form(...),
    product_id: int = Form(...),
):
    user = deps.get_user_by_token(db=db, token=token)
    if user:        
        get_product = db.query(Products).filter(
            Products.id == product_id, Products.status != -1
        ).first()
        if get_product:
            get_product.status = -1
            db.commit()
            return {"status": 1, "msg": "success"}
        else:
            return {"status": 0, "msg": "Not Found"}
    else:
        return {"status": -1, "msg": "Login Session Expired..."}

@router.post("/list-products")
def list_products(
    *, db: Session = Depends(deps.get_db),
    token: str = Form(None),
    product_name: str = Form(None),
    product_code: str = Form(None),
    page: int = 1, size: int = 10,
    min_price: int = Form(None),
    max_price: int = Form(None),
    order_type: int = Form(None, description="1-A-z,2 Z-A,3-Low to high ,4-high to Low")
):
    get_product = db.query(Products)    
    if token:
        user = deps.get_user_by_token(db=db, token=token)
        if not user:    
            return {"status": -1, "msg": "Login Session Expired..."}
            
        if user.user_type == 1:
            get_product = get_product.filter(Products.status != -1)
    else:
        get_product = get_product.filter(Products.status == 1)
    if product_name:
        get_product = get_product.filter(Products.name.like('%' + product_name + '%'))
    
    if product_code:
        get_product = get_product.filter(Products.product_code.like('%' + product_code + '%'))
    
    if min_price:
        get_product = get_product.filter(Products.price >= min_price)
    
    if max_price:
        get_product = get_product.filter(Products.price < max_price)
    
    get_product = get_product.distinct(Products.id)
    count = get_product.count()

    total_pages, offset, limit = get_pagination(
        row_count=count, current_page_no=page, default_page_size=size
    )
    
    if order_type == 1:
        get_product = get_product.order_by(Products.name.asc())
    if order_type == 2:
        get_product = get_product.order_by(Products.name.desc())
    if order_type == 3:
        get_product = get_product.order_by(Products.price.asc())
    if order_type == 4:
        get_product = get_product.order_by(Products.price.desc())

    get_product = get_product.limit(limit).offset(offset)
    get_product = get_product.all()

    data_lt = []

    if get_product:
        for each_data in get_product:
            data_lt.append({
                "id": each_data.id,
                "name": each_data.name,
                "price": each_data.price,
                "short_description": each_data.short_description,
                "actual_price": each_data.actual_price,
                "available_quantity": each_data.available_quantity,
                "tax_percentage": each_data.tax_percentage,
                "img_path": f"{settings.BASE_DOMAIN}{each_data.img_path}" if each_data.img_path else None,
                "img_alt": each_data.img_alt,
                "created_by": each_data.created_by,
                "created_at": each_data.created_at,
                "updated_at": each_data.updated_at,
                "status": each_data.status,
            })
    return {
        "status": 1, "msg": "success",
        "items": data_lt,
        "total": count,
        "total_page": total_pages,
        "page": page, "size": size
    }

@router.post("/view-products")
def view_products(
    *, db: Session = Depends(deps.get_db),
    token: str = Form(None),
    product_id: int = Form(...),
):
    get_product = db.query(Products).filter(Products.id == product_id)    
    
    if token:
        user = deps.get_user_by_token(db=db, token=token)
        if user:    
            pass
        else:
            return {"status": -1, "msg": "Login Session Expired..."}
        
        if user.user_type == 1 or user.user_type == 2:
            get_product = get_product.filter(Products.status != -1)
        else:
            get_product = get_product.filter(Products.status == 1)
    else:
        get_product = get_product.filter(Products.status == 1)
        
    get_product = get_product.first()
    
    data = {}
    if get_product:
        data = {
            "id": get_product.id,
            "name": get_product.name,
            "product_code": get_product.product_code,
            "short_description": get_product.short_description,
            "available_quantity": get_product.available_quantity,
            "actual_price": get_product.actual_price,
            "price": get_product.price,
            "tax_percentage": get_product.tax_percentage,
            "img_path": f"{settings.BASE_DOMAIN}{get_product.img_path}" if get_product.img_path else None,
            "img_alt": get_product.img_alt,
            "created_by": get_product.created_by,
            "created_by_name": get_product.user.user_name if get_product.created_by else None,
            "created_at": get_product.created_at,
            "updated_at": get_product.updated_at,
            "status": get_product.status,
        }
  
    return {
        "status": 1, "msg": "success",
        "data": data
    }


