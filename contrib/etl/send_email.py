#!/usr/bin/env python
import smtplib, email
import os
import argparse
from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.application import MIMEApplication
from email.Utils import formatdate

#Define the path
DIR =os.path.abspath(os.path.dirname(__file__))
FILES = ['error_sync_with_og.log', 'error_post_to_og.log']
LOGS = []

#Join the path components
for i in FILES:
        if os.path.exists(i) and os.path.isfile(i):
                LOGS.append(os.path.join(DIR, i))

def send_logs (server, port, send_from, to):

#send the log file to send_to
        msg = MIMEMultipart()
        msg ['From'] = send_from
        msg ['To'] = to
        msg ['Subject'] = """Attached are the error logs from AAFC Registry's publication process"""
        msg ['Date'] = formatdate(localtime = True)

# Attach the files
        for log in LOGS:
                part = MIMEBase('application', 'octect-stream')
                part.set_payload(open(log, 'rb').read())
                Encoders.encode_base64(part)
                part.add_header (
                        'Content-Disposition',
                        'attachment; filename={}'.format(os.path.basename(log))
                        )
                msg.attach(part)

        try:
                server = smtplib.SMTP(host= server, port = port)
                print 'Connected to server'
                server.ehlo()
                print 'Echo from server'
        except Exception, e:
                error = 'Something is broken: {}'.format(str(e))
                print error
                return False
        try:
                worked = server.sendmail(send_from,[to], msg.as_string())
                print "Mail has been sent"

        except Exception, e:
                error ='Email not sent: {}'.format(str(e))
                print error
                return False
        finally:
                server.close()
                print 'Server closed'

        return True

def main():
        parser = argparse.ArgumentParser(description ='Email server logs')
        parser.add_argument('-server', '--server', dest= 'server', help = 'The mail server')
        parser.add_argument('-port', '--port', dest ='port', help = 'Port number')
        parser.add_argument('-send_from', '--from', dest= 'send_from', help = 'Sender address')
        parser.add_argument('-to', '--to', dest ='to', help = 'Recipient address')

        args = parser.parse_args()

        email_Sent = send_logs(args.server, args.port, args.send_from, args.to)

if __name__=='__main__':
        main()
