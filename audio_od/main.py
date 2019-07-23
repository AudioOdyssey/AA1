#Python standard libraries
import os
import sys
import random
import hashlib
import binascii
import json
from datetime import datetime, timedelta
from functools import wraps
import base64
import re
from urllib.request import (
    urlopen, urlparse, urlunparse, urlretrieve)

#Third-party libraries
from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify, session, flash, send_from_directory, abort, g
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, login_url
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename
import pymysql
import pymysql.cursors
import jwt
from oauthlib.oauth2 import WebApplicationClient
import requests
from bs4 import BeautifulSoup as bs

#Internal imports
import config
from models import *


ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.secret_key = config.secret_key  
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "session/new.html"
login_manager.login_message = "Please login"

app.config['MAIL_SERVER'] = config.mail_server
app.config['MAIL_PORT'] = config.mail_port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.mail_name
app.config['MAIL_PASSWORD'] = config.mail_pass
mail = Mail(app)

UPLOAD_FOLDER = config.upload_folder

# oauth = OAuth(app)

GOOGLE_CLIENT_ID=config.google_client_id
GOOGLE_CLIENT_SECRET=config.google_client_secret
GOOGLE_DISCOVERY_URL="https://accounts.google.com/.well-known/openid-configuration"

FACEBOOK_APP_ID=config.facebook_client_id
FACEBOOK_APP_SECRET=config.facebook_client_secret


random.seed()

# refresh_t = None

