from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin

db = SQLAlchemy()
migrate = Migrate()
admin = Admin(name="Flask Shopping Cart")

def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(config_class)
  
  db.init_app(app)
  migrate.init_app(app, db)

  app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
  admin.init_app(app)
  with app.app_context():
    from app.blueprints.admin import models
  
  from app.blueprints.shop import shop
  app.register_blueprint(shop, url_prefix='/shop')
  
  from app.blueprints.errors import errors
  app.register_blueprint(errors)

  from app.blueprints.main import main
  app.register_blueprint(main)

  return app

from app import models