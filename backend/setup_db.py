import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import text
from db.database import engine, Base
from db.models import User, ChatSession, DbChatMessage, CompanyDocument, DocumentEmbedding

def setup_database():
    print("Setting up Supabase database...")
    
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
        print("Enabled pgvector extension.")
    
    Base.metadata.create_all(bind=engine)
    print("Created all tables.")
    
    print("Database setup complete!")
    print("\nTables created:")
    for table in Base.metadata.tables:
        print(f"  - {table}")

if __name__ == "__main__":
    setup_database()