def authentication_required(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        remember = request.cookies.get('remember_')
        if remember is None:
            token = session.get('token')
            if token is None or decode_auth_token(token) == 0:
                return redirect(url_for('session_new'))
            else:
                return func(*args, **kwargs)
        else:
            uid = decode_auth_token(remember)
            if uid == 'Invalid token. please log in again' or uid == 0 or uid == "Signature expired. Please log in again.":
                return redirect(url_for('session_new'))
            return func(*args, **kwargs)
    return func_wrapper
# google_blueprint = make_google_blueprint(client_id=config.google_client_id, client_secret=config.google_client_secret, scope=["profile","email"])

# app.register_blueprint(google_blueprint, url_prefix='/google_login'

google_client=WebApplicationClient(GOOGLE_CLIENT_ID)


def check_header(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        g.uid = getUid()
        if g.uid == 'Invalid token. please log in again':
            g.uid = 0
            g.user = None
            return func(*args, **kwargs)
        g.user = User.get(g.uid)
        return func(*args, **kwargs)
    return func_wrapper


@app.route("/")
@app.route("/home")
@app.route("/index")
@check_header
def home():
    auth_token = request.cookies.get('remember_')
    if auth_token is None:
        token = session.get('token')
        if token is None or not decode_auth_token(token):
            return render_template("index.html")
        else:
            return redirect(url_for('dash_story_full'))
    else:
        user_id = decode_auth_token(auth_token)
        if user_id == 'Signature expired. Please log in again.' or user_id == 0:
            return render_template('index.html')
        else:
            return redirect(url_for('dash_story_full'))
    return render_template('index.html')


@app.route("/user/new", methods=['GET', 'POST'])
@check_header
def user_new():  # fix later
    if request.method == "POST":
        details = request.form
        username = details['username']
        raw_password = details['password']
        if len(raw_password) < 8:
            return render_template("user/new.html", error="Please enter a password greater than 8 characters.")
        email = details['email_address']
        if not isValidEmail(email):
            return render_template("user/new.html", error="Invalid email")
        gender = int(details['gender'])
        country_of_origin = (details.get('country_of_origin'))
        profession = details['profession']
        disabilities = details.get('disabilities')
        if disabilities is None:
            disabilities_bool = 0
        else:
            disabilities_bool = 1
        language = int(details['language-id'])
        first_name = details['first_name']
        last_name = details['last_name']
        date_of_birth = datetime.strptime(
            details['birth-year'] + "-" + details['birth-month'] + "-" + details['birth-day'], '%Y-%m-%d')
        usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin,
                   profession_input=profession, disabilities_input=disabilities_bool, date_of_birth_input=date_of_birth,
                   first_name_input=first_name, last_name_input=last_name, language=language)
        result = usr.add_to_server()
        if result==-1:
            return render_template("user/new.html", error="Username already in use")
        elif result==-2:
            return render_template("user/new.html", error="Email already in use")
        else:
            return redirect(url_for("home"))
    return render_template("user/new.html")


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


def isValidEmail(email):
    if len(email) > 7:
        if re.match(r"^.+@(\[?)[a-zA-Z0-9-.]+.(([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email) != None:
            return True
    return False
    
    
@app.route("/app/user/new", methods=['POST', 'GET'])
def app_user_new():
    result = {}
    if request.method == "POST":
        details = request.get_json(force=True)
    return make_response(sign_up(details))


def sign_up(details_dict):
    username = details_dict['username']
    raw_password = details_dict['password']
    email = details_dict['email_address']
    gender = int(details_dict['gender'])
    country_of_origin = details_dict['country_of_origin']
    profession = details_dict['profession']
    disabilities = bool(details_dict['disabilities'])
    if disabilities:
        disabilities_bool = 1
    else:
        disabilities_bool = 0
    language = int(details_dict['language_id'])
    first_name = details_dict['first_name']
    last_name = details_dict['last_name']
    # date_of_birth = datetime.strptime(details_dict['date_of_birth'], '%Y-%m-%d')
    usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin,
               profession_input=profession, disabilities_input=disabilities_bool,
               first_name_input=first_name, last_name_input=last_name, language=language)
    result=usr.add_to_server()
    if result==-1:
        return json.dumps({"message" : "username already exists"})
    elif result==-2:
        return json.dumps({"message" : "email already in use"})
    else:
        cur = datetime.utcnow()
        exp = datetime.utcnow() + timedelta(days=30)
        return json.dumps({"token" : encode_auth_token(result, cur, exp), "message": "success"})


@app.route("/session/new", methods=['GET', 'POST'])
@check_header
def session_new():
    error = None
    if request.method == 'POST':
        details = request.form
        user_id = authenticate(details)
        if user_id:
            resp = make_response(redirect(url_for('dash_story_full')))
            current_time = datetime.utcnow()
            expired_date = current_time + timedelta(days=30)
            token = encode_auth_token(user_id, current_time, expired_date)
            if 'remember' in details:
                resp.set_cookie("remember_", token, expires=expired_date)
            else:
                session['token'] = token
            # conn = pymysql.connect(db_host, user=db_user, passwd=db_password, db=db_name, connect_timeout=5,
            #                        cursorclass=pymysql.cursors.DictCursor)
            # with conn.cursor() as cur:
            #     cur.execute(
            #         ("SELECT encoded_token, expires FROM auth_tokens WHERE userid=%s"), (user_id))
            #     query_data = cur.fetchone()
            #     if query_data is None:
            #         expired_date_refresh = datetime.utcnow(days=30)
            #         refresh_t = encode_auth_token(
            #             user_id, current_time, expired_date_refresh)
            #         cur.execute(('INSERT INTO auth_tokens(encoded_token, userid, expires) VALUES (%s, %s, %s)'), (
            #             refresh_t, user_id, expired_date_refresh))
            #         conn.commit()
            #     else:
            #         refresh_t = query_data['encoded_token']
            #         expires = query_data['expires']
            #         if current_time > expires:
            #             cur.execute(
            #                 ("INSERT INTO invalid_tokens(invalid_token, user_id) VALUES(%s, %s)"), (refresh_t, user_id))
            #             cur.execute(
            #                 ("DELETE FROM auth_tokens WHERE id = (SELECT id WHERE encoded_token = %s)"), (refresh_t))
            #             refresh_t = encode_auth_token(
            #                 user_id, current_time, expired_date_refresh)
            #             cur.execute(('INSERT INTO auth_tokens(encoded_token, userid, expires) VALUES (%s, %s, %s)'), (
            #                 refresh_t, user_id, expired_date_refresh))
            #             cur.commit()
            # cur.close()
            return resp
        else:
            error = "Username and/or password not valid"
    return render_template("session/new.html", error=error)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route('/google_login')
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri=google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url+"/google/authorized",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

@app.route('/google_login/google/authorized')
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )
    google_client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint=google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response=requests.get(uri, headers=headers,data=body)
    userinfo=userinfo_response.json()
    username=userinfo["given_name"]+userinfo['family_name']
    passwd = os.urandom(16).decode('latin-1')
    usr = User(username_input=username, email_input=userinfo['email'], first_name_input=userinfo['given_name'], last_name_input=userinfo['family_name'], password_input = passwd, signed_in_with="Google")
    result = usr.search_by_email()
    if result == -1:
        result.add_to_server()
    else:
        usr = User.get(result)
    resp = make_response(redirect(url_for('home')))
    cur = datetime.utcnow()
    exp = datetime.utcnow() + timedelta(days=30)
    token = encode_auth_token(usr.user_id, cur, exp)
    resp.set_cookie("remember_", token, expires=exp)
    # soup = bs(urlopen(userinfo['picture']))
    # for image in soup.findAll("img"):
    #     filename=str(usr.user_id)+".jpg"
    #     outpath = os.path.join(UPLOAD_FOLDER,"profile_pics", filename)
    #     urlretrieve(image['src'], outpath)
    return resp


