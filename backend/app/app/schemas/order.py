from typing import Optional, List
from pydantic import BaseModel

class ProductList(BaseModel):
    product_id: int
    quantity: int

class Denominations(BaseModel):
    amount: int
    count: int

class OrderCreate(BaseModel):
    token: Optional[str] = None
    email: Optional[str] = None
    paid_amount: Optional[float] = None
    denominations: List[Denominations]
    product_list: List[ProductList]

class DemoView(BaseModel):
    paid_amount: Optional[float] = None
    denominations: List[Denominations]
    product_list: List[ProductList]