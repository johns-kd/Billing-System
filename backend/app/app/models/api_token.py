from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class ApiTokens(Base):
    __tablename__ = "api_tokens"
    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    
    token = Column(String(100))
    created_at = Column(DateTime)
    renewed_at = Column(DateTime)
    device_type = Column(Integer)
    validity = Column(Integer)
    device_id = Column(String(255))
    push_device_id = Column(String(255))
    device_ip = Column(String(255))
    status = Column(Integer)
    user = relationship("User", back_populates="api_tokens")
