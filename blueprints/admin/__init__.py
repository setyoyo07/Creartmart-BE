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
import hashlib

blueprint_admin = Blueprint("admin", __name__)
api_admin = Api(blueprint_admin)

#admin resources untuk database user spesifik by id
class AdminUserResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1,
        special=1
    )

    @jwt_required
    @admin_required
    def get(self, id=None): #method untuk request data user,filter by id, input: (user_id di url)
        qry = Users.query.get(id)
        if qry is None:
            return {"message":"NOT FOUND"}, 404
        return [marshal(qry, Users.response_fields)], 200, {"Content-Type": "application/json"}

    @jwt_required
    @admin_required
    def put(self, id=None): #method untuk mengubah status aktif user,filter by id,input: (user_id di url, status di body)
        parser = reqparse.RequestParser()
        parser.add_argument("status", type=inputs.boolean, location="json", required=True)
        args = parser.parse_args()
        user = Users.query.get(id)

        user.status = args["status"]
        user.updated_at = datetime.now()
        db.session.commit()
        return marshal(user, Users.response_fields), 200, {"Content-Type": "application/json"}
        
# Admin Resources untuk semua database user 
class AdminAllUserResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def get(self): #method untuk request semua data user, bisa filter by status
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)
        parser.add_argument('status', location='args', help='invalid filterby value', choices=['true','false'])

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        user = Users.query
        if args['status'] is not None:
            if args['status'] == 'true':
                user = user.filter_by(status=True)
            elif args['status'] == 'false':
                user = user.filter_by(status=False)
            
        rows = []
        for row in user.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Users.response_fields))

        return rows, 200
 
#admin resources untuk database shop spesifik by id
class AdminShopResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def get(self, id=None): #method untuk request data shop,filter by id
        shop = Shops.query.get(id)
        if shop is None:
            return {"message":"NOT FOUND"}, 404
        shop = marshal(shop, Shops.response_fields)
        return [shop], 200, {"Content-Type": "application/json"}

# Admin resources untuk semua database shop 
class AdminAllShopResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def get(self): #method untuk request semua data shop
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        shop = Shops.query
        rows = []
        for row in shop.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Shops.response_fields))

        return rows, 200

#Admin Resources untuk database product
class AdminProductResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def get(self): #method untuk request data semua produk
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        product = Products.query

        rows = []
        for row in product.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Products.response_fields))
        
        return rows, 200

class AdminProductDetailResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def put(self, id=None): # method untuk mengedit data produk, input: (promo, discount, status berada di body )
        
        product = Products.query.filter_by(id=id).first()
        
        parser = reqparse.RequestParser()
        parser.add_argument("promo", type=inputs.boolean, location="json", default=product.promo)
        parser.add_argument("discount", type=int, location="json", default=product.discount)
        parser.add_argument("status", type=inputs.boolean, location="json", default=product.status)
        args = parser.parse_args()

        product.promo = args["promo"]
        product.discount = args["discount"]
        product.status = args["status"]
        product.updated_at = datetime.now()
        db.session.commit()
        return marshal(product, Products.response_fields), 200, {"Content-Type": "application/json"}

#admin resources untuk database transaction detail spesifik by id
class AdminTransactionResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def post(self, id=None): #method untuk mengubah payment status, input: (status di body)
        parser = reqparse.RequestParser()
        parser.add_argument("status", type=inputs.boolean, location="json", required=True)
        args = parser.parse_args()
        
        cart = Carts.query.get(id)
        if cart is None:
            return {"status":"NOT FOUND"}, 404

        cart.payment_status = args["status"]
        cart.updated_at = datetime.now()
        db.session.commit()

        return marshal(cart, Carts.response_fields), 200

    @jwt_required
    @admin_required
    def get(self, id=None): #menthod untuk request data transaksi detail spesifik by cart id
        cart = Carts.query.filter_by(status=False)
        cart = cart.filter_by(id=id).first()
        if cart is None:
            return {"message":"Not Found"}, 404
        transactiondetail = TransactionDetails.query.filter_by(cart_id=id)
        transactiondetail = transactiondetail.all()
        list_td = []
        for td in transactiondetail:
            product = Products.query.filter_by(id=td.product_id).first()
            marshaltd = marshal(td, TransactionDetails.response_fields)
            marshaltd["product_id"] = product.name
            list_td.append(marshaltd)
        shop = Shops.query.get(cart.shop_id)
        user = Users.query.get(cart.user_id)
        marshalCart = marshal(cart, Carts.response_fields)
        marshalCart["user_id"] = user.name
        marshalCart["shop_id"] = shop.name
        return [{"cart":[marshalCart], "transaction_detail": list_td}], 200

# Admin Resources untuk semua database Transaksi detail
class AdminAllTransactionResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def get(self): #method untuk request semua data transaksi detail
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=5)

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']
    
        cart = Carts.query
        cart = cart.filter_by(status=False)
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
            shop = Shops.query.get(qry.shop_id) 
            marshalCart = marshal(qry, Carts.response_fields)
            marshalCart["user_id"] = user.name
            marshalCart["shop_id"] = shop.name
            result.append({"cart":[marshalCart],"transaction_detail":list_td})

        return result, 200

#Admin resources untuk database payment
class AdminPaymentResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200
    @jwt_required
    @admin_required
    def get(self): #method untuk request semua data payment
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Payments.query

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Payments.response_fields))

        return rows, 200
    
    @jwt_required
    @admin_required
    def post(self): #method untuk menambahkan payment method baru, input:(payment_method, account_name, account_number yang berada di body)
        parser = reqparse.RequestParser()
        parser.add_argument('payment_method', location='json', default='')
        parser.add_argument('account_name', location='json', default='')
        parser.add_argument('account_number', location='json', default='')
        args = parser.parse_args()

        payment = Payments(args["payment_method"], args["account_name"], args["account_number"])
        db.session.add(payment)
        db.session.commit()

        return marshal(payment, Payments.response_fields), 200

class AdminPaymentDetailResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @admin_required
    def put(self, id=None): #method untuk mengedit data payment method, input (payment_method, account_name, account_number,status yang berada di body)
        parser = reqparse.RequestParser()
        parser.add_argument('payment_method', location='json', default='')
        parser.add_argument('account_name', location='json', default='')
        parser.add_argument('account_number', location='json', default='')
        parser.add_argument('status', type=inputs.boolean, location='json', default='')
        args = parser.parse_args()

        payment = Payments.query.filter_by(id=id).first()
        payment.payment_method = args["payment_method"]
        payment.account_name = args["account_name"]
        payment.account_number = args["account_number"]
        payment.status = args["status"]
        db.session.commit()

        return marshal(payment, Payments.response_fields), 200

api_admin.add_resource(AdminUserResources, "/users/<int:id>")
api_admin.add_resource(AdminAllUserResources, "/users")
api_admin.add_resource(AdminShopResources, "/shops/<int:id>")
api_admin.add_resource(AdminAllShopResources, "/shops")
api_admin.add_resource(AdminProductResources, "/product")
api_admin.add_resource(AdminProductDetailResources, "/product/<int:id>")
api_admin.add_resource(AdminTransactionResources, "/transaction/<int:id>")
api_admin.add_resource(AdminAllTransactionResources, "/transaction")
api_admin.add_resource(AdminPaymentResources, "/payment")
api_admin.add_resource(AdminPaymentDetailResources, "/payment/<int:id>")