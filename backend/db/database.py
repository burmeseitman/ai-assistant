import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Supabase PostgreSQL connection string (should use psycopg2 / postgresql://)
# You will replace this in .env (e.g., postgresql://postgres.[project]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_dev.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
