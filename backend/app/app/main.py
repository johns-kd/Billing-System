from fastapi import FastAPI, Request, status
from starlette.middleware.cors import CORSMiddleware
import sys
sys.path.append('../')
from app.api.api import api_router
from app.core.config import settings
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    docs_url=settings.API_DOC_PATH,
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# import logging

# logging.basicConfig(level=logging.DEBUG)
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     # Read and log the request body
#     body = await request.body()
#     logging.debug(f"Incoming request payload: {body.decode('utf-8')}")
    
#     # Recreate the body for further processing
#     async def receive_body():
#         return {"type": "http.request", "body": body}

#     request._receive = receive_body
#     response = await call_next(request)
#     return response
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content=jsonable_encoder({"detail": exc.errors()}),
#     )

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)