@app.route('/facebook_login')
def facebook_login():
    pass

@app.route("/app/session/new", methods=['POST', 'GET'])
def app_session_new():
    result = None
    if request.method == 'POST':
        details = request.json
        user_id = authenticate(details)
        current_time = datetime.utcnow()
        expired_date = datetime.utcnow() + timedelta(days=30)
        if user_id:
            result = {
                'auth_token': encode_auth_token(user_id, current_time, expired_date)
            }
        else:
            result = {
                'message': 'Username/password is incorrect'
            }
    return jsonify(result)


@app.before_first_request
def load_id():
    token = request.cookies.get('remember_')
    if token is None:
        return redirect(url_for('home'))
    uid = decode_auth_token(token)
    if uid == 0 or uid == 'Signature expired. Please log in again.' or uid == 'Invalid token. please log in again':
        return redirect(url_for('session_new'))
    resp = make_response(url_for('home'))
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(days = 30)
    new_token = encode_auth_token(uid, current_time, expiry_time)
    resp.set_cookie("remember_", new_token, expires=expiry_time)
    return resp


def authenticate(details):
    conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5,
                           cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        username = details['username']
        cur.execute(
            ("SELECT user_id FROM users WHERE username = %s"), username)
        result = cur.fetchone()
        if(result is None):
            return None
        else:
            usr = load_user(result['user_id'])
            if(usr.authenticate(details['password'])):
                return result['user_id']
            else:
                return None
    return None


@app.route("/refresh/token", methods=['GET'])
def issue_new_token():
    token = request.args.get('token')
    uid = decode_auth_token(token)
    if uid == 0 or uid == 'Signature expired. Please log in again.' or uid == 'Invalid token. please log in again':
        return json.dumps({'token' : '0'}), 404
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(days=30)
    new_token = encode_auth_token(uid, current_time, expiry_time)
    return json.dumps({'token' : new_token}), 200


def encode_auth_token(user_id, current_time, expired_date):
    payload = {
        'exp': expired_date,
        'iat': current_time,
        'sub': user_id
    }
    return jwt.encode(
        payload,
        app.secret_key,
        algorithm='HS256'
    )


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, app.secret_key)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 0
    except jwt.InvalidTokenError:
        return 0


@app.route("/app/session/logout")
def app_logout():
    session.pop("logged_in", None)
    session.pop("user_id", None)
    session.pop("platform", None)
    return redirect(url_for("home"))


@app.route("/session/logout", methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('home')))
    if request.cookies.get('remember_') is None:
        print(session)
        token = session.get('token')
        if token:
            session.clear()
            return resp
        elif decode_auth_token(token) == 0 or token is None:
            session.clear()
            return redirect(url_for("session_new"))
    else:
        resp.set_cookie('remember_', '', 0)
        return resp


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
    if file and allowed_file(file.filename):
        filename = str(getUid()) + ".jpg"
        file.save(os.path.join(UPLOAD_FOLDER, 'profile_pics', filename))
        return '{"status":"ok"}'
    return '{"status" : "error"}'


@app.route("/story/update", methods=["GET"])  # THIS NEEDS TO BE FINISHED
@authentication_required
@check_header
def story_update():
    story = Story.get(int(request.args['story_id']))
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    objects = StoryObject.obj_list(request.args['story_id'])
    events = StoryEvent.event_list(request.args['story_id'])
    locations = StoryLocation.loc_list(request.args['story_id'])
    coverimage = story.get_image_base64().decode("utf-8")
    return render_template("story/update.html", StoryLocation=StoryLocation, story=story, objects=objects, events=events, locations=locations, coverimage=coverimage)


@app.route("/story/image")
@authentication_required
@check_header
def story_image():
    story = Story.get(int(request.args['story_id']))
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    # print(story.get_image_base64())
    return story.get_image_base64()


valid_genres = {"Mystery", "Romance", "Sci-Fi", "Fantasy", "Historical Fiction", "Drama",
                "Horror", "Thriller", "Comedy", "Adventure", "Sports", "Non-Fiction", "Other Fiction"}


