from app import db, admin
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.dialects.postgresql import UUID
import uuid, os, stripe

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), index=True)
  image = db.Column(db.String(100), nullable=True)
  price = db.Column(db.Float, index=True)

  def __repr__(self):
    return f'<Product: {self.name} | {self.price}>'

class Coupon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String(10), unique=True, default=str(uuid.uuid4())[:8])
  code = db.Column(db.String(10), nullable=False)
  value = db.Column(db.Float, nullable=True)

  def __repr__(self):
    return f'<{self.code}>'

class ProductView(ModelView):
  def create_model(self, form):
    p = Product(name=form.name.data, image=form.image.data, price=form.price.data)
    db.session.add(p)
    db.session.commit()

    stripe.Product.create(
      name=form.name.data,
      type='good',
      attributes=['name'],
      images=[form.image.data],
      metadata={ 'price': form.price.data }
    )
    return self.render('admin/model/create.html', form=form)


class CouponView(ModelView):
  form_widget_args = {
    'uuid': { 'disabled': True }
  }

admin.add_views(
  ProductView(Product, db.session),
  CouponView(Coupon, db.session),
)
