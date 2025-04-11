# src/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv()

username = os.environ.get("PG_USERNAME")
password = os.environ.get("PG_PASSWORD")
host = os.environ.get("PG_HOST", "localhost")
db_name = os.environ.get("PG_DATABASE")
port = os.environ.get("PG_PORT", "5432")

db_url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"

# Create the SQLAlchemy engine
engine = create_engine(db_url, echo=True)  # echo=True logs SQL commands to the console

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """
    Returns a new session for interacting with the database.
    """
    return SessionLocal()
