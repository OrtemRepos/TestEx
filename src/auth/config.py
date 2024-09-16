import os
from dotenv import load_dotenv


load_dotenv("src/auth/.env")


class Config:
    JWT_SECRET = os.environ.get("JWT_SECRET")
    token_life_time = 3600
    refresh_token_life_time = 3600 * 24 * 30


config = Config()
