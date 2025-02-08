from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, DECIMAL
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class OrderTotal(Base):
    __tablename__ = "order_total"
    id = Column(Integer, primary_key=True,autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    code = Column(String(255))
    title = Column(String(255))
    count = Column(Integer)
    value = Column(DECIMAL(10, 2))
    amount_type = Column(Integer)#1-order amount, 2-denomination
    sort_order = Column(Integer)
    updated_at = Column(DateTime)
    status = Column(Integer)

    orders = relationship("Orders", back_populates="order_total")

