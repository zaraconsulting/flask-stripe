import smtplib, os
from app import app
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template

def send_email(customer):
  sender = app.config['ADMINS'][0]
  recipient = customer['email']

  msg = MIMEMultipart('alternative')
  msg['subject'] = "Order Confirmation"
  msg['from'] = sender
  msg['to'] = recipient
  msg['reply-to'] = "noreply@zaraconsulting.org"

  html = MIMEText(render_template('/email/confirmation.html', **customer), 'html')
  msg.attach(html)
  server = smtplib.SMTP(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT'))
  server.ehlo()
  server.starttls()
  server.login(app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
  server.sendmail(app.config['ADMINS'][0], recipient, msg.as_string())
  server.quit()