# Python standard libraries
import os
import sys

# Third-party libraries
from flask import redirect, render_template, request, url_for, session


# Internal imports
from audio_od import app
import config
from models import *


@app.route("/")
@app.route("/home")
@app.route("/index")
@auth_bp.check_header
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


@app.route("/about")
@auth_bp.check_header
def about():
    return render_template("about.html")



@app.route("/contact")
@auth_bp.check_header
def contact():
    return render_template("contact.html")


@app.errorhandler(403)
@auth_bp.check_header
def forbidden_403(e):
    # Pretend all 403s are 404s for security purposes
    return render_template('error/404.html'), 403


@app.errorhandler(404)
@auth_bp.check_header
def page_not_found_404(e):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
@auth_bp.check_header
def server_error_500(e):
    return render_template('error/500.html'), 500
