import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Read the PostgreSQL connection URL from the environment.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create the SQLAlchemy database engine.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create sessions for interacting with PostgreSQL.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """Provide a database session and close it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()