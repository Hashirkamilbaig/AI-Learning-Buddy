# agent/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load the secret database URL from the .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in .env file")

# The Engine is the heart of the connection. It manages the connection pool.
engine = create_engine(DATABASE_URL)

# A Session is our "workspace" for talking to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the master blueprint that all our table models will inherit from.
Base = declarative_base()