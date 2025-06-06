import sys
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app.database import Base, engine
from src.app.models import device  # This ensures all models are imported and registered with Base

def init_db():
    """Initialize the database and create all tables"""
    # Create the database if it doesn't exist
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    load_dotenv()  # Load environment variables
    init_db()
