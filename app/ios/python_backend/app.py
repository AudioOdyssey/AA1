from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister

app = Flask(__name__)

app.secret_key = b'-\x97P\xe7\xebx\xa3\xa3U\x12.\xb8\xf58\xc6Byx\x10\xcavoq\xad'

api = Api(app)

jwt = JWT(app, authenticate, identity)

api.add_resource(UserRegister, '/register')