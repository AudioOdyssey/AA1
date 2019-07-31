# Python standard libraries
import os

# Third-party libraries
from flask import redirect, render_template, request, url_for, session, Blueprint

# Internal imports
from audio_od import app
from audio_od.utils import authentication_required, check_header, decode_auth_token

dash_view = Blueprint('home', __name__)

@dash_view.route("/dashboard")
@app.route("/dashboard/")
@authentication_required
@check_header
def dashboard():
    stories = Story.story_list_by_creatordate(g.uid)
    base_url = base64.b64encode("/dash/story".encode()).decode("utf-8")
    return render_template("/dash/index.html", stories=stories, base_url=base_url)


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

