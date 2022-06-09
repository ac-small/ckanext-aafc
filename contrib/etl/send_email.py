import os
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Replace sender with a "From" address.
# Note: This address must be verified.
SENDER = ''
SENDERNAME = ''

# Replace recipient with a "To" address.
RECIPIENT  = ''

# Replace with your user name.
USERNAME_SMTP = ""

# Replace with your password.
PASSWORD_SMTP = ""

# Replace with SMTP server host and port number
HOST = ""
PORT =

# The subject line of the email.
SUBJECT = 'AAFC Data Catalogue Daily Syncronization'

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("This email is to confirm that the daily syncronization tasks for the AAFC Data Catalogue were successful. Attached are the logs.\r\n")

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h2>AAFC Data Catalogue Syncronization Complete</h2>
  <p>Please see attached logs.</p>
</body>
</html> """

#Define the path to the log files
DIR =os.path.abspath(os.path.dirname(__file__))
FILES = ['error_sync_with_og.log', 'error_post_to_og.log']
LOGS = []

#Join the file path components
for i in FILES:
    if os.path.exists(i) and os.path.isfile(i):
        LOGS.append(os.path.join(DIR, i))

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = SUBJECT
msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
msg['To'] = RECIPIENT

# Record the MIME types of both parts - text/plain and text/html.

for log in LOGS:
    part0 = MIMEBase('application', 'octect-stream')
    part0.set_payload(open(log, 'rb').read())
    encoders.encode_base64(part0)
    part0.add_header (
      'Content-Disposition',
       'attachment; filename={}'.format(os.path.basename(log))
    )
    msg.attach(part0)

part1 = MIMEText(BODY_TEXT, 'plain')
part2 = MIMEText(BODY_HTML, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Try to send the message.
try:
    server = smtplib.SMTP(HOST, PORT)
    server.ehlo()
    server.starttls()
    #stmplib docs recommend calling ehlo() before & after starttls()
    server.ehlo()
    server.login(USERNAME_SMTP, PASSWORD_SMTP)
    server.sendmail(SENDER, RECIPIENT, msg.as_string())
    server.close()
# Display an error message if something goes wrong.
except Exception as e:
    print ("Error: ", e)
else:
    print ("Email sent!")
