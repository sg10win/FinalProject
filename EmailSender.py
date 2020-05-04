import Email, smtplib, ssl
from Email import encoders
from Email.mime.base import MIMEBase
from Email.mime.multipart import MIMEMultipart
from Email.mime.text import MIMEText

class Email(object):
    @staticmethod
    def forget_password_email(code):
        # Create a multipart message and set headers
        subject = "ChatIt - verification code"
        body = f"Your code is: {code}"
        sender_email = "chatit.application"
        receiver_email = "segevshalom86@gmail.com"
        password = "segevshalom10"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject