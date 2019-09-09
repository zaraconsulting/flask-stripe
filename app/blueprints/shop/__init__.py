from app import app
from flask import render_template, redirect, url_for, session, request, jsonify, Blueprint
from app.models import Product
from app.email import send_email
import json, stripe, os
from collections import Counter

shop = Blueprint('shop', __name__, template_folder='templates')

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

@app.context_processor
def get_globals():
  if 'cart' not in session:
    session['cart'] = list()
  return dict(
    cartSession=session['cart'],
    Counter=Counter
  )

@shop.route('/')
def index():
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
    'amount': int(sum([i['price'] for i in session['cart']])*100),
    'jsonCart': [json.dumps(i) for i in session['cart']]
  }
  return render_template('shop/cart.html', **c)

@shop.route('/add/<int:id>')
def add(id):
  p = Product.query.get(id)
  if 'cart' not in session:
    session['cart'] = []
  cart = session['cart']
  cart.append(
    {
      'id': p.id,
      'name': p.name,
      'price': p.price,
      'image': p.image
    }
  )
  session['cart'] = cart
  return redirect(url_for('index'))

@shop.route('/remove/<int:id>')
def remove(id):
  p = Product.query.get(id)
  cart = session['cart']
  for i in cart:
    if p.name in i['name']:
      cart.remove(i)
      break
  session['cart'] = cart
  return redirect(url_for('shop.index'))

@shop.route('/charge', methods=['POST'])
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
    # send email
    send_email()
    return jsonify({'success': 'success!'})
  except stripe.error.StripeError:
    return jsonify({'status': 'error'}), 500

@shop.route('/thankyou')
def thankyou():
  return render_template('shop/checkout.html')