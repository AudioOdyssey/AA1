#Python standard libraries
import os
from datetime import datetime, timedelta
from functools import wraps
import re

#Third-party libraries
from flask import redirect, request, render_template, url_for, make_response, session, g
import jwt

#internal imports
from audio_od import app
import audio_od.config
from audio_od.models import User


def authentication_required(func):
    """This is used to check if a user is signed in. If the user is not signed it, the user will be redirected back to the
    index. Else, the user will be able to access the desired page. It first checks the long-lived token. If it can be decoded, then
    the user will be sent to the desired page. Else, s/he will be redirected back to index. If the remember_ token doesn't exist, 
    the session cookie will be checked and the same thing will happen when checking it. If the token is invalidated, then user 
    will be redirected back to the log-in screen."""
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        remember = request.cookies.get('remember_')
        if remember is None:
            token = session.get('token')
            uid = decode_auth_token(token)
            if uid == 0:
                return redirect(url_for('auth.session_new'))
            else:
                usr=load_user(uid)
                if usr.check_invalid_tokens(token):
                    session.clear()
                    return redirect(url_for('auth.session_new'))
                return func(*args, **kwargs)
        else:
            uid = decode_auth_token(remember)
            if uid == 0:
                return redirect(url_for('auth.session_new'))
            else:
                resp = make_response(redirect(url_for('auth.session_new')))
                usr=load_user(uid)
                if usr is None or usr.check_invalid_tokens(remember):
                    resp.set_cookie('remember_', '', 0)
                    return resp
                return func(*args, **kwargs)
    return func_wrapper


def check_header(func):
    """This is used to show the correct info for the website header. If the token can not be decoded, then the user will be redirected back
    to the index. Else, the correct information will be showed"""
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        g.uid = getUid()
        if g.uid == 0:
            g.uid = 0
            g.user = None
            return func(*args, **kwargs)
        g.user = User.get(g.uid)
        return func(*args, **kwargs)
    return func_wrapper


def check_invalid_app_token(token):
    """This method checks the app token to see if it has been invalidated before. If the token can't be decoded, method will return True. 
    If the token is in the invalidated_tokens table, True will be return. All other cases will return false."""
    uid=decode_auth_token(token)
    if uid==0:
        return True
    else:
        usr = load_user(uid)
        if usr is None or usr.check_invalid_tokens(token):
            return True
    return False



@app.before_first_request
def load_id():
    """Whenever the user first acccesses the website, the user's tokens will be checked. If it can be decoded, it will be refreshed.
    Else, s/he will be redirected back to the index page.""" 
    token = request.cookies.get('remember_')
    if token is None:
        return redirect(url_for('home.index'))
    uid = decode_auth_token(token)
    if uid == 0:
        return redirect(url_for('auth.session_new'))
    resp = make_response(url_for('home.index'))
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(days = 30)
    new_token = encode_auth_token(uid, current_time, expiry_time)
    resp.set_cookie("remember_", new_token, expires=expiry_time)
    return resp

def encode_auth_token(user_id, current_time, expired_date):
    """This method issues a new token. Contains the user_id, current time and expiry date"""
    payload = {
        'exp': expired_date,
        'iat': current_time,
        'sub': user_id
    }
    return jwt.encode(
        payload,
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def decode_auth_token(auth_token):
    """This method decodes the token. If successful, the user_id will be returned. Else, 0 will be returned."""
    try:
        payload = jwt.decode(auth_token, app.config['SECRET_KEY'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 0
    except jwt.InvalidTokenError:
        return 0


def getUid():
    """Returns the user_id"""
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


@app.errorhandler(403)
@check_header
def forbidden_403(e):
    # Pretend all 403s are 404s for security purposes
    return render_template('error/404.html'), 404


@app.errorhandler(404)
@check_header
def page_not_found_404(e):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
@check_header
def server_error_500(e):
    return render_template('error/500.html'), 500

def isValidEmail(email):
    """Uses regex to check if the email is valid or not. Will return true if valid, else will return false."""
    if len(email) > 7:
        if re.match(r"^.+@(\[?)[a-zA-Z0-9-.]+.(([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email) != None:
            return True
    return False


def load_user(user_id):
    return User.get(user_id)