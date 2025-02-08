from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True,autoincrement=True)
    order_no = Column(Integer)
    paid_amount = Column(DECIMAL(15, 2))
    balance_amount = Column(DECIMAL(15, 2))
    invoice_path = Column(String(5000))
    email_id = Column(String(255))
    total_amount = Column(DECIMAL(10, 2))
    created_at = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("user.id"))
    status = Column(Integer)#, comment="1 -> Active, 0 -> Inactive, -1 -> Deleted, 2 -> Pending"

    user = relationship("User", back_populates="orders")
    ordered_products = relationship("OrderedProducts", back_populates="orders")
    order_total = relationship("OrderTotal", back_populates="orders")










