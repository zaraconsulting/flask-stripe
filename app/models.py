from app import db
from datetime import datetime

class Product(db.Model):
  id_ = db.Column(db.String, primary_key=True)
  sku = db.Column(db.String)
  name = db.Column(db.String, index=True, nullable=False)
  image = db.Column(db.String, nullable=True)
  price = db.Column(db.Float, index=True, nullable=False)
  created = db.Column(db.DateTime)
  description = db.Column(db.Text)
  active = db.Column(db.Boolean)
  object_ = db.Column(db.String)
  url = db.Column(db.String, nullable=True)

  def __repr__(self):
    return f'<Product: {self.name} | {self.price}>'

class Coupon(db.Model):
  id_ = db.Column(db.String, primary_key=True)
  name = db.Column(db.String, nullable=False)
  duration = db.Column(db.String, nullable=False)
  duration_in_months = db.Column(db.Integer)
  created = db.Column(db.DateTime)
  percent_off = db.Column(db.Float)
  object_ = db.Column(db.String)

  def __repr__(self):
    return f'<{self.id_}> | <{self.name}>'