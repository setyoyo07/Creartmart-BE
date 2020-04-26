import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required

class TestHistoryCRUD():
    reset_db()
    # POST History Transaksi dengan menambahkan payment method
    def test_history_order_post(self, user):
        token = create_token(is_admin=False)
        data = {"payment_id": 1}
        res = user.post("/users/history/order/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

        data = {"payment_id": 1}
        res = user.post("/users/history/order/100", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 404

    # GET Order History
    def test_order_history_get_all(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/history/order", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_order_history_get_id(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/history/order/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET Invalid Seller History
    def test_seller_history_get_all(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/history/seller", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 404
    
    def test_seller_history_get_id(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/history/seller/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 404

    #GET Valid Seller History
    def test_seller_history_get_all(self, user):
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
        
        data = {"name": "LUKISAN2", 
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
        
        data = {"product_id": 3, 
        "quantity": 1}
        res = user.post("/users/carts", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        
        data = {}
        res = user.get("/users/history/seller", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_seller_history_get_id(self, user):
        token = create_token(is_admin=False)        
        data = {"payment_id": 1}
        res = user.post("/users/history/order/2", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        
        res = user.get("/users/history/seller/2", headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #GET transaction history (ADMIN)
    def test_admin_get_transaction(self, user):
        token = create_token(is_admin=True)
        data = {}
        res = user.get("/admin/transaction", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_admin_get_transaction_id(self, user):
        token = create_token(is_admin=True)
        data = {}
        res = user.get("/admin/transaction/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    #POST Payment Validation (ADMIN)
    def test_admin_post_validation(self, user):
        token = create_token(is_admin=True)
        data = {"status": False}
        res = user.post("/admin/transaction/1", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

        data = {"status": True}
        res = user.post("/admin/transaction/1", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200