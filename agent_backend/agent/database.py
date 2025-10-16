# agent/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from . import config

# The Engine is the heart of the connection. It manages the connection pool.
engine = create_engine(config.DATABASE_URL)

# A Session is our "workspace" for talking to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the master blueprint that all our table models will inherit from.
Base = declarative_base()