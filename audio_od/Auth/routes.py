#Python standard libraries
import os
import sys
import json
from datetime import datetime, timedelta
import base64
import re

#Third-party libraries
from flask import redirect, render_template, request, url_for, make_response, jsonify, session, abort, g, Blueprint
from flask_mail import Message, Mail
import pymysql
import pymysql.cursors
import jwt
from bs4 import BeautifulSoup as bs
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, Facebook, Google

#internal imports
from audio_od import app
import audio_od.config
from audio_od.models import User
from audio_od.utils import check_header, authentication_required, getUid, decode_auth_token, encode_auth_token



oauth = OAuth(app)
auth = Blueprint('auth', __name__)

mail = Mail(app)

@auth.route("/user/new", methods=['GET', 'POST'])
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
            return redirect(url_for("home.index"))
    return render_template("user/new.html")

    
@auth.route("/app/user/new", methods=['POST', 'GET'])
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


@auth.route("/session/new", methods=['GET', 'POST'])
@check_header
def session_new():
    error = None
    if request.method == 'POST':
        details = request.form
        user_id = authenticate(details)
        if user_id:
            resp = make_response(redirect(url_for('Users.dashboard')))
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

@auth.route("/app/session/new", methods=['POST', 'GET'])
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
    conn = pymysql.connect(app.config['DB_HOST'], user=app.config['USER'], passwd=app.config['DB_PASSWORD'], db=app.config['DB_NAME'], connect_timeout=5,
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
        usr.add_to_server()
    else:
        usr = User.get(result)
    resp = make_response(redirect(url_for('home.index')))
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
    if user_info is None:
        return render_template("user/new.html", error="User declined authorization through Facebook")
    username = user_info['given_name']+user_info['family_name']
    email=user_info['email']
    passwd = os.urandom(16).decode('latin-1')
    usr = User(username_input=username, email_input=email, first_name_input=user_info['given_name'], last_name_input=user_info['family_name'], password_input = passwd, signed_in_with="Facebook")
    result = usr.search_by_email()
    if result == -1:
        usr.add_to_server()
    else:
        usr = User.get(result)
    resp = make_response(redirect(url_for('home.index')))
    cur = datetime.utcnow()
    exp = datetime.utcnow() + timedelta(days=30)
    token = encode_auth_token(usr.user_id, cur, exp)
    resp.set_cookie("remember_", token, expires=exp)
    return resp


facebook_bp = create_flask_blueprint(Facebook, oauth, facebook_callback)
app.register_blueprint(facebook_bp, url_prefix='/facebook')



@auth.route("/refresh/token", methods=['GET'])
def issue_new_token():
    token = request.args.get('token')
    uid = decode_auth_token(token)
    if uid == 0 or uid == 'Signature expired. Please log in again.' or uid == 'Invalid token. please log in again':
        return json.dumps({'token' : '0'}), 404
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(days=30)
    new_token = encode_auth_token(uid, current_time, expiry_time)
    return json.dumps({'token' : new_token}), 200


@auth.route("/session/logout", methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('home.index')))
    if request.cookies.get('remember_') is None:
        print(session)
        token = session.get('token')
        if token:
            session.clear()
            return resp
        elif decode_auth_token(token) == 0 or token is None:
            session.clear()
            return redirect(url_for("auth.session_new"))
    else:
        resp.set_cookie('remember_', '', 0)
        return resp


@auth.route("/app/session/logout")
def app_logout():
    session.pop("logged_in", None)
    session.pop("user_id", None)
    session.pop("platform", None)
    return redirect(url_for("home.index"))



@auth.route("/password_reset", methods=["GET", "POST"])
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
                if usr.signed_in_with != "native":
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
{url_for('auth.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
                            '''
                mail.send(msg)
                print("Message Sent")
    return render_template("/password_reset/request.html")

@auth.route("/password_reset/<token>",  methods=["GET", "POST"])
@check_header
def reset_token(token):
    user = User.get_reset_user(token)
    if user is None:
        return redirect(url_for("auth.session_new"))
    if request.method == "POST":
        passwd = request.form.get('password')
        passco = request.form.get('password_confirm')
        if passwd != passco:
            return render_template("/password_reset/form.html", error="Passwords don't match!")
        user.password_salt = User.generate_password_salt()
        user.password = User.encrypt_password(passwd, user.password_salt)
        user.update_password()
        return redirect(url_for("auth.session_new"))
    return render_template("/password_reset/form.html")


@auth.route("/admin")
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

@auth.route("/admin/users", methods=["GET", "POST"])
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


def load_user(user_id):
    return User.get(user_id)