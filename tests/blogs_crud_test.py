import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required

class TestBlogCRUD():
    reset_db()
    # POST Blog
    def test_blog_post(self, user):
        token = create_token(is_admin=False)
        data = {"title": "Judul Blog", 
        "thumbnail": "image",
        "article": "LoremIpsum",}
        res = user.post("/public/blogs", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET Data Blog
    def test_blog_get(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/public/blogs", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_blog_get_id(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/public/blogs/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # PUT data blog
    def test_blog_put(self, user):
        token = create_token(is_admin=False)
        data = {"title": "ganti judul"}
        res = user.put("/public/blogs/1", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # DELETE METHOD
    def test_blog_delete(self, user):
        token = create_token(is_admin=False)
        res = user.delete("/public/blogs/1", headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
