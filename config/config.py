# config/config.py
import os
from dotenv import load_dotenv

# This line loads the variables from your private .env file
load_dotenv()

def get_env(varname, default=None):
    """Gets an environment variable or returns a default."""
    return os.environ.get(varname, default)

# LLM keys
# Notice these are just the names of the variables, NOT the keys themselves
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
GROQ_API_KEY = get_env("GROQ_API_KEY")

# Web Search API Keys
SERPAPI_KEY = get_env("SERPAPI_KEY")
GOOGLE_CSE_KEY = get_env("GOOGLE_CSE_KEY")
GOOGLE_CX = get_env("GOOGLE_CX")

# Other settings
VECTOR_STORE_DIR = get_env("VECTOR_STORE_DIR", "vector_store")
EMBEDDING_MODEL_NAME = get_env("EMBEDDING_MODEL_NAME", "text-embedding-3-small")  # OpenAI embedding model
CHAT_MEMORY_DB = get_env("CHAT_MEMORY_DB", "chat_memory.sqlite")
CHAT_MEMORY_JSON_DIR = get_env("CHAT_MEMORY_JSON_DIR", "chat_backups")

