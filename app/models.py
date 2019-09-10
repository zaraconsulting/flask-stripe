from app import db, admin
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.dialects.postgresql import UUID

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  prod_id = db.Column(db.String(50))
  sku = db.Column(db.String(50))
  name = db.Column(db.String(50), index=True)
  image = db.Column(db.String(100), nullable=True)
  price = db.Column(db.Float, index=True)

  def __repr__(self):
    return f'<Product: {self.name} | {self.price}>'

class Coupon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
  code = db.Column(db.String(10), nullable=False)

  def __repr__(self):
    return f'<self.code>'

admin.add_views(
  ModelView(Product, db.session),
)
