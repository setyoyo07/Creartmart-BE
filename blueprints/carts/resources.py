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
import hashlib

blueprint_cart = Blueprint("carts", __name__)
api_cart = Api(blueprint_cart)

#Cart resources
class CartResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @user_required
    def post(self): #menambah produk ke keranjang user
        parser =reqparse.RequestParser()
        parser.add_argument("product_id", type=int, location="json")
        parser.add_argument("quantity", type=int, location="json")
        args = parser.parse_args()

        claims = get_jwt_claims()
        user_id = claims['id']
        product = Products.query
        product = product.get(args["product_id"])
        if product is None:
            return {"message":"Product Not Available"}, 404
        if product.status == False:
            return {"message":"Product Not Available"}, 404
        cart = Carts.query.filter_by(status=True)
        cart = cart.filter_by(user_id = user_id)
        cart = cart.filter_by(shop_id = product.shop_id).first()
        if cart is None:
            cart = Carts(product.shop_id, user_id)
            db.session.add(cart)
            db.session.commit()

        td = TransactionDetails(args["product_id"], cart.id, product.price, args["quantity"])
        db.session.add(td)
        db.session.commit()

        cart.total_item += args["quantity"]
        if product.promo:
            cart.total_item_price += ((int(product.price)-(int(product.discount)*int(product.price)))*int(args["quantity"]))
        else:
            cart.total_item_price += (int(product.price)*int(args["quantity"]))
        cart.updated_at = datetime.now()
        db.session.commit()

        return {'status':'Success'}, 200

    @jwt_required
    @user_required
    def get(self): #mengambil data cart milik user
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(status=True)
        cart = cart.order_by(desc(Carts.updated_at))
        cart = cart.all()
        result=[]
        for qry in cart:
            shop = Shops.query.filter_by(id = qry.shop_id).first()
            marshalShop = marshal(shop, Shops.response_fields)
            marshalqry = marshal(qry, Carts.response_fields)
            marshalqry["shop_id"]=marshalShop
            transactiondetail = TransactionDetails.query.filter_by(cart_id=qry.id)
            transactiondetail = transactiondetail.all()
            list_td = []
            for td in transactiondetail:
                product = Products.query.filter_by(id=td.product_id).first()
                marshalProduct = marshal(product, Products.response_fields)
                marshaltd = marshal(td, TransactionDetails.response_fields)
                marshaltd["product_id"] = marshalProduct
                list_td.append(marshaltd)
            result.append({"cart":marshalqry,"transaction_detail": list_td})
        return result, 200

    @jwt_required
    @user_required
    def delete(self, id=None): #menghapus cart detail by id
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(status=True)
        qry = TransactionDetails.query.get(id)
        if qry is None:
            return {'status':'NOT_FOUND'}, 404

        cart = cart.filter_by(id=qry.cart_id).first()
        if cart is None:
            return {'status':'Access denied'}, 400

        #hard delete
        db.session.delete(qry)
        db.session.commit()
        return {"message":'Deleted'}, 200    

api_cart.add_resource(CartResources, "", "/<int:id>")
