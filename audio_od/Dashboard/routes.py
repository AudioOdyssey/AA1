# Python standard libraries
import os
import base64

# Third-party libraries
from flask import redirect, render_template, request, url_for, session, Blueprint, g

# Internal imports
from audio_od import app
from models import Story
from audio_od.utils import authentication_required, check_header, decode_auth_token

dash_view = Blueprint('dash', __name__)

@dash_view.route("/dashboard")
@app.route("/dashboard/")
@authentication_required
@check_header
def dashboard():
    """Endpoint for viewing the dashboard. Shows the stories a user created. Also on the side, shows the recently edited stories."""
    stories = Story.story_list_by_creatordate(g.uid)
    base_url = base64.b64encode("/dash/story".encode()).decode("utf-8")
    return render_template("/dash/index.html", stories=stories, base_url=base_url)


def isValidEmail(email):
    """Does the same thing as Auth/routes.isValidEmail"""
    if len(email) > 7:
        if re.match(r"^.+@(\[?)[a-zA-Z0-9-.]+.(([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email) != None:
            return True
    return False


@dash_view.route('/dashboard/<path:page>')
@authentication_required
@check_header
def dashboard_full(page):
    stories = Story.story_list_by_creatordate(g.uid)
    base_url = base64.b64encode(request.full_path[10:].encode()).decode("utf-8")
    return render_template("/dash/index.html", stories=stories, base_url=base_url)


@dash_view.route("/dash/story")
@authentication_required
@check_header
def dash_story():
    raw_stories = Story.story_list_by_creatordate(g.uid)
    stories = []
    for story in raw_stories:
        if story.verification_status != 3:
            stories.append(story)
    return render_template("/dash/story.html", stories=stories)


@dash_view.route("/dash/share")
@authentication_required
@check_header
def dash_share():
    stories = Story.story_shares_by_uid(g.user.user_id)
    return render_template("/dash/shared.html", stories=stories)


@dash_view.route("/dash/user")
@authentication_required
@check_header
def dash_user():
    userimage = g.user.get_profile_pic_base64().decode("utf-8")
    return render_template("/dash/user.html", userimage=userimage)


@dash_view.route("/dash/verified")
@authentication_required
@check_header
def dash_verified():
    raw_stories = Story.story_list_by_creatordate(g.user.user_id)
    stories = []
    for story in raw_stories:
        if story.verification_status == 3 and story.story_in_store != 1:
            stories.append(story)
    return render_template("/dash/verified.html", stories=stories)


@dash_view.route("/dash/published")
@authentication_required
@check_header
def dash_published():
    raw_stories = Story.story_list_by_creatordate(g.user.user_id)
    stories = []
    for story in raw_stories:
        if story.story_in_store == 1:
            stories.append(story)
    return render_template("/dash/published.html", stories=stories)

