from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required
from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from blueprints.shops.model import Shops
from blueprints.products.model import Products
from blueprints.carts.model import Carts
from blueprints.transaction_details.model import TransactionDetails
from blueprints.address.model import Addresses
import hashlib, requests, json

blueprint_checkout = Blueprint("checkout", __name__)
api_checkout = Api(blueprint_checkout)

#Checkout resources
class CheckoutResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200
        
    @jwt_required
    @user_required
    def post(self, id=None): #menambah alamat kirim dan mengecek ongkir

        host = 'https://api.rajaongkir.com/starter'
        api_key = '781097c8394774e84a1fc221687c6a77'
        #mengambil data alamat shop
        
        cart = Carts.query.get(id)
        if cart is None:
            return {"message":"NOT FOUND"}, 404
        
        claims = get_jwt_claims()
        if cart.user_id != claims["id"]:
            return {"message":"NOT FOUND"}, 404

        shop_id = cart.shop_id
        shop = Shops.query.get(shop_id)
        
        address = Addresses.query.filter_by(cart_id = id).first()
        if address is None:
            address = Addresses(id)
            db.session.add(address)
            db.session.commit()

        parser =reqparse.RequestParser()
        parser.add_argument("courier", location="json", required=True)
        parser.add_argument("country", location="json", default=address.country)
        parser.add_argument("province", location="json", default=address.province)
        parser.add_argument("city_type", location="json", default=address.city_type)
        parser.add_argument("city_name", location="json", default=address.city_name)
        parser.add_argument("street", location="json", default=address.street)
        parser.add_argument("postal_code", location="json", default=address.postal_code)
        args = parser.parse_args()                                                                                                                                                                                                                              
        
        #menambah/mengubah data ke database addresses
        address.country = args["country"]
        address.province = args["province"]
        address.city_name = args["city_name"]
        address.city_type = args["city_type"]
        address.street = args["street"]
        address.postal_code = args["postal_code"]
        address.courier = args["courier"]
        address.updated_at = datetime.now()
        db.session.commit()

        #request api rajaongkir untuk mencari kode city
        rq = requests.get(host + '/city', params={'key':api_key})            

        list_city = rq.json()
        list_city = list_city["rajaongkir"]["results"]
        for city in list_city:
            if (city["type"].lower() == (shop.city_type).lower()) and (city["city_name"].lower() == (shop.city_name).lower()):
                origin = city["city_id"]
            elif (city["type"].lower() == (args["city_type"]).lower()) and (city["city_name"].lower() == (args["city_name"]).lower()):
                destination = city["city_id"]
        
        #total weight
        transactiondetail = TransactionDetails.query.filter_by(cart_id=id).all()
        total_weight = 0
        for td in transactiondetail:
            product = Products.query.get(td.product_id)
            total_weight += product.weight
        cart.total_weight = total_weight
        db.session.commit()

        #request api rajaongkir untuk mencari shipping cost
        rq = requests.post(host + '/cost', headers={'key':api_key}, json={'origin':origin, 'destination':destination, "weight":cart.total_weight, "courier":args["courier"]})            

        ongkir = rq.json()
        ongkir = ongkir["rajaongkir"]["results"][0]["costs"]
        if ongkir is None:
            cart.shipping_cost = None
            db.session.commit()
            return {"message":"service not available"}, 400
        cart.shipping_cost = ongkir[0]["cost"][0]["value"]
        cart.total_price = cart.total_item_price + cart.shipping_cost
        db.session.commit()

        td = TransactionDetails.query.filter_by(cart_id=cart.id)
        td = td.all()
        marshalShop = marshal(shop, Shops.response_fields)
        marshalCart = marshal(cart, Carts.response_fields)
        marshalCart["shop_id"]=marshalShop
        marshaltd = marshal(td, TransactionDetails.response_fields)
        return [{"cart":marshalCart, "transaction_detail":marshaltd}], 200

        # return {"result":ongkir}, 200
    @jwt_required
    @user_required
    def get(self, id=None): #mengambil data untuk halaman checkout (data cart spesifik by id)
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(id=id)
        cart = cart.first()
        if cart is None:
            return {"message":"NOT FOUND"}, 404
        if cart.total_price == 0:
            cart.total_price = cart.total_item_price     
        td = TransactionDetails.query.filter_by(cart_id=cart.id)
        td = td.all()
        shop = Shops.query.filter_by(id = cart.shop_id).first()
        marshalShop = marshal(shop, Shops.response_fields)
        marshalCart = marshal(cart, Carts.response_fields)
        marshalCart["shop_id"]=marshalShop
        marshaltd = marshal(td, TransactionDetails.response_fields)
        return [{"cart":marshalCart, "transaction_detail":marshaltd}], 200

api_checkout.add_resource(CheckoutResources, "", "/<int:id>")