@app.route("/story/update", methods=["POST"])
@authentication_required
def story_update_post():
    details = request.form
    story_id = request.form.get('story_id')
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    story_title = details['story_title']
    story_synopsis = details['story_synopsis']
    story_price = details['story_price']
    genre = details.get('genre')
    if genre is None or genre not in valid_genres:
        genre = "Miscellaneous"
    story.length_of_story = details['length_of_story']
    story.inventory_size = details.get('inventory_size')
    story.starting_loc = details.get('starting_loc')
    story.story_id = story_id
    filename = ''
    file = request.files['cover']
    if file.filename == '':
        pass
    if file and allowed_file(file.filename):
        filename = str(story_id) + ".jpg"
        file.save(os.path.join(UPLOAD_FOLDER, 'covers', filename))
    story.verification_status = 0
    story.update_verify()
    story.update(story_title, "", story_price, 0, genre, story_synopsis)
    #story_title, story_author, story_price, story_language_id, length_of_story, genre, story_synopsis, inventory_size
    return '{"status":"ok"}'


@app.route("/story/destroy", methods=["POST"])
@authentication_required
def story_destroy():
    story = Story.get(request.args['story_id'])
    if story.user_creator_id != getUid() and not checkAdmin(getUid()):
        abort(403)
    Story.destroy(request.args['story_id'])
    return '{"status":"ok"}'


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/story/new", methods=["POST"])
@authentication_required
def story_new():
    uid = getUid()
    story = Story(user_creator_id=uid)
    story.story_synopsis = ""
    story.add_to_server()
    return '{"status":"ok", "story": {"story_id":' + str(story.story_id) + '}}'


@app.route("/story/object/show")
@authentication_required
@check_header
def object_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    objects = StoryObject.obj_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/object/show.html", locations=locations, events=events, objects=objects, story_id=story_id)


@app.route("/app/story/info", methods=['GET'])
def app_story_logistics():
    return Story.get_entities(int(request.args.get('story_id')))


@app.route("/app/store", methods=["GET"])
def app_store_info():
    return Story.display_for_store()


@app.route("/store/story/info", methods=['GET'])
def app_store_expand():
    details = request.json
    story_id = details.get("story_id")
    return Story.get_info(story_id)


@app.route("/app/library/", methods=['GET'])
def stories_show_owned_by_user():
    user_id = decode_auth_token(request.args.get("auth"))
    return Story.json_story_library(user_id)


@app.route("/story/object/update", methods=['POST'])
@authentication_required
def object_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    object_id = details['obj_id']
    if object_id == '':
        object_id = StoryObject.get_last_id(story_id)
    name = details['obj_name']
    desc = details['obj_description']
    starting_loc = details.get('obj_starting_loc')
    if starting_loc is None:
        starting_loc = 0
    can_pickup_obj = details.get('can_pickup_obj')
    if can_pickup_obj:
        can_pickup_obj = 1
    else:
        can_pickup_obj = 0
    is_hidden = details.get('is_hidden')
    if is_hidden:
        is_hidden = 1
    else:
        is_hidden = 0
    unhide_event_id = details.get('unhide_event_id')
    if unhide_event_id is None:
        is_hidden = 0
    # unhide_event_id = details['unhide_event_id']
    obj = StoryObject.get(story_id, object_id)
    obj.unhide_event_id = unhide_event_id
    obj.verification_status = 0
    obj.update_admin()
    story.verification_status = 0
    story.update_verify()
    obj.update(story_id, object_id, name=name, starting_loc=starting_loc,
               desc=desc, can_pickup_obj=can_pickup_obj, is_hidden=is_hidden)
    # return redirect(url_for("object_show"))
    return "ok"


@app.route("/story/object/new", methods=['POST'])
@authentication_required
def object_new():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    obj = StoryObject(story_id)
    obj.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","object":{"obj_id":' + str(obj.obj_id) + '}}'


