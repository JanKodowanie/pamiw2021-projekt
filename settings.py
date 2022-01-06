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
    # "core.users.models",
    # "core.blog.models"
)

def create_db_connection(app) -> None:
    register_tortoise(
        app,
        db_url=DATABASE_URL,
        modules={'models': MODEL_PATHS},
        generate_schemas=True,
        add_exception_handlers=True
    )

Tortoise.init_models(MODEL_PATHS, 'models')


# auth settings
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 600


# media settings
MEDIA_DIR = os.getenv('MEDIA_DIR')
MEDIA_ROOT = '/media'


# sendgrid settings
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
MAIN_EMAIL_TEMPLATE = os.getenv('MAIN_EMAIL_TEMPLATE')
DOMAIN = "https://microsociety.pl"
NO_REPLY_EMAIL = "no-reply@microsociety.pl"
PASS_RESET_ENDPOINT = 'accounts/passwordReset'