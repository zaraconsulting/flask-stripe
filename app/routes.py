from app import current_app
from flask import render_template, redirect, url_for
from app.models import Product

@app.route('/')
def index():
  c = {
    'products': Product.query.all()
  }
  return render_template('index.html', **c)