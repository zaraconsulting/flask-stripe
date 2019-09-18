from app import db, admin
from flask_admin import form
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext, lazy_gettext
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.dialects.postgresql import UUID
import uuid, os, stripe
from datetime import datetime

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

class Product(db.Model):
  id_ = db.Column(db.String, primary_key=True)
  sku = db.Column(db.String)
  name = db.Column(db.String, index=True, nullable=False)
  image = db.Column(db.String, nullable=True)
  price = db.Column(db.Float, index=True, nullable=False)
  active = db.Column(db.Boolean)
  created = db.Column(db.DateTime)
  description = db.Column(db.Text)
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

class ProductView(ModelView):
  # page_size = 10
  form_excluded_columns = ('sku', 'created', 'object_', 'url', 'active')
  column_exclude_list = ('url', 'description', 'object_')

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
        sku=sku.id,
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
      # Update Stripe SKU information
      sku = stripe.SKU.modify(
        model.sku,
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
      stripe.SKU.delete(model.sku)
      
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
  
  @action('delete', lazy_gettext('Delete'), lazy_gettext('Are you sure you want to delete selected records?'))
  def action_delete(self, ids):
    try:
      count = 0
      for i in Product.query.all():
        count+=1
        db.session.delete(i)
      db.session.commit()
      flash(ngettext('Record was successfully deleted.', '%(count)s records were successfully deleted.', count, count=count), 'success')
    except Exception as ex:
      if not self.handle_view_exception(ex):
        raise
    flash(gettext('Failed to delete records. %(error)s', error=str(ex)), 'error')

class CouponView(ModelView):
  column_exclude_list = ('object_', 'created')
  form_excluded_columns = ('object_', 'created')
  
  def on_form_prefill(self, form, id):
    form.duration.render_kw = {'readonly': True}
    form.duration_in_months.render_kw = {'readonly': True}
    form.percent_off.render_kw = {'readonly': True}


  def create_model(self, form):
    try:
      coupon = stripe.Coupon.create(
        name=form.name.data,
        duration=form.duration.data,
        duration_in_months=form.duration_in_months.data,
        percent_off=form.percent_off.data
      )

      c = Coupon(
        id_=coupon.id,
        name=coupon.name,
        duration=coupon.duration,
        duration_in_months=coupon.duration_in_months,
        percent_off=coupon.percent_off,
        created=datetime.fromtimestamp(coupon.created),
        object_=coupon.object
      )
      db.session.add(c)
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
      # Update Stripe Coupon information
      coupon = stripe.Coupon.modify(
        model.id_,
        name=form.name.data
      )

      # Update database Coupon model
      model.name = coupon.name
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
      stripe.Coupon.delete(model.name)

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
  
  @action('delete', lazy_gettext('Delete'), lazy_gettext('Are you sure you want to delete selected records?'))
  def action_delete(self, ids):
    try:
      count = 0
      for i in Coupon.query.all():
        count+=1
        db.session.delete(i)
      db.session.commit()
      flash(ngettext('Record was successfully deleted.', '%(count)s records were successfully deleted.', count, count=count), 'success')
    except Exception as ex:
      if not self.handle_view_exception(ex):
        raise
    flash(gettext('Failed to delete records. %(error)s', error=str(ex)), 'error')

admin.add_views(
  ProductView(Product, db.session),
  CouponView(Coupon, db.session),
)
