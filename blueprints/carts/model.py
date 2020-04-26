from blueprints import db
from flask_restful import fields
from datetime import datetime


class Carts(db.Model):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"))
    total_item = db.Column(db.Integer, default=0)
    total_item_price = db.Column(db.Integer, default=0)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    payment_status = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Integer, default=0)
    shipping_cost = db.Column(db.Integer, default=0)
    total_weight = db.Column(db.Integer, default=0)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "shop_id": fields.Integer,
        "user_id": fields.Integer,
        "total_item": fields.Integer,
        "total_item_price": fields.Integer,
        "shipping_cost": fields.Integer,
        "total_price": fields.Integer,
        "payment_id": fields.Integer,
        "payment_status": fields.Boolean,
        "total_weight": fields.Integer,
        "status": fields.Boolean
    }

    def __init__(self, shop_id, user_id):
        self.shop_id = shop_id
        self.user_id = user_id

    def __repr__(self):
        return "<Carts %r>" % self.id

class Payments(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_method = db.Column(db.String(255), default='')
    account_name = db.Column(db.String(255), default='')
    account_number = db.Column(db.String(255), default='')
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "payment_method": fields.String,
        "account_name": fields.String,
        "account_number": fields.String,
        "status": fields.Boolean
    }

    def __init__(self, payment_method, account_name, account_number):
        self.payment_method = payment_method
        self.account_number = account_number
        self.account_name = account_name
        
    def __repr__(self):
        return "<Payments %r>" % self.id