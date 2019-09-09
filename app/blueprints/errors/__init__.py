from flask import render_template, Blueprint
from app import app

errors = Blueprint('errors', __name__, template_folder='templates')

@app.errorhandler(404)
def not_found_error(error):
  return render_template('errors/404.html', error=error), 404

@app.errorhandler(500)
def unauthorized_error(error):
  return render_template('errors/500.html', error=error), 500