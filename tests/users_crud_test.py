import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required

class TestUserCRUD():
    reset_db()
    # GET METHOD
    def test_user_get(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/info", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    # PUT METHOD
    def test_user_put(self, user):
        token = create_token(is_admin=False)
        data = {"username": "user1 (edited)", 
        "password": "Alta@123"}
        res = user.put("/users/info", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    def test_user_put_invalid_username(self, user):
        token = create_token(is_admin=False)
        data = {"username": "user2", "password": "Alta@123"}
        res = user.put("/users/info", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 400

    def test_user_put_invalid_password(self, user):
        token = create_token(is_admin=False)
        data = {"username": "user1", "password": "Alta"}
        res = user.put("/users/info", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 400

    # DELETE METHOD
    def test_user_delete(self, user):
        token = create_token(is_admin=False)
        res = user.delete("/users/info", headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    # POST METHOD
    def test_user_register(self, user):
        token = create_token(is_admin=False)
        data = {"username": "user4", 
        "password": "Alta@123",
        "name": "D",
        "email": "D@email.com",
        "account_number": "123"}
        res = user.post("/users/register", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    def test_user_register_password_invalid(self, user):
        token = create_token(is_admin=False)
        data = {"username": "user4", 
        "password": "Alta123",
        "name": "D",
        "email": "D@email.com",
        "account_number": "123"}
        res = user.post("/users/register", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 400

    def test_user_register_username_invalid(self, user):
        token = create_token(is_admin=False)
        data = {"username": "user2", 
        "password": "Alta@123",
        "name": "D",
        "email": "D@email.com",
        "account_number": "123"}
        res = user.post("/users/register", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 400