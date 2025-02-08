from typing import Any, Dict, List, Optional, TypeVar, Generic, ClassVar
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
from fastapi import Query
from fastapi_pagination.default import Page as BasePage, Params as BaseParams
import pytz 

T = TypeVar("T")

class Params(BaseParams):
    size: int = Query(500, gt=0, le=1000, description="Page size")

class Page(BasePage[T], Generic[T]):
    __params_type__ = Params

# Local configuration
base_domain = "http://192.168.1.214"
base_url = "http://192.168.1.214"
base_dir = "/local_uploads"
base_domain_url = ""
base_url_segment = "/billing-api"    
base_upload_folder = "/var/www/html"
# data_base = "mysql+pymysql://root:W3solutions@localhost/billing_system"
data_base = "sqlite:///billing_system.db"

api_doc_path = "/docs"

class Settings(BaseSettings):
    API_V1_STR: str = base_url_segment
    BASE_UPLOAD_FOLDER: str = base_upload_folder
    BASEURL: str = base_url
    BASE_DIR :str= base_dir
    SALT_KEY: str = "AaH0322A@B&H@R!!akLLo012VSzXycAA1"
    FROM_MAIL: str = "johnsonkoilraj53@gmail.com"
    APP_PASSWORD: str = "lagw zeio emgs dajt"
    SECRET_KEY: str = ""
    DATA_BASE: str = data_base
    BASE_DOMAIN: str = base_domain
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BASE_DOMAIN_URL: str = base_domain_url
    API_DOC_PATH: str = api_doc_path
    otp_resend_remaining_sec: int = 120
    tz_IN: ClassVar = pytz.timezone('Asia/Kolkata')  
    SERVER_NAME: str = "Python Template"
    ROOT_SERVER_BASE_URL: str = ""
    SERVER_HOST: AnyHttpUrl = "http://localhost:8002"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:8000",
        "http://localhost:8002",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://cbe.themaestro.in",
        "http://cbe.themaestro.in",
    ]       
    
    PROJECT_NAME: str = "Billing System"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return data_base

settings = Settings()