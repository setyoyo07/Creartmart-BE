import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required

class TestShopsCRUD():
    reset_db()
    #GET shop dan produk oleh user, shop not available
    def test_shop_get_invalid(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/shops", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    # PUT Info Shop
    def test_shop_put(self, user):
        token = create_token(is_admin=False)
        data = {"email": "toko1@gmail.com", 
        "name": "Toko 1",
        "contact": "021",
        "province": "Banten",
        "city_type": "Kabupaten",
        "city_name": "Tangerang",
        "postalcode": "15510",
        "street_address": "Pasar Lama",
        "image": "foto"}
        res = user.put("/users/shops", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    def test_shop_put_invalid_name(self, user):
        token = create_token(is_admin=False)
        data = {"email": "toko1@gmail.com", 
        "name": "Shop 1",
        "contact": "021",
        "province": "Banten",
        "city_type": "Kabupaten",
        "city_name": "Tangerang",
        "postalcode": "15510",
        "street_address": "Pasar Lama",
        "image": "foto"}
        res = user.put("/users/shops", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 400

    # POST Product di shop
    def test_shop_post_product(self, user):
        token = create_token(is_admin=False)
        data = {"name": "LUKISAN1", 
        "price": 100000,
        "image": "link",
        "category": "Art",
        "subcategory": "Paint",
        "description":"New painting",
        "limited":True,
        "stock":1,
        "weight":2000}
        res = user.post("/users/shops/product", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #PUT product di shop
    def test_shop_put_product(self, user):
        token = create_token(is_admin=False)
        data = {"name": "LUKISAN1", 
        "price": 120000,
        "image": "link",
        "category": "Art",
        "subcategory": "Paint",
        "description":"New painting",
        "limited":True,
        "stock":1,
        "weight":2000}
        res = user.put("/users/shops/product/3", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET produk di shop by id
    def test_shop_get_product(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/shops/product/3", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    def test_shop_get_product_invalid(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/shops/product/10", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 404

    #GET shop dan produk oleh user, shop available
    def test_shop_get(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/shops", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #GET shop dan produk oleh public
    def test_publicShop_get(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/public/shops/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # DELETE produk di shop by id
    def test_shop_delete_product(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.delete("/users/shops/product/4", headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

