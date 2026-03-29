import re
import time

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


if not re.fullmatch(r"[A-Za-z0-9_]+", settings.DB_NAME):
    raise ValueError("DB_NAME may only contain letters, numbers, and underscore")

server_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
)
database_url = server_url.set(database=settings.DB_NAME)


def ensure_database_exists(retries: int = 20, delay_seconds: float = 2.0) -> None:
    admin_engine = create_engine(server_url, pool_pre_ping=True)
    try:
        for attempt in range(1, retries + 1):
            try:
                with admin_engine.connect() as connection:
                    connection.execute(
                        text(
                            f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` "
                            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                        )
                    )
                    connection.commit()
                return
            except Exception:
                if attempt == retries:
                    raise
                time.sleep(delay_seconds)
    finally:
        admin_engine.dispose()


ensure_database_exists()
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
