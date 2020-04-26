import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required

class TestAdminCRUD():
    reset_db()
    # GET Users
    def test_admin_users_get(self, user):
        token = create_token(is_admin=True)
        data = {}
        res = user.get("/admin/users/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_admin_users_get_invalid(self, user):
        token = create_token(is_admin=True)
        data = {}
        res = user.get("/admin/users/100", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 404

    def test_admin_allusers_get(self, user):
        token = create_token(is_admin=True)
        data = {"status":"true"}
        res = user.get("/admin/users", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    def test_admin_nonactiveusers_get(self, user):
        token = create_token(is_admin=True)
        data = {"status":"false"}
        res = user.get("/admin/users", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
        
    # PUT Users
    def test_admin_users_put(self, user):
        token = create_token(is_admin=True)
        data = {"status": True}
        res = user.put("/admin/users/1", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #GET shop by id
    def test_admin_get_shop(self, user):
        token = create_token(is_admin=True)
        data = {'status':'true'}
        res = user.get("/admin/shops", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
        data = {'status':'false'}
        res = user.get("/admin/shops", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_admin_get_shop_id(self, user):
        token = create_token(is_admin=True)
        data = {}
        res = user.get("/admin/shops/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #GET all product
    def test_admin_get_product(self, user):
        token = create_token(is_admin=True)
        data = {}
        res = user.get("/admin/product", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    # PUT info produk
    def test_admin_put_product(self, user):
        token = create_token(is_admin=True)
        data = {"status": True,
        "promo":True,
        "discount":30}
        res = user.put("/admin/product/2", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #POST Payment Method
    def test_admin_post_payment(self, user):
        token = create_token(is_admin=True)
        data = {"payment_method": "Bank Transfer", 
        "account_name": "Bank BCA atas nama PT Creart",
        "account_number": "123456789"}
        res = user.post("/admin/payment", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #PUT Payment Method
    def test_admin_put_payment(self, user):
        token = create_token(is_admin=True)
        data = {"payment_method": "Bank Transfer", 
        "account_name": "Bank BCA atas nama PT Creart",
        "account_number": "1234567",
        "status":True}
        res = user.put("/admin/payment/1", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    