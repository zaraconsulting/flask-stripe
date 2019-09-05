from app import app
from flask import render_template, redirect, url_for, session, request, jsonify
from app.models import Product
import json, stripe, os
from collections import Counter

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

def safe_dollar_to_cent(dollar, truncate=True):
  cents = float(dollar) * 100
  if truncate:
    return int(cents)
  else:
    return cents

@app.context_processor
def get_globals():
  if 'cart' not in session:
    session['cart'] = list()
  return dict(
    cartSession=session['cart'],
    Counter=Counter
  )

@app.route('/')
def index():
  c = {
    'products': Product.query.all()
  }
  # session.clear()
  # if 'cart' in session:
  #   print(session.get('cart'))
  return render_template('index.html', **c)

@app.route('/cart')
def cart():
  if 'cart' not in session:
    session['cart'] = list()
    redirect(url_for('index'))
  products = list()
  for i in session['cart']:
    if i not in products:
      products.append(i)

  sum_ = 0
  for i in session['cart']:
    sum_+=i['price']
  c = {
    'products': products,
    'cart': session['cart'],
    'cartTotal': sum_,
    'key': os.getenv('STRIPE_TEST_PUB'),
    'amount': int(sum([i['price'] for i in session['cart']])*100)
  }
  return render_template('cart.html', **c)

@app.route('/add/<int:id>')
def add(id):
  p = Product.query.get(id)
  # Add item to session
  if 'cart' not in session:
    session['cart'] = list()
  cart = session['cart']
  cart.append(dict(id=p.id, name=p.name, image=p.image, price=p.price))
  session['cart'] = cart
  return redirect(url_for('index'))


@app.route('/charge', methods=['POST'])
def charge():
  try:
    customer = stripe.Customer.create(
      email=request.json['email'],
      source=request.json['token']
    )
    amount = int(sum([i['price'] for i in session['cart']])*100)
    charge = stripe.Charge.create(
      customer=customer.id,
      amount=request.json['amount'],
      currency='usd',
      description=request.json['description']
    )
    session.clear()
    return jsonify({'success': 'success!'})
  except stripe.error.StripeError:
    return jsonify({'status': 'error'}), 500