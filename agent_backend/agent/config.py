# File: agent_backend/agent/config.py

import os
from dotenv import load_dotenv

# ==================================================================
# THE FIX IS HERE!
# ==================================================================
# Find the absolute path of the directory this file is in (agent/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go one level up to get the parent directory (agent_backend/)
parent_dir = os.path.dirname(current_dir)
# Construct the full path to the .env file
dotenv_path = os.path.join(parent_dir, '.env')

# Load the environment variables from that specific path
load_dotenv(dotenv_path=dotenv_path)

# Now, the rest of the file can correctly access the loaded variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

#Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

#YouTube API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# It's good practice to define model names and settings here
CHAT_MODEL_NAME = "gemini-2.5-flash" # Note: Updated to a more standard model name, 2.5 is not a public name yet.
EMBEDDING_MODEL_NAME = "models/embedding-001"

# --- Validation ---
# This is a crucial step to ensure the application doesn't start with missing keys.
if not GEMINI_API_KEY:
  raise ValueError("Missing GEMINI_API_KEY in .env file or failed to load .env")
if not SERPER_API_KEY:
  raise ValueError("Missing SERPER_API_KEY in .env file or failed to load .env")
if not DATABASE_URL:
  raise ValueError("Missing DATABASE_URL in .env file or failed to load .env")
if not YOUTUBE_API_KEY:
  raise ValueError("Missing YOUTUBE_API_KEY in .env file or failed to load .env")