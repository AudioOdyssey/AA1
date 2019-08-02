#Python standard libraries
import os
import sys
import json
import base64

#Third-party libraries
from flask import redirect, render_template, request, url_for, abort, g, Blueprint

#internal imports
from audio_od import app
from audio_od.models import User, Story
from audio_od.utils import authentication_required, check_header, isValidEmail, check_invalid_app_token

userprofile = Blueprint("Users", __name__)

@userprofile.route("/user/update", methods=['POST'])
@authentication_required
@check_header
def user_update():
    """Endpoint for allowing users to edit their own profile info. If successful, will return a status."""
    user = g.user
    user.username = request.form.get('username', '')
    user.first_name = request.form.get('first-name', '')
    user.last_name = request.form.get('last-name', '')
    if isValidEmail(request.form.get('email', '')):
        user.email = request.form.get('email')
    user.update_user_info()
    return '{"status":"ok"}'


valid_mimetypes = ['image/jpeg', 'image/png', 'image/bmp']


def allowed_file(file):
    mimetype = file.content_type
    return mimetype in valid_mimetypes


@userprofile.route("/app/user/info", methods=['GET'])
def app_user_info():
    """Sends the app all the user info in a json"""
    token = request.args.get('token')
    if check_invalid_app_token(token):
        return '{"status": "error"}'
    user_id = decode_auth_token(token)
    usr = User.get(user_id)
    return usr.user_profile_info()


@userprofile.route("/app/user/profile/upload", methods=['POST'])
def upload_profile_pic():
    """Allows users in the app to upload a profile picture"""
    details = request.json
    profile_pic = details.get('profile_pic')
    auth_token = request.args.get('token')
    token = request.args.get('token')
    if check_invalid_app_token(token):
        return '{"status": "error"}'
    uid = decode_auth_token(auth_token)
    if file and allowed_file(file):
        pic_name = str(uid) + '.jpg'
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics', pic_name), 'wb') as fh:
            fh.write(base64.b64decode(profile_pic)) 
        return json.dumps({'message' : 'success'}), 200
    return '{"status" : "error"}', 404

@userprofile.route("/user/picture", methods=['GET'])
@authentication_required
@check_header
def get_profile():
    """This endpoint returns the profile picture"""
    if (g.user is None):
        abort(403)
    return g.user.get_profile_pic_base64()



@userprofile.route("/user/picture", methods=['POST'])
@authentication_required
@check_header
def put_profile():
    """Allows users to upload profile pictures. If the profile picture is valid then the picture will be uploaded. If not an error will be returned"""
    filename = ''
    file = request.files['picture']
    if file.filename == '':
        return '{"status" : "error"}'
    if file and allowed_file(file):
        filename = str(g.uid) + ".jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics', filename))
        return '{"status":"ok"}'
    return '{"status" : "error"}'


@userprofile.route("/app/library/", methods=['GET'])
def stories_show_owned_by_user():
    """Returns all the stories an owner owns"""
    token = request.args.get('auth')
    if check_invalid_app_token(token):
        return '{"status": "error"}'
    user_id = decode_auth_token(request.args.get("auth"))
    return Story.json_story_library(user_id)


@userprofile.route("/app/purchase/story", methods=['POST'])
def app_purchase_story():
    token = request.args.get("token")
    if check_invalid_app_token(token):
        return '{"status": "error"}'
    uid = decode_auth_token(token)
    if uid:
        story = Story.get(request.args.get("story_id"))
        if story is None:
            return '{"status" : "Story does not exist."}'
        else:
            story.mark_purchased(uid)
            return '{"status" : "success"}'
    else:
        return '{"status" : "User does not exist."}'