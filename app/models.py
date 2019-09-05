from app import db

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), index=True)
  image = db.Column(db.String(100), nullable=True)
  price = db.Column(db.Float, index=True)

  def __init__(self, name, image, price):
    self.name = name
    self.image = image
    self.price = price

  def __repr__(self):
    return f'<Product: {self.name} | {self.price}>'