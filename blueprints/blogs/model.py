from blueprints import db
from flask_restful import fields
from datetime import datetime


class Blogs(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), default='')
    thumbnail = db.Column(db.String(255), default='')
    article = db.Column(db.String(255), default='')
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "title": fields.String,
        "thumbnail": fields.String,
        "article": fields.String,
        "status": fields.Boolean
    }

    def __init__(self, title, thumbnail, article):
        self.title = title
        self.thumbnail = thumbnail
        self.article = article
        
    def __repr__(self):
        return "<Blogs %r>" % self.id