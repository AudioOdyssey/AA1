from flask_restful import Resource, reqparse
from models.User import UserModel

from datetime import date

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="This field cannot be left blank."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="This field cannot be left blank."
    )
    parser.add_argument('first_name',
        type=str,
        required=True,
        help="This field cannot be left blank.")
    parser.add_argument('last_name',
        type=str,
        required=True,
        help="This field cannot be left blank.")
    parser.add_argument('email_address',
        type=str,
        required=True,
        help="This field cannot be left blank.")
    parser.add_argument('birthDate',
        type=date,
        required=True,
        help="This field cannot be left blank")

    def post(self):
        data = UserRegister.parser.parse_args()

        result = UserModel()
        if result.find_by_username(data['usernameTextField']):
            return {"message": "User already exists"}, 400
        
        user = UserModel(username_input = data['usernameTextField'], password_input = data['passwordTextField'])
        user.add_to_server()

        return {"message": "User created successfully."}, 201
        

    