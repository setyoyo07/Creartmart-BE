import json, hashlib, logging
from . import user, create_token, reset_db
from password_strength import PasswordPolicy
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, user_required
from unittest import mock
from unittest.mock import patch

class TestCheckoutCRUD():
    reset_db()
    # GET Data for checkout page
    def test_checkout_get(self, user):
        token = create_token(is_admin=False)
        data = {}
        res = user.get("/users/checkout/1", query_string=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200

    def test_checkout_post(self, user):
        token = create_token(is_admin=False)
        data = {"courier": "jne", 
        "country": "Indonesia",
        "city_type": "Kota",
        "city_name": "Malang",
        "street": "Jalan Tidar",
        "postal_code":"15510"}
        res = user.post("/users/checkout/1", json=data, headers={"Authorization": "Bearer "+token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
