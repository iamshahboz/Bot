from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Database URL (SQLite in this case)
DATABASE_URL = 'sqlite:///products.db'  # SQLite database file

# Create engine and sessionmaker
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create tables (if not already created)
Base.metadata.create_all(engine)

# Function to get a new session
def get_session():
    return Session()
