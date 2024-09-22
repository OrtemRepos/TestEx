import os
from pathlib import Path

from dotenv import load_dotenv

path_env = [
    "./.env",
    ".secret.env",
    ".email.env",
    ".celery.env",
    ".logging.env",
]


def load_env():
    for path in path_env:
        if Path.exists(Path(path)):
            print(load_dotenv(Path(path)))


class Config:
    def __init__(self):
        self.POSTGRES_DB = os.environ.get("POSTGRES_DB")
        self.POSTGRES_USER = os.environ.get("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
        self.POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
        self.POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
        self.POSTGRES_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        self.REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
        self.REDIS_USER = os.environ.get("REDIS_USER")
        self.REDIS_PORT = os.environ.get("REDIS_PORT")
        self.REDIS_HOST = os.environ.get("REDIS_HOST")
        self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

        self.RABBITMQ_USER = os.environ.get("RABBITMQ_USER")
        self.RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
        self.RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
        self.RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT")
        self.RABBITMQ_URL = f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

        self.JWT_SECRET = os.environ.get("JWT_SECRET")
        self.CRYPT_KEY = os.environ.get("CRYPT_KEY")

        self.token_life_time = int(os.environ.get("TOKEN_LIFE"))
        self.refresh_token_life_time = int(
            os.environ.get("REFRESH_TOKEN_LIFE")
        )

        self.SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
        self.SMTP_HOST = os.environ.get("SMTP_HOST")
        self.SMTP_PORT = os.environ.get("SMTP_PORT")
        self.SMTP_USER = os.environ.get("SMTP_USER")


load_env()
config = Config()
