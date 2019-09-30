from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class CouponForm(FlaskForm):
  entry = StringField()
  submit = SubmitField('Use Coupon')