from flask import render_template, redirect, url_for, session, request, jsonify, current_app
# from app.models import Product
from app.blueprints.shop.email import send_email
import json, stripe, os
from collections import Counter
from app.blueprints.shop import shop
from app.blueprints.main import main
from datetime import datetime
from app.models import Coupon
from app.blueprints.shop.forms import CouponForm

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

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
    'total': session['subTotal'],
    'grandTotal': (session['subTotal'] * tax) + session['subTotal'],
    'key': os.getenv('STRIPE_TEST_PUB'),
    'amount': int(sum([i['price'] for i in session['cart']])*100),
    'form': form,
    'tax': tax * 100,
    'coupon': int(request.args.get('coupon', float())),
    'couponName': request.args.get('couponName', str()),
  }
  return render_template('shop/cart.html', **c)

@shop.route('/add/<id>')
def add(id):
  """
  [GET] /shop/add/<id>
  """
  if 'cart' not in session:
    session['cart'] = list()
    session['subTotal'] = 0

  p = stripe.Product.retrieve(id)
  
  session['cart'].append(
    {
      'id': p.id,
      'name': p.name,
      'price': float(p.metadata.price),
      'image': p.images[0]
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
      tax=current_app.config.get('PROCESSING_FEE') * 100,
      subtotal=session['subTotal'],
      grandTotal=(session['subTotal'] * current_app.config.get('PROCESSING_FEE') * 100) + session['subTotal'],
      coupon=int(session['coupon'])
    )

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
    coupon = Coupon.query.filter_by(code=form.entry.data).first()
    if not coupon:
      return redirect(url_for('shop.index'))
    session['subTotal'] = session['subTotal'] - (session['subTotal'] * float(coupon.value / 100))
  session['coupon'] = coupon.value
  return redirect(url_for('shop.index', coupon=int(coupon.value), couponName=coupon.code))

@shop.route('/coupon/remove')
def removeCoupon():
  session['subTotal'] = 0
  for i in session['cart']:
    session['subTotal']+=i['price']
  return redirect(url_for('shop.index'))