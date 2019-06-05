from models.User import UserModel

def authenticate(username, password):
    usr = UserModel()
    user_result = usr.find_by_username(username)
    if user_result and user_result.authenticate(password):
        return user_result

def identity(payload):
    user_id = payload['identity']
    usr = UserModel()
    return usr.get(user_id)