import os
import logging
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger('uvicorn')


# web connection settings
FRONTEND_URL = os.getenv('FRONTEND_URL')
FRONTEND_DOMAIN = os.getenv('BACKEND_DOMAIN')
BACKEND_URL = os.getenv('BACKEND_URL')
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL
]

CORS_ALLOWED_METHODS = ["*"]
CORS_ALLOWED_HEADERS = ["*"]
ALLOWED_HOSTS = [FRONTEND_DOMAIN]