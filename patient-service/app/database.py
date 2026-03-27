import pymysql
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load variables from project .env file regardless of current working directory.
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")

def create_db_if_not_exists():
    """Connects to MySQL server and creates the DB if it doesn't exist."""
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    try:
        with connection.cursor() as cursor:
            # Use backticks for DB name to handle special characters
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        connection.commit()
    finally:
        connection.close()

# Run the creation check before SQLAlchemy starts
create_db_if_not_exists()

# Professional Connection String
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()