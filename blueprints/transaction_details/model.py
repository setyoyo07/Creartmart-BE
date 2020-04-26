from blueprints import db
from flask_restful import fields
from datetime import datetime


class TransactionDetails(db.Model):
    __tablename__ = "transactiondetails"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    price = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "product_id": fields.Integer,
        "cart_id": fields.Integer,
        "price": fields.Integer,
        "quantity": fields.Integer,
        "status": fields.Boolean
    }

    def __init__(self, product_id, cart_id, price, quantity):
        self.product_id = product_id
        self.cart_id = cart_id
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return "<TransactionDetails %r>" % self.id