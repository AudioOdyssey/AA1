#Python standard libraries
import os
import sys
import json
from datetime import datetime, timedelta
from functools import wraps
import base64
import re

#Third-party libraries
from flask import redirect, render_template, request, url_for, make_response, jsonify, session, abort, g
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, login_url
from flask_mail import Message, Mail
import pymysql
import pymysql.cursors
import jwt
from bs4 import BeautifulSoup as bs
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, Facebook, Google

#internal imports
from audio_od import app
import config
from models import User

app.config['MAIL_SERVER'] = config.mail_server
app.config['MAIL_PORT'] = config.mail_port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.mail_name
app.config['MAIL_PASSWORD'] = config.mail_pass
mail = Mail(app)

app.config['GOOGLE_CLIENT_ID']=config.google_client_id
app.config['GOOGLE_CLIENT_SECRET']=config.google_client_secret
GOOGLE_DISCOVERY_URL="https://accounts.google.com/.well-known/openid-configuration"

app.config['FACEBOOK_CLIENT_ID'] = config.facebook_client_id
app.config['FACEBOOK_CLIENT_SECRET'] = config.facebook_client_secret

oauth = OAuth(app)


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
    func_wrapper.__name__ = func.__name__
    return func_wrapper


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
    func_wrapper.__name__ = func.__name__
    return func_wrapper



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


def isValidEmail(email):
    if len(email) > 7:
        if re.match(r"^.+@(\[?)[a-zA-Z0-9-.]+.(([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email) != None:
            return True
    return False


@app.route("/session/new", methods=['GET', 'POST'])
@check_header
def session_new():
    error = None
    if request.method == 'POST':
        details = request.form
        user_id = authenticate(details)
        if user_id:
            resp = make_response(redirect(url_for('dashboard')))
            current_time = datetime.utcnow()
            expired_date = current_time + timedelta(days=30)
            token = encode_auth_token(user_id, current_time, expired_date)
            if 'remember' in details:
                resp.set_cookie("remember_", token, expires=expired_date)
            else:
                session['token'] = token
            return resp
        else:
            error = "Username and/or password not valid"
    return render_template("session/new.html", error=error)

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


def google_callback(remote, token, userinfo):
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


google_bp = create_flask_blueprint(Google, oauth, google_callback)
app.register_blueprint(google_bp, url_prefix='/google')


def facebook_callback(remote, token, user_info):
    username = user_info['given_name']+user_info['family_name']
    email=user_info['email']
    passwd = os.urandom(16).decode('latin-1')
    usr = User(username_input=username, email_input=email, first_name_input=user_info['given_name'], last_name_input=user_info['family_name'], password_input = passwd, signed_in_with="Facebook")
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
    return resp


facebook_bp = create_flask_blueprint(Facebook, oauth, facebook_callback)
app.register_blueprint(facebook_bp, url_prefix='/facebook')




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


@app.route("/app/session/logout")
def app_logout():
    session.pop("logged_in", None)
    session.pop("user_id", None)
    session.pop("platform", None)
    return redirect(url_for("home"))



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

def getUid():
    token = session.get('token')
    if token is None:
        token = request.cookies.get('remember_')
    return decode_auth_token(token)

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


def checkEditorAdmin(uid):
    user = User.get(uid)
    return user.is_admin or user.is_copy_editor or user.is_content_editor

def checkAdmin(uid):
    user = User.get(uid)
    return user.is_admin


def load_user(user_id):
    return User.get(user_id)