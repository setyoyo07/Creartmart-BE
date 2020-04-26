from blueprints import db
from flask_restful import fields
from datetime import datetime


class Shops(db.Model):
    __tablename__ = "shops"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String(190), unique=True, default='')
    email = db.Column(db.String(255), default='')
    contact = db.Column(db.String(255), default='')
    province = db.Column(db.String(255), default='')
    city_type = db.Column(db.String(255), default='')
    city_name = db.Column(db.String(255), default='')
    postalcode = db.Column(db.String(255), default='')
    street_address = db.Column(db.String(255), default='')
    image = db.Column(db.String(255), default='')
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "user_id": fields.Integer,
        "name": fields.String,
        "email": fields.String,
        "contact": fields.String,
        "province": fields.String,
        "city_type": fields.String,
        "city_name": fields.String,
        "postalcode": fields.String,
        "street_address": fields.String,
        "image": fields.String,
        "status": fields.Boolean
    }

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return "<Shops %r>" % self.id
