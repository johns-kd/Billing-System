from fastapi import APIRouter, Depends, Form
from app.api import deps
from sqlalchemy.orm import Session
from app.schemas import *
from app.models import *
from utils import *

router = APIRouter()   

@router.post("/product-dropdown")
def product_dropdown(
    db: Session = Depends(deps.get_db),
    token: str = Form(None),
    product_id: int = Form(None),
    name: str = Form(None),      
    product_code: str = Form(None),                    
):
    get_all_product = db.query(Products).filter(Products.status == 1)
    user = None
    if token:
        user = deps.get_user_by_token(db=db, token=token)
        if not user:
            return {"status": -1, "msg": "Session Expires Please Login Again."}
        
    if not token or (user and user.user_type == 2):
        get_all_product = get_all_product.filter(Products.available_quantity>0)

    if product_id:
        get_all_product = get_all_product.filter(Products.id == product_id)

    if name:
        get_all_product = get_all_product.filter(Products.name.like('%' + name + '%'))
    if product_code:
        get_all_product = get_all_product.filter(Products.product_code == product_code)
    
    get_all_product = get_all_product.all()
    data_list = []
    for row in get_all_product:
        data_list.append({
            "id": row.id,
            "product_code": row.product_code,
            "name": row.name,
            "status": row.status,
            "available_qty": row.available_quantity if row.available_quantity else 0,
        })
    print(data_list)
    return {"status": 1, "msg": "Success", "data": data_list}
