from flask import render_template, redirect, url_for, session, request, jsonify, current_app
from app.models import Product
from app.blueprints.shop.email import send_email
import json, stripe, os
from collections import Counter
from app.blueprints.shop import shop
from app.blueprints.main import main
from datetime import datetime
from app.models import Coupon
from app.blueprints.shop.forms import CouponForm

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

def getUSD(amount):
  return round(amount, 2)

@shop.context_processor
def get_globals():
  if 'cart' not in session or len(session['cart']) == 0:
    session['cart'] = list()
    session['subTotal'] = 0
  return dict(
    cartSession=session['cart'],
  )

@shop.route('/')
def index():
  """
  [GET] /shop
  """
  if 'cart' not in session or len(session['cart']) == 0:
    session['cart'] = list()
    session['subTotal'] = 0

  form = CouponForm()

  # initialize products
  products = []
  for i in session['cart']:
    if i not in products:
      products.append(i)

  tax = current_app.config.get('PROCESSING_FEE')

  c = {
    'products': products,
    'cart': session['cart'],
    'subTotal': getUSD(sum([i['price'] for i in session['cart']])),
    'grandTotal': getUSD((session['subTotal'] * tax) + session['subTotal']),
    'key': os.getenv('STRIPE_TEST_PUB'),
    'amount': int(getUSD((session['subTotal'] * tax) + session['subTotal']) * 100),
    'form': form,
    'tax': getUSD(sum([i['price'] for i in session['cart']]) * tax),
    'coupon': int(request.args.get('coupon', float())),
    'couponName': request.args.get('couponName', str()),
  }
  return render_template('shop/cart.html', **c)

@shop.route('/add/<id>')
def add(id):
  """
  [GET] /shop/add/<str:id>
  """
  if 'cart' not in session:
    session['cart'] = list()
    session['subTotal'] = 0

  p = Product.query.filter_by(id_=id).first()
  
  session['cart'].append(
    {
      'id': p.id_,
      'name': p.name,
      'price': p.price,
      'description': p.description,
      'image': p.image
    }
  )
  
  # calculate subtotal
  session['subTotal'] = 0
  for i in session['cart']:
    session['subTotal']+=i['price']
  return redirect(url_for('main.index'))

@shop.route('/remove/<id>')
def remove(id):
  """
  [GET] /shop/remove/<id>
  """
  p = stripe.Product.retrieve(id)
  cart = session['cart']
  for i in cart:
    if p.name in i['name']:
      cart.remove(i)
      break
  session['subTotal'] = 0
  for i in cart:
    session['subTotal']+=i['price']
  session['cart'] = cart
  return redirect(url_for('shop.index'))

@shop.route('/charge', methods=['POST'])
def charge():
  """
  [GET] /shop/charge
  """
  try:
    # Build product dictionaries from Session cart 
    products = list()
    productDict = dict()
    for i in session['cart']:
      if i not in products:
        products.append(i)
        productDict[i['id']] = f"Name: {i['name']}; Quantity: {session['cart'].count(i)};"
      
    # Create Stripe customer object
    customer = stripe.Customer.create(email=request.json['email'], source=request.json['token'])
    
    # Create Stripe charge object
    charge = stripe.Charge.create(
      customer=customer.id,
      amount=request.json['amount'],
      currency='usd',
      description=request.json['description'],
      metadata=productDict
    )

    # Build Customer Order Information object
    customerInfo = dict(
      id=customer.id,
      email=customer.email,
      description=charge.description,
      order_no=charge.id,
      cart=session['cart'],
      products=products,
      transactionDate=datetime.fromtimestamp(charge.created).strftime("%B %d, %Y"),
      tax=sum([i['price'] for i in session['cart']]) * current_app.config.get('PROCESSING_FEE'),
      subtotal=sum([i['price'] for i in session['cart']]),
      grandTotal=(session['subTotal'] * current_app.config.get('PROCESSING_FEE')) + session['subTotal'],
    )
    if 'coupon' in session:
      customerInfo['coupon']=int(session['coupon'])

    send_email(customerInfo) # Send confirmation email
    session.clear() # clear Session cart
    return jsonify({'success': 'success!'})
  except stripe.error.StripeError:
    return jsonify({'status': 'error'}), 500

@shop.route('/thankyou')
def thankyou():
  """
  [GET] /shop/thankyou
  """
  return render_template('shop/checkout.html')

@shop.route('/clear')
def clear():
  """
  [GET] /shop/clear
  """
  session.clear()
  return redirect(url_for('shop.index'))

@shop.route('/coupon/add', methods=['POST'])
def useCoupon():
  form = CouponForm()
  session['originalSubTotal'] = session['subTotal']
  if form.validate_on_submit():
    coupon = Coupon.query.filter_by(name=form.entry.data).first()
    if not coupon:
      return redirect(url_for('shop.index'))
    session['subTotal'] = session['subTotal'] - (session['subTotal'] * float(coupon.percent_off / 100))
  session['coupon'] = coupon.percent_off
  return redirect(url_for('shop.index', coupon=int(coupon.percent_off), couponName=coupon.name))

@shop.route('/coupon/remove')
def removeCoupon():
  session['subTotal'] = 0
  for i in session['cart']:
    session['subTotal']+=i['price']
  return redirect(url_for('shop.index'))