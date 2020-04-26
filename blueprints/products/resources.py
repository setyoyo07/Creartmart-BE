from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required
from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from blueprints.products.model import Products
from blueprints.shops.model import Shops
import hashlib

blueprint_product = Blueprint("products", __name__)
api_product = Api(blueprint_product)

#product resources
class ProductResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    def get(self): #mengambil data semua produk, filter by category dan subcategory
        parser = reqparse.RequestParser()
        parser.add_argument("category", location="args")
        parser.add_argument("subcategory", location="args")
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)
        parser.add_argument('order_by', location='args', help='invalid orderby value', choices=['price','sold'])

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Products.query
        qry = qry.filter_by(status=True)

        if args['category'] is not None:
            qry = qry.filter_by(category=(args['category']))

        if args['subcategory'] is not None:
            qry = qry.filter_by(subcategory=args['subcategory'])

        qry = qry.order_by(desc(Products.created_at))
        if args['order_by'] is not None:
            if args['order_by'] == 'price':
                qry = qry.order_by(Products.price)
            elif args['order_by'] == 'sold':
                qry = qry.order_by(desc(Products.sold))

        rows = []
        i = 0
        for row in qry.limit(args['rp']).offset(offset).all():
            shop = Shops.query.filter_by(id=row.shop_id).first()
            marshalShop = marshal(shop, Shops.response_fields)
            rows.append(marshal(row, Products.response_fields))
            rows[i]["shop_id"]=marshalShop
            i+=1
        
        return rows, 200

#Product Detail resources
class ProductDetailResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    def get(self, id=None): #mengambil data produk spesifik by id
        product = Products.query
        qry = product.filter_by(id=id).first()
        if qry is not None:
            shop = Shops.query.filter_by(id=qry.shop_id).first()
            marshalProduct = marshal(qry, Products.response_fields)

            return marshalProduct, 200
        return {'status':'NOT_FOUND'}, 404

#limited product resources
class ProductLimitedResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    def get(self): #mengambil data produk dengan fitur limited
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)
        parser.add_argument('order_by', location='args', help='invalid orderby value', choices=['price'])

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Products.query.filter_by(limited=True)
        qry = qry.filter_by(status=True)
        qry = qry.order_by(desc(Products.created_at))
        if args['order_by'] is not None:
            if args['order_by'] == 'price':
                qry = qry.order_by(Products.price)
            
        rows = []
        i = 0
        for row in qry.limit(args['rp']).offset(offset).all():
            shop = Shops.query.filter_by(id=row.shop_id).first()
            marshalShop = marshal(shop, Shops.response_fields)
            rows.append(marshal(row, Products.response_fields))
            rows[i]["shop_id"]=marshalShop
            i+=1
        return rows, 200

#popular product resources
class ProductPopularResources(Resource):
    def options(self, id=None):
            return {'status':'ok'},200

    def get(self): #mengambil data produk yang paling sering dibeli
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)
        parser.add_argument('order_by', location='args', help='invalid orderby value', choices=['price'])

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Products.query.order_by(desc(Products.sold))
        qry = qry.filter_by(status=True)
        if args['order_by'] is not None:
            if args['order_by'] == 'price':
                qry = qry.order_by(Products.price)
            
        rows = []
        i = 0
        for row in qry.limit(args['rp']).offset(offset).all():
            shop = Shops.query.filter_by(id=row.shop_id).first()
            marshalShop = marshal(shop, Shops.response_fields)
            rows.append(marshal(row, Products.response_fields))
            rows[i]["shop_id"]=marshalShop
            i+=1
        return rows, 200

#promo product resouces
class ProductPromoResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    def get(self): #mengambil data yang memiliki promo discount
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)
        parser.add_argument('order_by', location='args', help='invalid orderby value', choices=['price'])

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Products.query.filter_by(promo = True)
        qry = qry.filter_by(status=True)
        qry = qry.order_by(desc(Products.created_at))
        if args['order_by'] is not None:
            if args['order_by'] == 'price':
                qry = qry.order_by(Products.price)
            
        rows = []
        i = 0
        for row in qry.limit(args['rp']).offset(offset).all():
            shop = Shops.query.filter_by(id=row.shop_id).first()
            marshalShop = marshal(shop, Shops.response_fields)
            rows.append(marshal(row, Products.response_fields))
            rows[i]["shop_id"]=marshalShop
            i+=1
        return rows, 200

class ProductSearchResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    def get(self): #mengambil data semua produk, filter by category dan subcategory
        parser = reqparse.RequestParser()
        parser.add_argument("keyword", location="args")
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)
        parser.add_argument('order_by', location='args', help='invalid orderby value', choices=['price','sold'])

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        if args['keyword'] is not None:
            product = Products.query.filter(Products.name.like("%"+args['keyword']+"%") |
            Products.category.like("%"+args['keyword']+"%") | Products.subcategory.like("%"+args['keyword']+"%") |
            Products.description.like("%"+args['keyword']+"%"))

        product = product.filter_by(status=True)

        product = product.order_by(desc(Products.created_at))
        if args['order_by'] is not None:
            if args['order_by'] == 'price':
                product = product.order_by(Products.price)
            elif args['order_by'] == 'sold':
                product = product.order_by(desc(Products.sold))

        rows = []
        i = 0
        for row in product.limit(args['rp']).offset(offset).all():
            shop = Shops.query.filter_by(id=row.shop_id).first()
            marshalShop = marshal(shop, Shops.response_fields)
            rows.append(marshal(row, Products.response_fields))
            rows[i]["shop_id"]=marshalShop
            i+=1
        
        return rows, 200

api_product.add_resource(ProductResources, "")
api_product.add_resource(ProductDetailResources, "/<int:id>")
api_product.add_resource(ProductLimitedResources, "/limited")
api_product.add_resource(ProductPopularResources, "/popular")
api_product.add_resource(ProductPromoResources, "/promo")
api_product.add_resource(ProductSearchResources, "/search")