from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from datetime import timedelta
from functools import wraps
from flask_cors import CORS
import json, random, string, os

app = Flask(__name__) # membuat semua blueprint
app.config["APP_DEBUG"] = True
CORS(app)
# JWT Config
app.config["JWT_SECRET_KEY"] = "".join(random.choice(string.ascii_letters) for i in range(32))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# SQLAlchemy Config
try:
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/rest_portofolio_test'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/rest_portofolio_test'
except Exception as e:
    raise e

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

#admin & non-admin authorization
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"status": "FORBIDDEN", "message": "You should be an admin to access this point"}, 403
        return fn(*args, **kwargs)
    return wrapper

def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims["is_admin"]:
            return {"status": "FORBIDDEN", "message": "You should be a user to access this point"}, 403
        return fn(*args, **kwargs)
    return wrapper


@app.after_request
def after_request(response):
    try:
        request_data = request.get_json()
    except:
        request_data = request.args.to_dict()
    if response.status_code == 200:
        app.logger.info("REQUEST_LOG\t%s", json.dumps({
            "method": request.method,
            "code": response.status,
            "request": request_data,
            "response": json.loads(response.data.decode("utf-8"))
        }))
    else:
        app.logger.error("REQUEST_LOG\t%s", json.dumps({
            "method": request.method,
            "code": response.status,
            "request": request_data,
            "response": json.loads(response.data.decode("utf-8"))
        }))
    return response

from blueprints.login import blueprint_login
from blueprints.users.resources import blueprint_user
from blueprints.shops.resources import blueprint_shop, blueprint_public_shop
from blueprints.products.resources import blueprint_product
from blueprints.blogs.resources import blueprint_blogs
from blueprints.carts.resources import blueprint_cart
from blueprints.checkout import blueprint_checkout
from blueprints.history import blueprint_history
from blueprints.admin import blueprint_admin

app.register_blueprint(blueprint_login, url_prefix="/users/login")
app.register_blueprint(blueprint_user, url_prefix="/users")
app.register_blueprint(blueprint_shop, url_prefix="/users/shops")
app.register_blueprint(blueprint_public_shop, url_prefix="/public/shops")
app.register_blueprint(blueprint_product, url_prefix="/public/products")
app.register_blueprint(blueprint_blogs, url_prefix="/public/blogs")
app.register_blueprint(blueprint_cart, url_prefix="/users/carts")
app.register_blueprint(blueprint_checkout, url_prefix="/users/checkout")
app.register_blueprint(blueprint_history, url_prefix="/users/history")
app.register_blueprint(blueprint_admin, url_prefix="/admin")

db.create_all()
