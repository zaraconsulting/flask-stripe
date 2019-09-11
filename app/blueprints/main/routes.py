from flask import render_template, redirect, url_for, current_app, session
from app.models import Product
from app.blueprints.main import main
from collections import Counter

@main.context_processor
def get_globals():
  if 'cart' not in session or len(session['cart']) == 0:
    session['cart'] = list()
    session['subTotal'] = 0
  return dict(
    cartSession=session['cart'],
  )

@main.route('/')
def index():
  """
  [GET] /
  """
  if 'cart' not in session:
    session['cart'] = list()
    session['subTotal'] = 0

  c = {
    'products': Product.query.all()
  }
  return render_template('index.html', **c)