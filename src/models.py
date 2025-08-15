from sqlalchemy import Column, Integer, String
from .main import Base  # NEW: Import Base from main.py so it shares the same metadata

# NEW: SQLAlchemy ORM model for the users table
class User(Base):
    __tablename__ = "users"  # MySQL table name

    id = Column(Integer, primary_key=True, index=True)   # Auto-increment primary key
    name = Column(String(255), unique=True, nullable=False)  # Username must be unique
    email = Column(String(255), unique=True, nullable=False) # Email must be unique
    password = Column(String(255), nullable=False)           # Hashed password
