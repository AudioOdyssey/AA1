import os
import sys


from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify, session, flash, send_from_directory, abort, g


from audio_od import app
import config
from models import *
from auth import authentication_required, check_header

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
            return redirect(url_for('dashboard'))
    else:
        user_id = decode_auth_token(auth_token)
        if user_id == 'Signature expired. Please log in again.' or user_id == 0:
            return render_template('index.html')
        else:
            return redirect(url_for('dashboard'))
    return render_template('index.html')



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