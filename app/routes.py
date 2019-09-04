from app import app
from flask import render_template, redirect, url_for

@app.route('/')
def index():
  c = {

  }
  return render_template('index.html', **c)

@app.route('/cart')
def cart():
  c = {

  }
  return render_template('cart.html', **c)