from blueprints import db
from flask_restful import fields
from datetime import datetime

class Addresses(db.Model): #Model database alamat pengiriman barang
    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    country = db.Column(db.String(255), default='')
    province = db.Column(db.String(255), default='')
    city_type = db.Column(db.String(255), default='') #kabupaten atau kota
    city_name = db.Column(db.String(255), default='')
    street = db.Column(db.String(255), default='')
    postal_code = db.Column(db.String(255), default='')
    courier = db.Column(db.String(255), default='') #jenis jasa pengiriman barang (ex:jne, pos, tiki)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "cart_id": fields.String,
        "country": fields.String,
        "province": fields.String,
        "city_type": fields.String,
        "city_name": fields.String,
        "street": fields.String,
        "postal_code": fields.String,
        "courier": fields.String,
        "status": fields.Boolean
    }

    def __init__(self, cart_id)  :
        self.cart_id = cart_id
        
    def __repr__(self):
        return "<Addresses %r>" % self.id