# Third-party libraries
from flask import redirect, render_template, request, url_for, session, Blueprint


# Internal imports
from audio_od.utils import check_header, decode_auth_token

home = Blueprint('home', __name__)

@home.route("/")
@home.route("/home")
@home.route("/index")
@check_header
def index():
    """Endpoint for the homepage. If the user is logged in, then the user will be redirected back
    to the dashboard page. Else, the user will be sent back to the normal index page."""
    auth_token = request.cookies.get('remember_')
    if auth_token is None:
        token = session.get('token')
        if token is None or not decode_auth_token(token):
            return render_template("index.html")
    else:
        user_id = decode_auth_token(auth_token)
        if user_id in ('Signature expired. Please log in again.', 0):
            return render_template('index.html')
    return redirect(url_for('dash.dashboard'))


@home.route("/about")
@check_header
def about():
    return render_template("about.html")


@home.route("/eula")
@check_header
def eula():
    return render_template("eula.html")
