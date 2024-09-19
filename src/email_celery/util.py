from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def generate_email(
    user_email: str, token: str, html_msg: str, subject_msg: str
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject_msg
    text = f"Hello, please confirm your email\nThis your token: {token}"
    html_msg = html_msg.replace("|token|", token)
    print(html_msg)
    plain_msg = MIMEText(text, "plain")
    html = MIMEText(html_msg, "html")
    msg.attach(plain_msg)
    msg.attach(html)
    return msg
