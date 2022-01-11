import os
import logging
from dotenv import load_dotenv
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise


load_dotenv()
logger = logging.getLogger('uvicorn')


# db settings

DATABASE_URL = os.getenv('DATABASE_URL')

MODEL_PATHS = (
    "core.users.models",
    "core.blog.models",
    "aerich.models"
)

DB_CONFIG = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": MODEL_PATHS,
            "default_connection": "default"
        },
    },
}

def create_db_connection(app) -> None:
    register_tortoise(
        app,
        DB_CONFIG
    )

Tortoise.init_models(MODEL_PATHS, 'models')


# auth settings
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 600


# web connection settings
FRONTEND_URL = os.getenv('FRONTEND_URL')
BACKEND_DOMAIN = os.getenv('BACKEND_DOMAIN')
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL
]

CORS_ALLOWED_METHODS = ["*"]
CORS_ALLOWED_HEADERS = ["*"]
ALLOWED_HOSTS = [BACKEND_DOMAIN]


# media settings
MEDIA_DIR = os.getenv('MEDIA_DIR')
MEDIA_ROOT = '/media'


# sendgrid settings
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
MAIN_EMAIL_TEMPLATE = os.getenv('MAIN_EMAIL_TEMPLATE')

NO_REPLY_EMAIL = "no-reply@microsociety.pl"
PASS_RESET_ENDPOINT = "account/reset-password"