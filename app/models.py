from app import db, admin
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.dialects.postgresql import UUID
import uuid

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
  uuid = db.Column(UUID(as_uuid=True), unique=True, default=str(uuid.uuid4()), nullable=False)
  code = db.Column(db.String(10), nullable=False)
  value = db.Column(db.Float(), nullable=True)

  def __repr__(self):
    return f'<self.code>'

class CouponView(ModelView):
  form_widget_args = {
    'uuid': { 'disabled': True }
  }

admin.add_views(
  ModelView(Product, db.session),
  CouponView(Coupon, db.session),
)
