import smtplib

from celery import Celery  # type: ignore

from src.email_celery.celery_config import config as celery_config
from src.email_celery.config import config
from src.email_celery.constant import html_forgot_password_msg, html_verify_msg
from src.email_celery.util import generate_email

async_queue = Celery("router")
async_queue.config_from_object(celery_config)


@async_queue.task
def send_verification_email_task(user_email: str, token: str) -> bool:
    email = generate_email(
        user_email, token, html_verify_msg, "Verify your email"
    )
    with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_USER, user_email, email.as_string())
    return True


@async_queue.task
def send_forgot_password_email_task(user_email: str, token: str) -> bool:
    email = generate_email(
        user_email, token, html_forgot_password_msg, "Reset your password"
    )
    with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_USER, user_email, email.as_string())
    return True
