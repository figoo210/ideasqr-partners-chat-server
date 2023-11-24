from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from passlib.context import CryptContext
from databases import Database
from dotenv import load_dotenv
import os

load_dotenv()

# Auth
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Database
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@localhost:3306/PartnersChatAppDB"

database = Database(SQLALCHEMY_DATABASE_URL)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=900,           # Increase pool_size for more concurrent connections
    max_overflow=100,        # Allow up to 10 connections above pool_size during bursts
    pool_recycle=3600,      # Recycle connections every hour to avoid staleness
    # pool_pre_ping=True       # Enable pool_pre_ping to check and refresh connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
