import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    ORS_API_KEY = os.getenv("ORS_API_KEY")
    BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    
    if not ORS_API_KEY:
        print("Warning: ORS_API_KEY not found in environment variables.")

    if not BRAVE_SEARCH_API_KEY:
        print("Warning: BRAVE_SEARCH_API_KEY not found in environment variables.")
    
    if not LLM_API_KEY:
        print("Warning: LLM_API_KEY not found in environment variables.")
