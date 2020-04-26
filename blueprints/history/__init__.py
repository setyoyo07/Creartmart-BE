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
from blueprints.carts.model import Carts, Payments
from blueprints.transaction_details.model import TransactionDetails
from blueprints.address.model import Addresses
import hashlib, requests, json

blueprint_history = Blueprint("history", __name__)
api_history = Api(blueprint_history)

#Order Detail resources
class OrderDetailResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @user_required
    def post(self, id=None): #menambah payment method dan payment status
        parser =reqparse.RequestParser()
        parser.add_argument("payment_id", location="args", required=True)
        args = parser.parse_args()    

        claims = get_jwt_claims()
        cart = Carts.query.get(id)
        if cart is None:
            return {"status":"NOT FOUND"}, 404
        transactiondetail = TransactionDetails.query.filter_by(cart_id=id)
        transactiondetail = transactiondetail.all()
        list_td = []
        for td in transactiondetail:
            product = Products.query.filter_by(id=td.product_id).first()
            product.sold += td.quantity
            product.stock -= td.quantity
            if product.stock == 0:
                product.status = False 
            db.session.commit()
        cart.payment_id = args["payment_id"]
        cart.status = False
        cart.updated_at = datetime.now()
        db.session.commit()

        return marshal(cart, Carts.response_fields), 200

    @jwt_required
    @user_required
    def get(self, id=None): #mengambil data transaksi detail spesifik by cart id
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(status=False)
        cart = cart.filter_by(id=id)
        cart = cart.first()
        transactiondetail = TransactionDetails.query.filter_by(cart_id=id)
        transactiondetail = transactiondetail.all()
        list_td = []
        for td in transactiondetail:
            product = Products.query.filter_by(id=td.product_id).first()
            marshalProduct = marshal(product, Products.response_fields)
            marshaltd = marshal(td, TransactionDetails.response_fields)
            marshaltd["product_id"] = marshalProduct
            list_td.append(marshaltd)
        address = Addresses.query.filter_by(cart_id=id).first()
        payment = Payments.query.get(cart.payment_id)
        shop = Shops.query.get(cart.shop_id)
        marshalCart = marshal(cart, Carts.response_fields)
        marshalAddress = marshal(address, Addresses.response_fields)
        marshalPayment = marshal(payment, Payments.response_fields)
        marshalShop = marshal(shop, Shops.response_fields)
        marshalCart["payment_id"] = marshalPayment
        marshalCart["shop_id"] = marshalShop
        return {"result":[marshalCart], "transaction_detail":list_td, "shipping_address":marshalAddress}, 200

# Order History Resources
class OrderHistoryResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @user_required
    def get(self): #mengambil semua data transaksi detail untuk user
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=5)

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']
    
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(status=False)
        cart = cart.order_by(desc(Carts.created_at))
        cart = cart.all()
        if cart is None:
            return {"message":"NOT FOUND"}, 404

        result = []
        for qry in cart:
            transactiondetail = TransactionDetails.query.filter_by(cart_id=qry.id)
            transactiondetail = transactiondetail.all()
            list_td = []
            for td in transactiondetail:
                product = Products.query.filter_by(id=td.product_id).first()
                marshaltd = marshal(td, TransactionDetails.response_fields)
                marshaltd["product_id"] = product.name
                list_td.append(marshaltd)
            shop = Shops.query.get(qry.shop_id)
            marshalCart = marshal(qry, Carts.response_fields)
            marshalCart["shop_id"] = shop.name
            result.append({"cart":[marshalCart],"transaction_detail":list_td})

        return result, 200

#Seller History Detail Resources
class SellerDetailResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @user_required
    def get(self, id=None): #mengambil data transaksi detail untuk seller/shop spesifik by cart id
        claims = get_jwt_claims()
        shop = Shops.query.filter_by(user_id = claims["id"]).first()
        if shop is None:
            return {"message":"NOT FOUND"}, 404
        cart = Carts.query.filter_by(shop_id = shop.id)
        cart = cart.filter_by(status=False)
        cart = cart.filter_by(id=id)
        cart = cart.first()
        if cart is None:
            return {"message":"NOT FOUND"}, 404

        transactiondetail = TransactionDetails.query.filter_by(cart_id=id)
        transactiondetail = transactiondetail.all()
        list_td = []
        for td in transactiondetail:
            product = Products.query.filter_by(id=td.product_id).first()
            marshalProduct = marshal(product, Products.response_fields)
            marshaltd = marshal(td, TransactionDetails.response_fields)
            marshaltd["product_id"] = marshalProduct
            list_td.append(marshaltd)
        address = Addresses.query.filter_by(cart_id=id).first()
        payment = Payments.query.get(cart.payment_id)
        shop = Shops.query.get(cart.shop_id)
        marshalCart = marshal(cart, Carts.response_fields)
        marshalAddress = marshal(address, Addresses.response_fields)
        marshalPayment = marshal(payment, Payments.response_fields)
        marshalShop = marshal(shop, Shops.response_fields)
        marshalCart["payment_id"] = marshalPayment
        marshalCart["shop_id"] = marshalShop
        return {"result":[marshalCart], "transaction_detail":list_td, "shipping_address":marshalAddress}, 200

#Seller History Resources
class SellerHistoryResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200
        
    @jwt_required
    @user_required
    def get(self): #mengambil semua data transaksi detail untuk seller
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']
    
        claims = get_jwt_claims()
        shop = Shops.query.filter_by(user_id = claims["id"]).first()
        if shop is None:
            return {"message":"NOT FOUND"}, 404
        cart = Carts.query.filter_by(shop_id = shop.id)
        cart = cart.filter_by(status=False)
        cart = cart.order_by(desc(Carts.created_at))
        cart = cart.all()
        if cart is None:
            return {"message":"NOT FOUND"}, 404
        
        result = []
        for qry in cart:
            transactiondetail = TransactionDetails.query.filter_by(cart_id=qry.id)
            transactiondetail = transactiondetail.all()
            list_td = []
            for td in transactiondetail:
                product = Products.query.filter_by(id=td.product_id).first()
                marshaltd = marshal(td, TransactionDetails.response_fields)
                marshaltd["product_id"] = product.name
                list_td.append(marshaltd)
            user = Users.query.get(qry.user_id)
            marshalCart = marshal(qry, Carts.response_fields)
            marshalCart["user_id"] = user.name
            result.append({"cart":[marshalCart],"transaction_detail":list_td})

        return result, 200

api_history.add_resource(OrderDetailResources, "/order/<int:id>")
api_history.add_resource(OrderHistoryResources, "/order")
api_history.add_resource(SellerDetailResources, "/seller/<int:id>")
api_history.add_resource(SellerHistoryResources, "/seller")