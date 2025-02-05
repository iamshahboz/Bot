from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

# Define base class for declarative models
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float)
    image = Column(String)  # Store image file_id as a string
    barcode = Column(String, unique=True)

    def __repr__(self):
        return f"<Product(name={self.name}, barcode={self.barcode})>"
