from app.blueprints.errors import errors

@errors.errorhandler(404)
def not_found_error(error):
  return render_template('errors/404.html', error=error), 404

@errors.errorhandler(500)
def unauthorized_error(error):
  return render_template('errors/500.html', error=error), 500