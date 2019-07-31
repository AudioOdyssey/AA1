#Python standard libraries
import os
import sys
import json
import base64

#Third-party libraries
from flask import redirect, render_template, request, url_for, abort, g, Blueprint

#internal imports
from audio_od import app
from models import User, Story
from audio_od.utils import authentication_required, check_header

userprofile = Blueprint("Users", __name__)

@userprofile.route("/user/update", methods=['POST'])
@authentication_required
@check_header
def user_update():
    user = g.user
    user.username = request.form.get('username', '')
    user.first_name = request.form.get('first-name', '')
    user.last_name = request.form.get('last-name', '')
    if isValidEmail(request.form.get('email', '')):
        user.email = request.form.get('email')
    user.update_user_info()
    return '{"status":"ok"}'


@userprofile.route("/app/user/info", methods=['GET'])
def app_user_info():
    token = request.args.get('token')
    user_id = decode_auth_token(token)
    usr = User.get(user_id)
    return usr.user_profile_info()


@userprofile.route("/app/user/profile/upload", methods=['POST'])
def upload_profile_pic():
    details = request.json
    profile_pic = details.get('profile_pic')
    auth_token = request.args.get('token')
    uid = decode_auth_token(auth_token)
    pic_name = str(uid) + '.jpg'
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics', pic_name), 'wb') as fh:
        fh.write(base64.b64decode(profile_pic)) 
    return json.dumps({'message' : 'success'}), 200


@userprofile.route("/user/picture", methods=['GET'])
@authentication_required
@check_header
def get_profile():
    if (g.user is None):
        abort(403)
    return g.user.get_profile_pic_base64()



@userprofile.route("/user/picture", methods=['POST'])
@authentication_required
@check_header
def put_profile():
    filename = ''
    file = request.files['picture']
    if file.filename == '':
        return '{"status" : "error"}'
    if file and allowed_file(file):
        filename = str(getUid()) + ".jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics', filename))
        return '{"status":"ok"}'
    return '{"status" : "error"}'


@userprofile.route("/app/library/", methods=['GET'])
def stories_show_owned_by_user():
    user_id = decode_auth_token(request.args.get("auth"))
    return Story.json_story_library(user_id)


@userprofile.route("/help")
@check_header
def index_help():
    return render_template("help/index.html")