#Python standard libraries
import os
from datetime import datetime, timedelta
from functools import wraps

#Third-party libraries
from flask import redirect, request, url_for, make_response, session, g
import jwt

#internal imports
from audio_od import app
import audio_od.config
from audio_od.models import User


def authentication_required(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        remember = request.cookies.get('remember_')
        if remember is None:
            token = session.get('token')
            if token is None or decode_auth_token(token) == 0:
                return redirect(url_for('auth.session_new'))
            else:
                return func(*args, **kwargs)
        else:
            uid = decode_auth_token(remember)
            if uid == 'Invalid token. please log in again' or uid == 0 or uid == "Signature expired. Please log in again.":
                return redirect(url_for('auth.session_new'))
            return func(*args, **kwargs)
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
    return func_wrapper


@app.before_first_request
def load_id():
    print(1)
    token = request.cookies.get('remember_')
    if token is None:
        return redirect(url_for('home'))
    uid = decode_auth_token(token)
    if uid == 0 or uid == 'Signature expired. Please log in again.' or uid == 'Invalid token. please log in again':
        return redirect(url_for('auth.session_new'))
    resp = make_response(url_for('home'))
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(days = 30)
    new_token = encode_auth_token(uid, current_time, expiry_time)
    resp.set_cookie("remember_", new_token, expires=expiry_time)
    return resp



def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, app.config['SECRET_KEY'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 0
    except jwt.InvalidTokenError:
        return 0


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
