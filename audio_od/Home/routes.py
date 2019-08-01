# Python standard libraries
import os
import sys

# Third-party libraries
from flask import redirect, render_template, request, url_for, session, Blueprint


# Internal imports
from audio_od import app
from audio_od.utils import authentication_required, check_header, decode_auth_token

home = Blueprint('home', __name__)

@home.route("/")
@home.route("/home")
@home.route("/index")
@check_header
def index():
    """Endpoint for the homepage. If the user is logged in, then the user will be redirected back to the dashboard page. Else, the user will be s
    back to the normal index page."""
    auth_token = request.cookies.get('remember_')
    if auth_token is None: #if the user does not have a remember me token, the session token will be checked
        token = session.get('token')
        if token is None or not decode_auth_token(token):
            return render_template("index.html")
        else:
            return redirect(url_for('dash.dashboard'))
    else:
        user_id = decode_auth_token(auth_token)
        if user_id == 'Signature expired. Please log in again.' or user_id == 0:
            return render_template('index.html')
        else:
            return redirect(url_for('dash.dashboard'))
    return render_template('index.html')


@home.route("/about")
@check_header
def about():
    return render_template("about.html")



@home.route("/contact")
@check_header
def contact():
    return render_template("contact.html")