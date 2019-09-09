from app import db, admin
from flask_admin import form
from flask_admin.contrib.sqla import ModelView

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  prod_id = db.Column(db.String(50))
  sku = db.Column(db.String(50))
  name = db.Column(db.String(50), index=True)
  image = db.Column(db.String(100), nullable=True)
  price = db.Column(db.Float, index=True)

  def __repr__(self):
    return f'<Product: {self.name} | {self.price}>'

admin.add_views(
  ModelView(Product, db.session),
)
