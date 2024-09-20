from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import config


def generate_email(
    user_email: str, token: str, html_msg: str, subject_msg: str
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject_msg
    msg["From"] = config.SMTP_USER
    msg["To"] = user_email
    text = f"Hello, please confirm your email\nThis your token: {token}"
    html_msg = html_msg.replace("|token|", token)
    plain_msg = MIMEText(text, "plain")
    html = MIMEText(html_msg, "html")
    msg.attach(plain_msg)
    msg.attach(html)
    return msg
