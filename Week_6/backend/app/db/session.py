from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL for local PostgreSQL on port 5464
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Test123@localhost:5464/spotify_clone")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 