import os
from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

#Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

#YouTube API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# It's good practice to define model names and settings here
CHAT_MODEL_NAME = "gemini-2.5-flash"
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"

# --- Validation ---
# This is a crucial step to ensure the application doesn't start with missing keys.
if not GEMINI_API_KEY:
  raise ValueError("Missing GEMINI_API_KEY in .env file")
if not SERPER_API_KEY:
  raise ValueError("Missing SERPER_API_KEY in .env file")
if not DATABASE_URL:
  raise ValueError("Missing DATABASE_URL in .env file")
if not YOUTUBE_API_KEY:
  raise ValueError("Missing YOUTUBE_API_KEY in .env file")