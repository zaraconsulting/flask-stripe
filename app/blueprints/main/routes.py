from flask import render_template, redirect, url_for, current_app, session
from app.models import Product
from app.blueprints.main import main
from collections import Counter

@main.context_processor
def get_globals():
  if 'cart' not in session:
    session['cart'] = list()
  return dict(
    cartSession=session['cart'],
    Counter=Counter
  )

@main.route('/')
def index():
  c = {
    'products': Product.query.all()
  }
  return render_template('index.html', **c)