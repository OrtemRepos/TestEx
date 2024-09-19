import os

from dotenv import load_dotenv

from src.config import config as user_config

load_dotenv("src/email_celery/.celery.env")


class Config:
    def __init__(self):
        self.enable_utc = os.environ.get("ENABLE_UTC", False) == "True"
        self.broker_url = user_config.RABBITMQ_URL
        self.result_backend = user_config.REDIS_URL


config = Config()  # noqa: F811
