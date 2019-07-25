#Python standard libraries
import os
import sys
import json
import base64

#Third-party libraries
from flask import redirect, render_template, request, url_for, make_response, jsonify, session, abort, g
import jwt

#internal imports
from audio_od import app
import config
from models import User

@app.route("/user/update", methods=['POST'])
@authentication_required
@check_header
def user_update():
    user = g.user
    user.username = request.form.get('username')
    user.first_name = request.form.get('first-name')
    user.last_name = request.form.get('last-name')
    if isValidEmail(request.form.get('email')):
        user.email = request.form.get('email')
    user.update_user_info()
    return '{"status":"ok"}'


@app.route("/app/user/info", methods=['GET'])
def app_user_info():
    token = request.args.get('token')
    user_id = decode_auth_token(token)
    usr = User.get(user_id)
    return usr.user_profile_info()


@app.route("/app/user/profile/upload", methods=['POST'])
def upload_profile_pic():
    details = request.json
    profile_pic = details.get('profile_pic')
    auth_token = request.args.get('token')
    uid = decode_auth_token(auth_token)
    pic_name = str(uid) + '.jpg'
    with open(os.path.join(UPLOAD_FOLDER, 'profile_pics', pic_name), 'wb') as fh:
        fh.write(base64.b64decode(profile_pic)) 
    return json.dumps({'message' : 'success'}), 200


@app.route("/user/picture", methods=['GET'])
@authentication_required
@check_header
def get_profile():
    if (g.user is None):
        abort(403)
    return g.user.get_profile_pic_base64()



@app.route("/user/picture", methods=['POST'])
@authentication_required
@check_header
def put_profile():
    filename = ''
    file = request.files['picture']
    if file.filename == '':
        return '{"status" : "error"}'
    if file and allowed_file(file):
        filename = str(getUid()) + ".jpg"
        file.save(os.path.join(UPLOAD_FOLDER, 'profile_pics', filename))
        return '{"status":"ok"}'
    return '{"status" : "error"}'


@app.route("/dashboard")
@authentication_required
@check_header
def dashboard():
    stories = Story.story_list_by_creatordate(g.uid)
    return render_template("/dash/index.html", stories=stories, base_url="")


@app.route('/dashboard/<path:page>')
@authentication_required
@check_header
def dashboard_full(page):
    stories = Story.story_list_by_creatordate(g.uid)
    base_url = base64.b64encode(request.full_path[10:].encode()).decode("utf-8")
    print(base_url)
    return render_template("/dash/index.html", stories=stories, base_url=base_url)


@app.route("/dash/story")
@authentication_required
@check_header
def dash_story():
    stories = Story.story_list_by_creatordate(g.uid)
    return render_template("/dash/story.html", stories=stories)


@app.route("/dash/share")
@authentication_required
@check_header
def dash_share():
    stories = Story.story_shares_by_uid(g.user.user_id)
    return render_template("/dash/story.html", stories=stories)


@app.route("/dash/user")
@authentication_required
@check_header
def dash_user():
    userimage = g.user.get_profile_pic_base64().decode("utf-8")
    return render_template("/dash/user.html", userimage=userimage)


@app.route("/app/library/", methods=['GET'])
def stories_show_owned_by_user():
    user_id = decode_auth_token(request.args.get("auth"))
    return Story.json_story_library(user_id)
