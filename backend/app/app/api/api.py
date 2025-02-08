from fastapi import APIRouter
from .endpoints import authentication, user,product,order,dropdown

api_router = APIRouter()

api_router.include_router(authentication.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(product.router, prefix="/product", tags=["Product"])
api_router.include_router(order.router, prefix="/order", tags=["Order"])
api_router.include_router(dropdown.router, prefix="/dropdown", tags=["Dropdown"])