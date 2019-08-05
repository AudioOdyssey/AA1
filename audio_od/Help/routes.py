# Third-party libraries
from flask import render_template, Blueprint

# Internal imports
from audio_od.utils import authentication_required, check_header, decode_auth_token

helper = Blueprint('help', __name__)

@helper.route("/help/story")
@check_header
def help():
    return render_template("help/story.html")


@helper.route("/help")
@check_header
def index_help():
    return render_template("help/index.html")


@helper.route("/help/verification")
@check_header
def vhelp():
    return render_template("help/verification.html")


@helper.route("/help/treeview")
@check_header
def treeview_help():
    return render_template("help/treeview.html")

@helper.route("/help/run")
@check_header
def help_run():
    return render_template("help/run.html")

