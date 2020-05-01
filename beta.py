import random

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

code = random.randint(10000000,100000000)

subject = "ChatIt - verification code"
body = f"Your code is: {code}"
sender_email = "chatit.application"
receiver_email = "segevshalom86@gmail.com"
password = "segevshalom10"

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email  # Recommended for mass emails

# Add body to email
message.attach(MIMEText(body, "plain"))

#filename = "pyFile.py"  # In same directory as script

# Open PDF file in binary mode
# with open(filename, "rb") as attachment:
#     # Add file as application/octet-stream
#     # Email client can usually download this automatically as attachment
#     part = MIMEBase("application", "octet-stream")
#     part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
#encoders.encode_base64(part)

# Add header as key/value pair to attachment part
#part.add_header(
#    "Content-Disposition",
#    f"attachment; filename= {filename}",
#)

# Add attachment to message and convert message to string
#message.attach(part)
text = message.as_string()

# Log in to server using secure context and send email
s = ['snirshalom2010@gmail.com', 'dshalom01@gmail.com', 'segevshalom86@gmail.com', "ravithoffman2878@gmail.com", '']
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    for i in s:
        server.sendmail(sender_email, i, text)