@app.route("/story/object/destroy", methods=['POST'])
@authentication_required
def object_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryObject.obj_del(request.form['story_id'], request.form['obj_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/event/show", methods=['GET'])
@authentication_required
@check_header
def event_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/show.html", locations=locations, events=events, story_id=story_id)


@app.route('/story/event/update', methods=['POST'])
@authentication_required
def event_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    if request.method == 'POST':
        details = request.form
        story_id = details['story_id']
        story = Story.get(story_id)
        if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
            abort(403)
        event_id = details['event_id']
        if event_id == '':
            event_id = StoryEvent.get_last_id(story_id)
        name = details['event_name']
        location = details.get('event_loc')
        if location is None:
            location = 0
        desc = details['ev_description']
        is_global = details.get('is_global')
        if is_global is None:
            is_global = False
        else:
            is_global = True
        evnt = StoryEvent.get(story_id, event_id)
        evnt.verification_status = 0
        evnt.update_admin()
        story.verification_status = 0
        story.update_verify()
        evnt.update(story_id, event_id, name, location, desc, is_global)
    return '{"status":"ok"}'


@app.route('/story/event/new', methods=['POST'])
@authentication_required
def event_new():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.args
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    evnt = StoryEvent(story_id)
    evnt.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","event":{"event_id":' + str(evnt.event_id) + '}}'


@app.route("/story/event/destroy", methods=['POST'])
@authentication_required
def event_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryEvent.event_del(request.form['story_id'], request.form['event_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/location/show")
@authentication_required
@check_header
def location_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/show.html", locations=locations, events=events, story_id=story_id)


@app.route("/story/location/indiv")
@authentication_required
@check_header
def location_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = request.args["location_id"]
    location = StoryLocation.get(story_id, location_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/indiv.html", location=location, locations=locations, events=events, story_id=story_id, location_id=location_id)


@app.route("/story/object/indiv")
@authentication_required
@check_header
def object_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    object_id = request.args["object_id"]
    obj = StoryObject.get(story_id, object_id)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/object/indiv.html", obj=obj, locations=locations, story_id=story_id, object_id=object_id, events=events)


@app.route("/story/location/decision/indiv")
@authentication_required
@check_header
def decision_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = request.args["location_id"]
    decision_id = request.args["decision_id"]
    decision = StoryDecision.get(story_id, location_id, decision_id)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/location/decision/indiv.html", locations=locations, decision=decision, story_id=story_id, decision_id=decision_id, events=events, objects=objects)


@app.route("/story/event/indiv")
@authentication_required
@check_header
def event_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    event_id = request.args["event_id"]
    event = StoryEvent.get(story_id, event_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/indiv.html", StoryLocation=StoryLocation, event=event, locations=locations, story_id=story_id, event_id=event_id)


@app.route('/story/location/update', methods=['POST'])
@authentication_required
def location_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    loc_id = details['loc_id']
    if loc_id is None:
        loc_id = StoryLocation.get_last_id(story_id)
    name = details.get('location_name')
    original_desc = details['location_origin_description']
    short_desc = details['location_short_description']
    post_event_description = details['location_post_event_description']
    event_id = details.get("location_event_id")
    if event_id is None:
        event_id = 0
    next_location_id = details.get('next_loc_id')
    if next_location_id is None:
        next_location_id = 0
    loc = StoryLocation.get(story_id, loc_id)
    loc.update(story_id, loc_id, name, original_desc, short_desc,
               post_event_description, event_id, next_location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route('/story/location/new', methods=['POST'])
@authentication_required
def location_new():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    loc = StoryLocation(story_id)
    loc.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","location":{"location_id":' + str(loc.location_id) + '}}'


@app.route("/story/location/destroy", methods=['POST'])
@authentication_required
def location_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryLocation.loc_del(request.form['story_id'], request.form['loc_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/location/decision/show")
@authentication_required
@check_header
def decision_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story = Story.get(request.args['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    decisions = StoryDecision.dec_list_for_story_loc(
        request.args['story_id'], request.args['location_id'])
    locations = StoryLocation.loc_list(
        request.args['story_id'])
    location = StoryLocation.get(
        request.args['story_id'], request.args['location_id'])
    objects = StoryObject.obj_list(
        request.args['story_id'])
  #  print(objects)
   # print(objects[0].obj_name)
    events = StoryEvent.event_list(
        request.args['story_id'])
    return render_template("story/location/decision/show.html", StoryLocation=StoryLocation, decisions=decisions, events=events, objects=objects, story_id=request.args['story_id'], locations=locations, location=location)


@app.route("/story/location/decision/update", methods=['POST'])
@authentication_required
def decision_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.form
    story_id = details["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = details["location_id"]
    decision_id = details['decision_id']
    if decision_id == '':
        decision_id = StoryDecision.get_last_id(story_id, location_id)
    decision_name = details['decision_name']
    sequence = details['sequence_number']
    if sequence == '':
        sequence = 0
    transition = details.get('transition')
    if transition is None:
        transition = False
    else:
        transition = True
    transition_loc_id = details.get("transition_loc_id")
    if transition_loc_id is None:
        transition_loc_id = 0
    is_hidden = details.get('hidden')
    if is_hidden is None:
        is_hidden = False
    else:
        is_hidden = True
    show_event_id = details.get("show_event_id")
    if show_event_id is None:
        show_event_id = 0
    show_object_id = details.get("show_object_id")
    if show_object_id is None:
        show_object_id = 0
    is_locked = details.get("locked")
    if is_locked is None:
        is_locked = False
    else:
        is_locked = True
    locked_descr = details.get('locked_descr')
    if locked_descr is None:
        locked_descr = ''
    unlock_event_id = details.get('unlock_event_id')
    if unlock_event_id is None:
        unlock_event_id = 0
    unlock_obj_id = details.get("unlock_object_id")
    if unlock_obj_id is None:
        unlock_obj_id = 0
    aftermath_desc = details['aftermath_desc']
    cause_event = details.get('cause_event')
    if cause_event is None:
        cause_event = False
    else:
        cause_event = True
    effect_event_id = details.get('effect_event_id')
    if effect_event_id is None:
        effect_event_id = 0
    dec_description = details['dec_description']
    can_occur_once = details.get("can_occur_once")
    if can_occur_once is None:
        can_occur_once = False
    else:
        can_occur_once = True
    is_locked_by_event_id = details.get("is_locked_by_event_id")
    if is_locked_by_event_id is None:
        is_locked_by_event_id = 0
    locked_by_event_desc = details.get("locked_by_event_description")
    if locked_by_event_desc is None:
        locked_by_event_desc = ""
    dec = StoryDecision.get(story_id, location_id, decision_id)
    dec.update(story_id, decision_id, location_id, sequence, decision_name, transition, transition_loc_id, is_hidden, is_locked, dec_description, show_event_id,
               show_object_id, unlock_event_id, unlock_obj_id, locked_descr, aftermath_desc, cause_event, effect_event_id, can_occur_once, is_locked_by_event_id, locked_by_event_desc)
    dec.verification_status = 0
    dec.update_admin()
    loc = StoryLocation.get(story_id, location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/location/decision/new", methods=['POST'])
@authentication_required
def decision_new():
    # if "logged_in" not in session:
        # return redirect(url_for("session_new"))
    details = request.args
    story_id = details["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = details["location_id"]
    dec = StoryDecision(story_id, location_id)
    dec.add_to_server()
    loc = StoryLocation.get(story_id, location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","decision":{"decision_id":' + str(dec.decision_id) + '}}'


@app.route("/story/location/decision/destroy", methods=['POST'])
@authentication_required
def decision_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryDecision.dec_del(
        request.form['story_id'], request.form['location_id'], request.form['decision_id'])
    loc = StoryLocation.get(
        request.form['story_id'], request.form['location_id'])
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/about")
@check_header
def about():
    return render_template("about.html")


@app.route("/contact")
@check_header
def contact():
    return render_template("contact.html")


@app.route("/verification/view")
@authentication_required
@check_header
def verification_view():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    if not checkEditorAdmin(getUid()):
        abort(403)
    stories = Story.story_list_ready_for_verification()
    return render_template("verification/view.html", stories=stories)


@app.route("/verification/review")
@authentication_required
@check_header
def verification_review():
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    objects = StoryObject.obj_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    decisions = StoryDecision.dec_list_story(story_id)
    return render_template("verification/review.html", StoryLocation=StoryLocation, StoryEvent=StoryEvent, story=story, story_id=story_id, objects=objects, locations=locations, events=events, decisions=decisions)


@app.route("/verification/review/update", methods=['POST'])
@authentication_required
def review_update():
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    details = request.form
    story_id = details['story_id']
    entity_type = details['type']
    ent_id = details.get('ent_id')
    is_verified = details.get('is_verified')
    reviewer_comment = details['comment']
    if entity_type.lower() == 'object':
        obj = StoryObject.get(story_id, ent_id)
        obj.reviewer_comments = reviewer_comment
        obj.is_verified = is_verified
        obj.update_admin()
    elif entity_type.lower() == 'location':
        loc = StoryLocation.get(story_id, ent_id)
        loc.reviewer_comments = reviewer_comment
        loc.is_verified = is_verified
        loc.update_admin()
    elif entity_type.lower() == 'event':
        evnt = StoryEvent.get(story_id, ent_id)
        evnt.reviewer_comments = reviewer_comment
        evnt.is_verified = is_verified
        evnt.update_admin()
    elif entity_type.lower() == 'story':
        story = Story.get(story_id)
        print(story.verification_status)
        story.parental_rating = details['parental_ratings']
        story.verifier_id = getUid()
        story.reviewer_comments = reviewer_comment
        if StoryDecision.check_verify(story_id) and StoryLocation.check_verify(story_id) and StoryObject.check_verify(story_id) and StoryEvent.check_verify(story_id):
            story.verification_status = is_verified
            story.story_in_store = True
        if int(is_verified) == 2:
            story.verification_status = is_verified
            story.story_in_store=False
        story.update_verify()
    else:
        loc_id = details['loc_id']
        dec = StoryDecision.get(story_id, loc_id, ent_id)
        dec.reviewer_comments = reviewer_comment
        dec.is_verified = is_verified
        dec.update_admin()
    return '{"status":"ok"}'


@app.route("/verification/status")
@authentication_required
@check_header
def verification_story():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    story_id = request.args["story_id"]
    locations = StoryLocation.loc_list(story_id)
    decisions = StoryDecision.dec_list_story(story_id)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("verification/status.html", events=events, story_id=story_id, locations=locations, decisions=decisions, objects=objects)


@app.route("/verification/submit", methods=["POST"])
@authentication_required
@check_header
def verification_submit():
    details = request.args
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    story.verification_status = 1
    story.update_verify()
    decs = StoryDecision.dec_list_story(story_id)
    for dec in decs:
        if dec.verification_status != 3:
            dec.verification_status = 1
            dec.update_admin()
    evts = StoryEvent.event_list(story_id)
    for evt in evts:
        if evt.verification_status != 3:
            evt.verification_status = 1
            evt.update_admin()
    locs = StoryLocation.loc_list(story_id)
    for loc in locs:
        if loc.verification_status != 3:
            loc.verification_status = 1
            loc.update_admin()
    objs = StoryObject.obj_list(story_id)
    for obj in objs:
        if obj.verification_status != 3:
            obj.verification_status = 1
            obj.update_admin()
    return '{"status":"ok"}'


@app.route("/story/treeview")
@authentication_required
@check_header
def treeview():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    locations = StoryLocation.loc_list(story_id)
    loc_id = request.args.get('location_id')
    decisions = []
    location = None
    if loc_id is not None:
        decisions = StoryDecision.dec_list_for_story_loc(story_id, loc_id)
        location = StoryLocation.get(story_id, loc_id)
    else:
        loc_id = 0
    return render_template("story/treeview.html", StoryLocation=StoryLocation, loc_id=loc_id, locations=locations, location=location, decisions=decisions, story=story)


@app.route("/verification/treeview")
@authentication_required
@check_header
def verify_treeview():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    story_id = request.args['story_id']
    story = Story.get(story_id)
    locations = StoryLocation.loc_list(story_id)
    loc_id = request.args.get('location_id')
    decisions = []
    if loc_id is not None:
        decisions = StoryDecision.dec_list_for_story_loc(story_id, loc_id)

    location = StoryLocation.get(story_id, loc_id)
    return render_template("verification/treeview.html", StoryLocation=StoryLocation, loc_id=loc_id, locations=locations, location=location, decisions=decisions, story=story)


@app.route("/story/run")
@authentication_required
@check_header
def story_run():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    loc_id = request.args.get("location_id")
    location = None
    if loc_id is None:
        loc_id = story.starting_loc
    location = StoryLocation.get(story_id, loc_id)
    decisions = StoryDecision.dec_list_for_story_loc(story_id, loc_id)
    objects = StoryObject.obj_list_loc(story_id, loc_id)

    cookies = request.cookies
    rundata = cookies.get("rundata")
    inv = []
    evts = []
    triggered = []
    backs = []
    if not rundata is None:
        obj = json.loads(rundata)
        for itm in obj['items']:
            inv.append(StoryObject.get(story_id, itm))
        for ent in obj['events']:
            evts.append(StoryEvent.get(story_id, ent))
        triggered = obj['decs']
        for back in obj['back']:
            backs.append(StoryLocation.get(story_id, back))

    return render_template("story/run.html", inv=inv, evts=evts, triggered=triggered, backs=backs, objects=objects, decisions=decisions, StoryEvent=StoryEvent, StoryLocation=StoryLocation, StoryObject=StoryObject, story=story, location=location)


@app.route("/story/help")
@authentication_required
@check_header
def help():
    return render_template("story/help.html")


@app.route("/verification/help")
@authentication_required
@check_header
def vhelp():
    return render_template("verification/help.html")


@app.route("/story/treeview_help")
@authentication_required
@check_header
def treeview_help():
    story_id = request.args['story_id']
    story = Story.get(story_id)
    return render_template("story/treeview_help.html", story=story)


@app.route("/admin")
@authentication_required
@check_header
def admin_index():
    uid = getUid()
    if not checkAdmin(uid):
        abort(403)
    acct = User.get(uid)
    if not acct.is_admin:
        abort(403)
    stories = Story.get_story_count()
    users = User.get_user_count()
    return render_template("admin/index.html", stories=stories, users=users)


@app.route("/admin/users", methods=["GET", "POST"])
@authentication_required
@check_header
def admin_users():
    uid = getUid()
    if not checkAdmin(uid):
        abort(403)
    acct = User.get(uid)
    if not acct.is_admin:
        abort(403)
    if request.method == "GET":
        users = User.list_of_all_users()
        return render_template("admin/users.html", users=users)
    else:
        user = User()
        user.user_id = request.form.get("user_id")
        user.username = request.form.get("username")
        user.is_admin = True
        user.is_content_editor = True
        user.is_copy_editor = True
        print(request.form.get("is_admin"))
        if request.form.get("is_admin") is None:
            user.is_admin = False
        if request.form.get("is_content_editor") is None:
            user.is_content_editor = False
        if request.form.get("is_copy_editor") is None:
            user.is_copy_editor = False
        print(user.username)
        print(user.user_id)
        user.update_admin()
        return '{"status":"ok"}'


@app.route("/password_reset", methods=["GET", "POST"])
@check_header
def password_request():
    if request.method == "POST":
        email = request.form.get('email')
        if email is not None:
            token = User.get_reset_token(email, 900)
            usr = User(email_input = email)
            result = usr.search_by_email()
            if result != -1:
                usr = User.get(result)
                if usr.signed_in_with != "native" or usr.signed_in_with != '':
                    error = "You signed in with " + usr.signed_in_with + "."
                    return render_template("session/new.html", error=error)
            else:
                return render_template("session/new.html", error="Email not found.")
            print("Token Got")
            if token is not None:
                msg = Message('Password Reset Request',
                                sender='noreply@myaudioodyssey.com',
                                recipients=[email])
                msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
                            '''
                mail.send(msg)
                print("Message Sent")
    return render_template("/password_reset/request.html")

@app.route("/password_reset/<token>",  methods=["GET", "POST"])
@check_header
def reset_token(token):
    user = User.get_reset_user(token)
    if user is None:
        return redirect(url_for("session_new"))
    if request.method == "POST":
        passwd = request.form.get('password')
        passco = request.form.get('password_confirm')
        if passwd != passco:
            return render_template("/password_reset/form.html", error="Passwords don't match!")
        user.password_salt = User.generate_password_salt()
        user.password = User.encrypt_password(passwd, user.password_salt)
        user.update_password()
        return redirect(url_for("session_new"))
    return render_template("/password_reset/form.html")


@app.route("/dash")
@authentication_required
@check_header
def dashboard():
    stories = Story.story_list_by_creatordate(g.uid)
    base_url = ""
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


@app.route("/dash/stories")
@authentication_required
@check_header
def dash_story_full():
    stories = Story.story_list_by_creatordate(g.uid)
    return render_template("/dash/index.html", stories=stories, content=render_template("/dash/story.html", stories=stories))


@app.route("/dash/users")
@authentication_required
@check_header
def dash_user_full():
    stories = Story.story_list_by_creatordate(g.uid)
    userimage = g.user.get_profile_pic_base64().decode("utf-8")
    return render_template("/dash/index.html", stories=stories, content=render_template("/dash/user.html", userimage=userimage))


@app.errorhandler(403)
@check_header
def forbidden_403(e):
    # Pretend all 403s are 404s for security purposes
    return render_template('error/404.html'), 403


@app.errorhandler(404)
@check_header
def page_not_found_404(e):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
@check_header
def server_error_500(e):
    return render_template('error/500.html'), 500


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# @login_manager.unauthorized_handler
# def unauthorized():
#     return redirect(url_for("session_new"))

def getUid():
    token = session.get('token')
    if token is None:
        token = request.cookies.get('remember_')
    return decode_auth_token(token)


def checkEditorAdmin(uid):
    user = User.get(uid)
    return user.is_admin or user.is_copy_editor or user.is_content_editor

def checkAdmin(uid):
    user = User.get(uid)
    return user.is_admin


if __name__ == '__main__':
    app.run()
