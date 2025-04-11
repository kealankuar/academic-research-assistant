import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

username = os.environ.get("PG_USERNAME")
password = os.environ.get("PG_PASSWORD")
host = os.environ.get("PG_HOST", "localhost")
db_name = os.environ.get("PG_DATABASE")
port = os.environ.get("PG_PORT", "5432")

db_url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
engine = create_engine(db_url)

with engine.connect() as connection:
    result = connection.execute(text("SELECT version();"))
    for row in result:
        print("PostgreSQL version:", row)
