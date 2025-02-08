from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(255))
    short_description = Column(String(255))
    product_code = Column(String(255))
    img_alt = Column(String(255))
    img_path = Column(String(255))
    tax_percentage = Column(Integer)
    gst_amount = Column(DECIMAL(15, 2))
    actual_price = Column(DECIMAL(15, 2))
    price = Column(DECIMAL(15, 2))
    available_quantity = Column(Integer)

    created_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Integer)

    user = relationship("User", back_populates="products")
    ordered_products = relationship("OrderedProducts", back_populates="products")


