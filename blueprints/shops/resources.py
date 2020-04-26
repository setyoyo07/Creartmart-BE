from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required
from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from blueprints.users.model import Users
from blueprints.shops.model import Shops
from blueprints.products.model import Products
import hashlib

blueprint_shop = Blueprint("shops", __name__)
api_shop = Api(blueprint_shop)
blueprint_public_shop = Blueprint("public shops", __name__)
api_public_shop = Api(blueprint_public_shop)

#shops info resources
class ShopResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @user_required
    def get(self): #mengambil data shop dan produknya
        user_claims_data = get_jwt_claims()
        qry = Shops.query.filter_by(user_id = user_claims_data["id"])
        qry = qry.first()
        if qry is None:
            qry = Shops(user_claims_data["id"])
            qry.name = "Shop not available"
            # dummy data
            qry.email = ""
            qry.contact = ""
            qry.province = ""
            qry.city_name = ""
            qry.city_type = ""
            qry.postalcode = ""
            qry.street_address = ""
            qry.image = ""
            product = [{"id":"","image":""}]
            shop = marshal(qry, Shops.response_fields)
            return {"result":shop, "product":product}, 200, {"Content-Type": "application/json"}
        else:
            shop = marshal(qry, Shops.response_fields)
            product = Products.query.filter_by(shop_id=shop['id'])
            product = product.filter_by(status=True)
            product = product.order_by(desc(Products.created_at))
            product = product.all()
            product = marshal(product, Products.response_fields)
            return {"result":shop,"product": product}, 200, {"Content-Type": "application/json"}

    @jwt_required
    @user_required
    def put(self): #mengubah info shop
        parser = reqparse.RequestParser()
        parser.add_argument("email", location="json", required=True)
        parser.add_argument("name", location="json", required=True)
        parser.add_argument("contact", location="json", required=True)
        parser.add_argument("province", location="json", required=True)
        parser.add_argument("city_type", location="json", required=True)
        parser.add_argument("city_name", location="json", required=True)
        parser.add_argument("postalcode", location="json", required=True)
        parser.add_argument("street_address", location="json")
        parser.add_argument("image", location="json")
        args = parser.parse_args()
        user_claims_data = get_jwt_claims()
        qry = Shops.query.filter_by(user_id=user_claims_data["id"])

        if qry.first() is None:
            shop = Shops(user_claims_data["id"])
            db.session.add(shop)
            db.session.commit()
        qry = Shops.query.filter_by(user_id=user_claims_data["id"])        
        qry = qry.first()
        if qry.name != args["name"]:
            if Shops.query.filter_by(name=args["name"]).first() is not None:
                return {"status": "FAILED", "message": "Shop's name already exists"}, 400, {"Content-Type": "application/json"}
        qry.name = args["name"]
        qry.email = args["email"]
        qry.contact = args["contact"]
        qry.province = args["province"]
        qry.city_type = args["city_type"]
        qry.city_name = args["city_name"]
        qry.postalcode = args["postalcode"]
        qry.status = True
        if args["street_address"] is not None:
            qry.street_address = args["street_address"]
        if args["image"] is not None:
            qry.image = args["image"]
        qry.updated_at = datetime.now()
        db.session.commit()
        return marshal(qry, Shops.response_fields), 200, {"Content-Type": "application/json"}

