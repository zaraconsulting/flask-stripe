from flask import Flask
app = Flask(__name__)

from config import Config
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)

from flask_admin import Admin
admin = Admin(app)

from flask_mail import Mail
mail = Mail(app)

from app.blueprints.shop import shop
app.register_blueprint(shop, url_prefix='/shop')

from app.blueprints.errors import errors
app.register_blueprint(errors)

from app import routes, models, errors