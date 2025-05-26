from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
STORAGE_HAND_PATH = os.getenv("STORAGE_HAND_PATH", "src/storage/hands/")

# Create storage directories if they don't exist
os.makedirs("src/storage/hands", exist_ok=True)
os.makedirs("src/storage/uploads", exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Increase pool size
    max_overflow=30,  # Increase max overflow
    pool_timeout=60,  # Increase timeout to 60 seconds
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True  # Enable connection health checks
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
