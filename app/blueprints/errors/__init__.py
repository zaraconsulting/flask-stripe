from flask import render_template, Blueprint
from app import app

errors = Blueprint('errors', __name__, template_folder='templates')

@app.errorhandler(404)
@errors.route('/404')
def not_found_error(error):
  return render_template('errors/404.html', error=error), 404