from sqlalchemy import Column, Integer, String, Float, Text
from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    image = Column(String, nullable=True)
    external_id = Column(Integer, unique=True, nullable=True)  # For synced products
