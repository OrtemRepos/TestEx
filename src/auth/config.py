import os
from dotenv import load_dotenv


load_dotenv("src/auth/.env")


class Config:
    JWT_SECRET = os.environ.get("JWT_SECRET")


config = Config()
