import pytest, logging, hashlib, json
from flask import Flask, request
from app import cache
from blueprints import app, db
from blueprints.users.model import Users
from blueprints.products.model import Products
from blueprints.carts.model import Carts, Payments
from blueprints.address.model import Addresses
from blueprints.blogs.model import Blogs
from blueprints.shops.model import Shops
from blueprints.transaction_details.model import TransactionDetails

def call_user(request):
    user = app.test_client()
    return user

def reset_db():
    db.drop_all()
    db.create_all()
    user1 = Users("user1", hashlib.md5("Alta@123".encode()).hexdigest(), "A@email.com", "123")
    user2 = Users("user2", hashlib.md5("Alta@123".encode()).hexdigest(), "B@email.com", "456")
    user3 = Users("user3", hashlib.md5("Alta@123".encode()).hexdigest(), "C@email.com", "789")
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

    shop1 = Shops(user2.id)
    shop1.email = "shop1@email.com"
    shop1.name = "Shop 1"
    shop1.contact = "02199999"
    shop1.province = "Banten"
    shop1.city_type = "Kota"
    shop1.city_name = "Tangerang"
    shop1.postalcode = "15510"
    db.session.add(shop1)
    db.session.commit()

    product1 = Products(shop1.id, "lukisan", 50000, "Art", "Paint", "link", True, "", 1, 2000)
    product2 = Products(shop1.id, "lukisan2", 10000, "Art", "Paint", "link", False, "", 10, 2000)
    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()
    
@pytest.fixture
def user(request):
    return call_user(request)

def create_token(is_admin=True):
    if is_admin: cache_user = "test_token_admin"
    else: cache_user = "test_token_nonadmin"
    token = cache.get(cache_user)
    if token is None:
        # prepare request input
        if is_admin:
            data = {
                "username": "admin",
                "password": "Admin@creart"
            }
        else:
            data = {
                "username": "user1",
                "password": "Alta@123"
            }
        # do request
        req = call_user(request)
        res = req.post("/users/login", json=data)
        # store response
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        # compare with expected result
        assert res.status_code == 200
        assert res_json["message"] == "Token is successfully created"
        # save token into cache
        cache.set(cache_user, res_json["token"], timeout=30)
        # return
        return res_json["token"]
    return token