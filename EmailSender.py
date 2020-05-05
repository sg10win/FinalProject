import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender(object):
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

        message.attach(MIMEText(body, "plain"))

        text = message.as_string()
        EmailSender.send_email(sender_email, password, receiver_email, text)
        # Log in to server using secure context and send email
    @staticmethod
    def send_email(sender_email, password, receiver_email, text):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)