import os

from dotenv import load_dotenv

load_dotenv("src/auth/.env")


class Config:
    JWT_SECRET: str = os.environ.get("JWT_SECRET")  # type: ignore
    CRYPT_KEY: bytes = os.environ.get("CRYPT_KEY")  # type: ignore

    token_life_time = 3600
    refresh_token_life_time = 3600 * 24 * 30


config = Config()
