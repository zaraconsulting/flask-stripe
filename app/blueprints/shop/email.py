import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template, current_app

def send_email(customer):
  sender = current_app.config['ADMINS'][0]
  recipient = customer['email']

  msg = MIMEMultipart('alternative')
  msg['subject'] = f"Order Confirmation"
  msg['from'] = sender
  msg['to'] = recipient
  msg['reply-to'] = "noreply@zaraconsulting.org"

  html = MIMEText(render_template('email/confirmation.html', **customer), 'html')
  msg.attach(html)
  server = smtplib.SMTP(current_app.config.get('MAIL_SERVER'), current_app.config.get('MAIL_PORT'))
  server.ehlo()
  server.starttls()
  server.login(current_app.config.get('MAIL_USERNAME'), current_app.config.get('MAIL_PASSWORD'))
  server.sendmail(current_app.config['ADMINS'][0], recipient, msg.as_string())
  server.quit()