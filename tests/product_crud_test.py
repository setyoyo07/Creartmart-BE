import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required

class TestBlogCRUD():
    reset_db()

    # GET Semua Data Produk filter harga
    def test_product_get_sort_price(self, user):
        token = create_token(is_admin=False)
        data = {"category": "Art",
        "subcategory": "paint",
        "order_by": "price"}
        res = user.get("/public/products", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    # GET Semua Data Produk filter terlaris
    def test_product_get_sort_sold(self, user):
        token = create_token(is_admin=False)
        data = {"category": "Art",
        "subcategory": "paint",
        "order_by": "sold"}
        res = user.get("/public/products", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #GET produk by id
    def test_product_get_id(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/public/products/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET Semua Data Produk fitur limited
    def test_product_get_limited(self, user):
        token = create_token(is_admin=False)
        data = {"order_by": "price"}
        res = user.get("/public/products/limited", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET Semua Data Produk fitur popular
    def test_product_get_popular(self, user):
        token = create_token(is_admin=False)
        data = {"order_by": "price"}
        res = user.get("/public/products/popular", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET Semua Data Produk fitur promo
    def test_product_get_promo(self, user):
        token = create_token(is_admin=False)
        data = {"order_by": "price"}
        res = user.get("/public/products/promo", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET Semua Data Produk fitur search
    def test_product_get_search(self, user):
        token = create_token(is_admin=False)
        data = {"keyword": "luki"}
        res = user.get("/public/products/search", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

