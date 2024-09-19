import os

from dotenv import load_dotenv

load_dotenv("src/email_celery/.email.env")


class Config:
    def __init__(self):
        self.SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
        self.SMTP_HOST = os.environ.get("SMTP_HOST")
        self.SMTP_PORT = os.environ.get("SMTP_PORT")
        self.SMTP_USER = os.environ.get("SMTP_USER")


config = Config()
