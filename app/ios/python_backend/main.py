from flask_restful import Resource, reqparse
from models.user import UserModel

parser = reqparse.RequestParser()
parser.add_argument('username',
    type=str,
    required=True,
    help="This field cannot be left blank.")

parser.add_argument('password', 
    type=str,
    required=True,
    help="This field cannot be left blank.")


