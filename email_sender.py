import smtplib
from email.mime.text import MIMEText

import config_loader

_EMAIL_SUBJECT = "[YALMA] Visits are available"


class EmailSenderException(Exception):
    pass


def __load_email_setting():
    settings = config_loader.read_configuration("email_settings", ["username", "password", "smtp_server", "smtp_port"])
    return settings["username"], settings["password"], settings["smtp_server"], settings["smtp_port"]


def send_email(to: str, message: str):
    username, password, smtp_server, smtp_port = __load_email_setting()

    email_message = MIMEText(message)
    email_message["From"] = username
    email_message["To"] = to
    email_message["Subject"] = _EMAIL_SUBJECT

    mail_server_connection = None

    try:
        print("Sending an email message with notification...")

        mail_server_connection = smtplib.SMTP_SSL(smtp_server, smtp_port)
        mail_server_connection.ehlo()
        mail_server_connection.login(username, password)
        mail_server_connection.sendmail(username, to, email_message.as_string())

        print("The notification has been successfully sent")
    except Exception as exception:
        raise EmailSenderException(f"Unable to send the email. Details: {exception}") from None
    finally:
        if mail_server_connection is not None:
            mail_server_connection.close()