#shop products resources
class ShopProductResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @user_required
    def post(self): #menambah product toko yang akan dijual
        parser = reqparse.RequestParser()
        parser.add_argument("name", location="json", required=True)
        parser.add_argument("price", type=int, location="json", required=True)
        parser.add_argument("image", location="json", required=True)
        parser.add_argument("category", location="json", required=True)
        parser.add_argument("subcategory", location="json")
        parser.add_argument("description", location="json")
        parser.add_argument("limited", type=inputs.boolean, location="json", required=True)
        parser.add_argument("stock", type=int, location="json", required=True)
        parser.add_argument("weight", type=int, location="json", required=True)
        args = parser.parse_args()

        user_claims_data = get_jwt_claims()
        qry = Shops.query.filter_by(user_id=user_claims_data["id"])
        qry = qry.first()

        if qry is None:
            return {"status":"FAILED", "message":"Shop's Data not complete. Please complete your Shop's data first!"}, 404, {"Content-Type": "application/json"}
        else:
            product = Products(qry.id, args["name"], args["price"], args["category"], args["subcategory"], args["image"], args["limited"], args["description"], args["stock"],args["weight"])
            db.session.add(product)
            db.session.commit()
            return marshal(product, Products.response_fields), 200, {"Content-Type": "application/json"}
    
    @jwt_required
    @user_required
    def get(self, id=None): #mengambil data produk di shop, spesifik by id
        user_claims_data = get_jwt_claims()
        shop = Shops.query.filter_by(user_id=user_claims_data["id"])
        shop = shop.first()
        product = Products.query
        qry = product.get(id)

        if qry is not None:
            if qry.shop_id == shop.id:
                return marshal(qry, Products.response_fields), 200
            return {'status':'NOT_FOUND'}, 404
        return {'status':'NOT_FOUND'}, 404

    @jwt_required
    @user_required
    def put(self, id=None): #mengubah/mengedit data produk di shop
        
        user_claims_data = get_jwt_claims()
        shop = Shops.query.filter_by(user_id=user_claims_data["id"])
        shop = shop.first()
        product = Products.query
        qry = product.get(id)

        if qry is not None:        
            if qry.shop_id != shop.id:
                return {"status":"access denied"}, 400

            parser = reqparse.RequestParser()
            parser.add_argument("name", location="json", default=qry.name)
            parser.add_argument("price", type=int, location="json", default=qry.price)
            parser.add_argument("image", location="json", default=qry.image)
            parser.add_argument("category", location="json", default=qry.category)
            parser.add_argument("subcategory", location="json", default=qry.subcategory)
            parser.add_argument("description", location="json", default=qry.description)
            parser.add_argument("limited", type=inputs.boolean, location="json", default=qry.limited)
            parser.add_argument("stock", type=int, location="json", default=qry.stock)
            parser.add_argument("weight", type=int, location="json", default=qry.weight)
            args = parser.parse_args()

            qry.name = args["name"]
            qry.price = args["price"]
            qry.category = args["category"]
            qry.subcategory = args["subcategory"]
            qry.image = args["image"]
            qry.description = args["description"]
            qry.limited = args["limited"]
            qry.stock = args["stock"]
            qry.weight = args["weight"]
            qry.updated_at = datetime.now()
            db.session.commit()
            return marshal(qry, Products.response_fields), 200, {"Content-Type": "application/json"}
        return {'status':'NOT_FOUND'}, 404

    @jwt_required
    @user_required
    def delete(self, id=None): #menghapus produk di shop
        user_claims_data = get_jwt_claims()
        shop = Shops.query.filter_by(user_id=user_claims_data["id"])
        shop = shop.first()
        product = Products.query
        qry = product.get(id)

        if qry is None:
            return {'status':'NOT_FOUND'}, 404
        if qry.shop_id != shop.id:
            return {"status":"access denied"}, 400

        #soft delete
        qry.status = False
        db.session.commit()
        
        return {"message": "Product Succesfully Deleted"}, 200, {"Content-Type": "application/json"}

#public shop resources
class PublicShopResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    def get(self, id=None): #mengambil data shop berdasarkan shop id untuk ditampilkan di halaman public
        qry = Shops.query.get(id)
        if qry is not None:
            shop = marshal(qry, Shops.response_fields)
            product = Products.query.filter_by(shop_id=qry.id)
            product = product.filter_by(status=True)
            product = product.order_by(desc(Products.created_at))
            product = product.all()
            product = marshal(product, Products.response_fields)
            return {"result":shop,"product": product}, 200, {"Content-Type": "application/json"}
        return {'status':'NOT_FOUND'}, 404
        
api_shop.add_resource(ShopResources, "")
api_shop.add_resource(ShopProductResources, "/product", "/product/<int:id>")
api_public_shop.add_resource(PublicShopResources, "/<int:id>")