html_verify_msg = ""
with open("src/email_celery/template/confirm_email.html") as f:
    html_verify_msg = f.read()

html_forgot_password_msg = ""
with open("src/email_celery/template/reset_password.html") as f:
    html_forgot_password_msg = f.read()
