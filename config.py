import os
basedir = os.path.abspath(os.path.dirname(__name__))

class Config:
  SECRET_KEY = os.getenv('SECRET_KEY')