from blueprints import db
from flask_restful import fields
from datetime import datetime


class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"))
    name = db.Column(db.String(255), default='')
    price = db.Column(db.Integer, default=0)
    category = db.Column(db.String(255), default='')
    subcategory = db.Column(db.String(255), default='')
    image = db.Column(db.String(255), default='')
    limited = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(255), default='')
    sold = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=1)
    promo = db.Column(db.Boolean, default=False)
    discount = db.Column(db.Integer, default=0)
    weight = db.Column(db.Integer, default=0)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "shop_id": fields.Integer,
        "name": fields.String,
        "price": fields.Integer,
        "category": fields.String,
        "subcategory": fields.String,
        "image": fields.String,
        "limited": fields.Boolean,
        "description": fields.String,
        "sold": fields.Integer,
        "stock": fields.Integer,
        "promo": fields.Boolean,
        "discount": fields.Integer,
        "weight": fields.Integer,
        "status": fields.Boolean
    }

    def __init__(self, shop_id, name, price, category, subcategory, image, limited, description, stock, weight):
        self.shop_id = shop_id
        self.name = name
        self.price = price
        self.category = category
        self.subcategory = subcategory
        self.image = image
        self.limited = limited
        self.description = description
        self.stock = stock
        self.weight = weight

    def __repr__(self):
        return "<Products %r>" % self.id