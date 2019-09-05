from app import app, db
from app.models import Product

@app.shell_context_processor
def get_context():
  return dict(
    db=db, 
    Product=Product
  )