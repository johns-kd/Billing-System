from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, DECIMAL
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class OrderedProducts(Base):
    __tablename__ = "ordered_products"
    id = Column(Integer, primary_key=True,autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(10, 2))
    total_price = Column(DECIMAL(10, 2))
    gst_percent = Column(DECIMAL(10, 2))
    gst_amount = Column(DECIMAL(10, 2))
    status = Column(Integer)#, comment="1-active, 0 ->inactive, -1 -> deleted", 

    orders = relationship("Orders", back_populates="ordered_products")
    products = relationship("Products", back_populates="ordered_products")


