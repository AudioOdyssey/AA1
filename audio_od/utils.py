#Python standard libraries
import os
from datetime import datetime, timedelta
from functools import wraps

#Third-party libraries
from flask import redirect, request, render_template, url_for, make_response, session, g
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
        return redirect(url_for('home.index'))
    uid = decode_auth_token(token)
    if uid == 0 or uid == 'Signature expired. Please log in again.' or uid == 'Invalid token. please log in again':
        return redirect(url_for('auth.session_new'))
    resp = make_response(url_for('home.index'))
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(days = 30)
    new_token = encode_auth_token(uid, current_time, expiry_time)
    resp.set_cookie("remember_", new_token, expires=expiry_time)
    return resp

def encode_auth_token(user_id, current_time, expired_date):
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