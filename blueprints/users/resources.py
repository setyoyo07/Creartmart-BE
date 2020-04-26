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
from blueprints.carts.model import Carts
import hashlib

blueprint_user = Blueprint("user", __name__)
api_user = Api(blueprint_user)

#users resources
class UserResources(Resource):
    policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1
    )

    def options(self, id=None):
        return {'status':'ok'},200

    @jwt_required
    @user_required
    def get(self): #mengambil data user (user info untuk user yg sedang login)
        user_claims_data = get_jwt_claims()
        qry = Users.query.get(user_claims_data["id"])
        return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}

    @jwt_required
    @user_required
    def put(self): #mengubah data user info
        user_claims_data = get_jwt_claims()
        qry = Users.query.get(user_claims_data["id"])
        parser = reqparse.RequestParser()
        parser.add_argument("username", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        parser.add_argument("name", location="json", default=qry.name)
        parser.add_argument("email", location="json", default=qry.email)
        parser.add_argument("contact", location="json", default=qry.contact)
        parser.add_argument("address", location="json", default=qry.address)
        parser.add_argument("account_number", location="json", default=qry.account_number)
        parser.add_argument("image", location="json", default=qry.image)
        args = parser.parse_args()

        #validasi password
        validation = self.policy.test(args["password"])
        if validation == []:
            pwd_digest = hashlib.md5(args["password"].encode()).hexdigest()
            if qry.username != args["username"]:
                if Users.query.filter_by(username=args["username"]).first() is not None:
                    return {"status": "FAILED", "message": "Username already exists"}, 400, {"Content-Type": "application/json"}
            qry.username = args["username"]
            qry.password = pwd_digest
            qry.name = args["name"]
            qry.email = args["email"]
            qry.contact = args["contact"]
            qry.address = args["address"]
            qry.account_number = args["account_number"]
            qry.image = args["image"]
            qry.updated_at = datetime.now()
            db.session.commit()
            return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}
        return {"status": "FAILED", "message": "Password not valid"}, 400, {"Content-Type": "application/json"}

    @jwt_required
    @user_required
    def delete(self): #deactivate akun user
        user_claims_data = get_jwt_claims()
        qry = Users.query.get(user_claims_data["id"])
        #Check Active Product
        shop = Shops.query.filter_by(user_id=qry.id).first()
        if shop is not None:
            product = Products.query.filter_by(shop_id=shop.id).all()
            for item in product:
                item.status = False
                db.session.commit()    
        qry.status = False
        db.session.commit()
        
        return {"message": "Succesfully Deactivated"}, 200, {"Content-Type": "application/json"}

#users register resources
class UserRegisterResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200

    policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1
    )
    #untuk public tidak perlu token
    def post(self): #mendaftar akun user baru
        parser = reqparse.RequestParser()
        parser.add_argument("username", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        parser.add_argument("email", location="json", required=True)
        parser.add_argument("account_number", location="json", required=True)
        args = parser.parse_args()
        #validasi password
        validation = self.policy.test(args["password"])
        if validation == []:
            pwd_digest = hashlib.md5(args["password"].encode()).hexdigest()
            user = Users(args["username"], pwd_digest, args["email"], args["account_number"])
            if Users.query.filter_by(username=args["username"]).all() != []:
                return {"status": "FAILED", "message": "Username already exists"}, 400, {"Content-Type": "application/json"}
            db.session.add(user)
            db.session.commit()
            return marshal(user, Users.response_fields), 200, {"Content-Type": "application/json"}
        return {"status": "FAILED", "message": "Password is not accepted"}, 400, {"Content-Type": "application/json"}

api_user.add_resource(UserResources, "/info")
api_user.add_resource(UserRegisterResources, "/register")