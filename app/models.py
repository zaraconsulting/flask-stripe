from app import db, admin
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.dialects.postgresql import UUID
import uuid, os, stripe
from datetime import datetime

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

class Product(db.Model):
  id_ = db.Column(db.String, primary_key=True)
  name = db.Column(db.String(50), index=True, nullable=False)
  image = db.Column(db.String(100), nullable=True)
  price = db.Column(db.Float, index=True, nullable=False)
  active = db.Column(db.Boolean)
  created = db.Column(db.DateTime)
  description = db.Column(db.Text)
  object_ = db.Column(db.String)
  url = db.Column(db.String, nullable=True)

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
  # page_size = 10
  form_excluded_columns = ('created', 'object_', 'url', 'active')
  column_exclude_list = ('url', 'description')

  def create_model(self, form):
    try:
      # Create Stripe product
      product = stripe.Product.create(
        name=form.name.data,
        type='good',
        attributes=['name'],
        description=form.description.data,
        images=[form.image.data],
      )

      # Create SKU for Stripe product
      sku = stripe.SKU.create(
        product=product.id,
        attributes={'name': product.name},
        price=int(form.price.data * 100),
        currency='usd',
        image=product.images[0],
        inventory={'type': 'infinite'}
      ) 
      
      # Create database product
      p = Product(
        id_=product.id,
        name=product.name,
        image=product.images[0],
        price=form.price.data,
        active=product.active,
        created=datetime.fromtimestamp(product.created),
        description=product.description,
        object_=product.type,
        url=product.url
      )
      db.session.add(p)
      db.session.commit()
    except Exception as ex:
      if not self.handle_view_exception(ex):
        flash(gettext('Failed to create record. %(error)s', error=str(ex)), 'error')
        log.exception('Failed to create record.')
      self.session.rollback()
      return False
    return self.render('admin/model/create.html', form=form)

  def update_model(self, form, model):
    try:
      for i in stripe.SKU.list():
        if i.product == model.id_:
          sid = i.id

      # Update Stripe SKU information
      sku = stripe.SKU.modify(
        sid,
        image = form.image.data,
        price = int(form.price.data * 100)
      )

      # Update Stripe Product information
      product = stripe.Product.modify(
        model.id_,
        name = form.name.data,
        images = [sku.image],
        description = form.description.data
      )

      # Update database Product model
      model.name = product.name
      model.image = sku.image
      model.price = form.price.data
      model.description = product.description
      db.session.commit()
    
    except Exception as ex:
      if not self.handle_view_exception(ex):
        flash(gettext('Failed to update record. %(error)s', error=str(ex)), 'error')
        log.exception('Failed to update record.')
      self.session.rollback()
      return False
    return True

  
  def delete_model(self, model):
    try:
      # Delete SKU from Stripe (must be done before deleting product)
      for i in stripe.SKU.list():
        if i.product == model.id_:
          stripe.SKU.delete(i.id)
      
      # Delete product from Stripe
      stripe.Product.delete(model.id_)

      # Delete from database
      db.session.delete(model)
      db.session.commit()

    except Exception as ex:
      if not self.handle_view_exception(ex):
        flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
        log.exception('Failed to delete record.')
      self.session.rollback()
      return False
    return True

class CouponView(ModelView):
  form_widget_args = {
    'uuid': { 'disabled': True }
  }

admin.add_views(
  ProductView(Product, db.session),
  CouponView(Coupon, db.session),
)
