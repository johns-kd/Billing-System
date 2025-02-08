from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True,autoincrement=True)
    user_type = Column(Integer)#1->Admin, 2->Customer
    name = Column(String(200))
    user_name = Column(String(200))
    email = Column(String(255))
    phone = Column(String(20))
    alternative_number = Column(String(20))
    password = Column(String(255))
    image = Column(String(255))
    otp = Column(String(20))
    otp_expire_at = Column(DateTime)
    otp_verified_status = Column(Integer)
    otp_verified_at = Column(DateTime)
    reset_key = Column(String(255))
    created_by = Column(Integer, ForeignKey("user.id"), 
                      )
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Integer)

    api_tokens = relationship("ApiTokens", back_populates="user")
    products = relationship("Products", back_populates="user")
    orders = relationship("Orders", back_populates="user")
    creator = relationship("User", remote_side=[id], foreign_keys=[created_by], 
                           backref="created_users")



