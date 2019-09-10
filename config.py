import os
basedir = os.path.abspath(os.path.dirname(__name__))

class Config:
  SECRET_KEY = os.getenv('SECRET_KEY')
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  MAIL_SERVER = os.getenv('MAIL_SERVER')
  MAIL_PORT = os.getenv('MAIL_PORT')
  MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
  ADMINS = ['derek@zaraconsulting.org']
  MAIL_USERNAME = os.getenv('MAIL_USERNAME')
  MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
  BUSINESS_NAME = os.getenv('BUSINESS_NAME')