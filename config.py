import os
basedir = os.path.abspath(os.path.dirname(__name__))

class Config:
  SECRET_KEY = os.getenv('SECRET_KEY') or os.environ.get('SECRET_KEY')
  FLASK_APP = os.getenv('FLASK_APP') or os.environ.get('FLASK_APP')
  FLASK_DEBUG = os.getenv('FLASK_DEBUG') or os.environ.get('FLASK_DEBUG')
  FLASK_ENV = os.getenv('FLASK_ENV') or os.environ.get('FLASK_ENV')
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or os.environ.get('DATABASE_URL')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  MAIL_SERVER = os.getenv('MAIL_SERVER') or os.environ.get('MAIL_SERVER')
  MAIL_PORT = os.getenv('MAIL_PORT') or os.environ.get('MAIL_PORT')
  MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') or os.environ.get('MAIL_USE_TLS')
  ADMINS = ['derek@zaraconsulting.org']
  MAIL_USERNAME = os.getenv('MAIL_USERNAME') or os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or os.environ.get('MAIL_PASSWORD')
  BUSINESS_NAME = os.getenv('BUSINESS_NAME') or os.environ.get('BUSINESS_NAME')
  PROCESSING_FEE = os.getenv('PROCESSING_FEE') or os.environ.get('PROCESSING_FEE')