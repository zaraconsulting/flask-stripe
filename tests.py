import unittest
from app import db, create_app
from app.models import Product, Coupon
from config import Config
from flask import jsonify
import uuid, stripe

class TestConfig(Config):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ProductModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def testCreateProduct(self):
    p = Product(prod_id='123456789', name="test product", image='https://placehold.it/500x500', price=59.99)
    db.session.add(p)
    db.session.commit()
    self.assertEqual(p.name, 'test product')
    self.assertEqual(p.price, 59.99)

class CouponModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def testCreateCoupon(self):
    c = Coupon(uuid=str(uuid.uuid1().int)[:10], code='TXTNOW', value=5.0)
    db.session.add(c)
    db.session.commit()
    self.assertEqual(c.code, 'TXTNOW')
    self.assertEqual(c.value, 5.0)

if __name__ == '__main__':
  unittest.main(verbosity=2)