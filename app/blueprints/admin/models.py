from app import db, admin
from flask import current_app, request, flash
from flask_admin import form
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext, lazy_gettext
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from flask_admin.contrib.fileadmin.s3 import S3FileAdmin
from flask_admin.form.upload import ImageUploadField
import stripe, os
from app import s3
from app.models import Product, Coupon

stripe.api_key = os.getenv('STRIPE_TEST_SECRET')

class ProductView(ModelView):
	# page_size = 10
	form_excluded_columns = ('sku', 'created', 'object_', 'url')
	column_exclude_list = ('url', 'description', 'object_')
	form_overrides = dict(image=ImageUploadField)
	# form_args = {
	#   'image': dict(
	#     thumbnail_size=(500, 500, True),
	#     url_relative_path=f'{current_app.config.get("S3_RELATIVE_URL_PATH")}',
	#     namegen=lambda x: int(f'{x.year}{x.month}{x.day}{x.hour}{x.minute}{x.second}'),
	#     storage_type='s3',
	#     bucket_name=current_app.config.get('S3_BUCKET_NAME'),
	#     access_key_id=current_app.config.get('S3_ACCESS_KEY_ID'),
	#     access_key_secret=current_app.config.get('S3_SECRET_ACCESS_KEY'),
	#     acl='public-read',
	#     allowed_extensions=('png', 'jpg'),
	#   )
	# }

	def create_model(self, form):
		try:
			getDate = lambda x: f'{x.year}{x.month}{x.day}{x.hour}{x.minute}{x.second}'
			if request.files["image"]:
				s3.upload_to_aws(request.files["image"], current_app.config.get('S3_BUCKET_NAME'), 'products/' + getDate(datetime.utcnow()) + '.png')

				# # Create Stripe product
				# product = stripe.Product.create(
				#   name=form.name.data,
				#   type='good',
				#   attributes=['name'],
				#   description=form.description.data,
				#   images=[file_upload],
				# )

				# # Create SKU for Stripe product
				# sku = stripe.SKU.create(
				#   product=product.id,
				#   attributes={'name': product.name},
				#   price=int(form.price.data * 100),
				#   currency='usd',
				#   image=product.images[0],
				#   inventory={'type': 'infinite'}
				# ) 
				
				# # Create database product
				# p = Product(
				#   id_=product.id,
				#   sku=sku.id,
				#   name=product.name,
				#   image=product.images[0],
				#   price=form.price.data,
				#   active=product.active,
				#   created=datetime.fromtimestamp(product.created),
				#   description=product.description,
				#   object_=product.type,
				#   url=product.url
				# )
				# db.session.add(p)
				# db.session.commit()
		except Exception as ex:
			if not self.handle_view_exception(ex):
				flash(gettext('Failed to create record. %(error)s', error=str(ex)), 'error')
				log.exception('Failed to create record.')
			self.session.rollback()
			return False
		return True

	def update_model(self, form, model):
		try:
			file = request.files["image"]
			file.filename = getDate(datetime.utcnow()) + '.png'
			file_upload = upload_file_to_s3(file, current_app.config.get('S3_BUCKET_NAME'))

			# Update Stripe SKU information
			sku = stripe.SKU.modify(
				model.sku,
				image = file_upload,
				price = int(form.price.data * 100)
			)

			# Update Stripe Product information
			product = stripe.Product.modify(
				model.id_,
				name=form.name.data,
				images=[file_upload],
				description=form.description.data,
				active=form.active.data,
			)

			# Update database Product model
			model.name = product.name
			model.image = file_upload
			model.price = form.price.data
			model.active = product.active
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
	column_exclude_list = ('object_')
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
	S3FileAdmin(os.getenv('S3_BUCKET_NAME'), 'us-east-2', os.getenv('S3_ACCESS_KEY_ID'), os.getenv('S3_SECRET_ACCESS_KEY')),
)