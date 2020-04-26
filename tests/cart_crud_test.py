import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required

class TestCartCRUD():
    reset_db()
    # POST Cart
    def test_cart_post(self, user):
        token = create_token(is_admin=False)
        data = {"product_id": 1, 
        "quantity": 1}
        res = user.post("/users/carts", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # GET Cart 
    def test_cart_get(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/carts", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # Delete Cart 
    def test_cart_delete(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.delete("/users/carts/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
 