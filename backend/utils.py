import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(file_path: str = None) -> str:
    return os.environ.get("API_KEY")