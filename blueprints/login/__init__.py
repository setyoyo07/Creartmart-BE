from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token
from blueprints.users.model import Users
import hashlib

blueprint_login = Blueprint("login", __name__)
api = Api(blueprint_login)

#login / create token resources
class CreateTokenResources(Resource):
    def options(self, id=None):
        return {'status':'ok'},200
         
    def post(self): #method untuk login dan mengambil token
        parser = reqparse.RequestParser()
        parser.add_argument("username", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        args = parser.parse_args()
        password = hashlib.md5(args["password"].encode()).hexdigest()
        if args["username"] == "admin" and args["password"] == "Admin@creart":
            user_claims_data = {}
            user_claims_data["is_admin"] = True
        else:
            qry = Users.query.filter_by(username=args["username"])
            qry = qry.filter_by(password=password)
            qry = qry.filter_by(status=True).first()
            if qry is None:
                return {"status": "UNAUTHORIZED", "message": "Invalid username or password"}, 401, {"Content-Type": "application/json"}
            user_claims_data = marshal(qry, Users.jwt_claim_fields)
            user_claims_data["is_admin"] = False
        token = create_access_token(identity=args["username"], user_claims=user_claims_data)
        return {"token": token, "admin":user_claims_data["is_admin"], "message": "Token is successfully created"}, 200, {"Content-Type": "application/json"}

api.add_resource(CreateTokenResources, "")