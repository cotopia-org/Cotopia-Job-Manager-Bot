from os import getenv

from dotenv import load_dotenv

load_dotenv()
API_BASE = getenv("BACKEND_API_URL")
