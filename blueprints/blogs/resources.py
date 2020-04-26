from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required
from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from blueprints.blogs.model import Blogs
import hashlib

blueprint_blogs = Blueprint("blogs", __name__)
api_blogs = Api(blueprint_blogs)

#Blog resources
class BlogResources(Resource):

    def get(self): #mengambil semua data blog
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=20)
        
        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Blogs.query

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Blogs.response_fields))

        return rows, 200

    def post(self): #POSTING ARTICLE DI BLOG
        parser = reqparse.RequestParser()
        parser.add_argument('title', location='args', default='')
        parser.add_argument('thumbnail', location='args', default='')
        parser.add_argument('article', location='args', default='')
    
        args = parser.parse_args()

        blog = Blogs(args["title"], args["thumbnail"], args["article"])
        db.session.add(blog)
        db.session.commit()

        return marshal(blog, Blogs.response_fields), 200

#Blog Detail resources
class BlogDetailResources(Resource):
    
    def get(self, id=None): #mengambil data blog spesifik by id
        blog = Blogs.query
        qry = blog.get(id)
        if qry is not None:
            return marshal(qry, Blogs.response_fields), 200
        return {'status':'NOT_FOUND'}, 404

    def put(self, id=None): #mengubah data blog
        blog = Blogs.query.get(id)
        
        parser = reqparse.RequestParser()
        parser.add_argument('title', location='args', default=blog.title)
        parser.add_argument('thumbnail', location='args', default=blog.thumbnail)
        parser.add_argument('article', location='args', default=blog.article)
    
        args = parser.parse_args()

        blog.title = args["title"]
        blog.thumbnail = args["thumbnail"]
        blog.article = args["article"]
        db.session.commit()

        return marshal(blog, Blogs.response_fields), 200

    def delete(self, id=None):
        blog = Blogs.query
        qry = blog.get(id)

        if qry is None:
            return {'status':'NOT_FOUND'}, 404

        #hard delete
        db.session.delete(qry)
        db.session.commit()
        return 'Deleted', 200

api_blogs.add_resource(BlogResources, "")
api_blogs.add_resource(BlogDetailResources, "/<int:id>")
