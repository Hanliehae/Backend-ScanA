from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
STORAGE_HAND_PATH = os.getenv("STORAGE_HAND_PATH", "src/storage/hands/")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
