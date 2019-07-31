#Python standard libraries
import os
import sys
import hashlib
import binascii
import json


#Third-party libraries
from flask import redirect, render_template, request, url_for, Blueprint


#Internal imports
from audio_od import app
import config
from models import *
from audio_od.utils import authentication_required, check_header, checkEditorAdmin, getUid

verification = Blueprint('verification', __name__)


@app.route("/verification")
@app.route("/verification/")
@verification.route("/verification/view")
@authentication_required
@check_header
def verification_view():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    if not checkEditorAdmin(getUid()):
        abort(403)
    stories = Story.story_list_ready_for_verification()
    return render_template("verification/view.html", stories=stories)


@verification.route("/verification/review")
@authentication_required
@check_header
def verification_review():
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    objects = StoryObject.obj_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    decisions = StoryDecision.dec_list_story(story_id)
    return render_template("verification/review.html", StoryObject=StoryObject, StoryLocation=StoryLocation, StoryEvent=StoryEvent, story=story, story_id=story_id, objects=objects, locations=locations, events=events, decisions=decisions)


@verification.route("/verification/review/update", methods=['POST'])
@authentication_required
def review_update():
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    details = request.form
    story_id = details['story_id']
    entity_type = details['type']
    ent_id = details.get('ent_id')
    is_verified = details.get('is_verified')
    reviewer_comment = details['comment']
    if entity_type.lower() == 'object':
        obj = StoryObject.get(story_id, ent_id)
        obj.reviewer_comments = reviewer_comment
        obj.verification_status = is_verified
        obj.update_admin()
    elif entity_type.lower() == 'location':
        loc = StoryLocation.get(story_id, ent_id)
        loc.reviewer_comments = reviewer_comment
        obj.verification_status = is_verified
        loc.update_admin()
    elif entity_type.lower() == 'event':
        evnt = StoryEvent.get(story_id, ent_id)
        evnt.reviewer_comments = reviewer_comment
        obj.verification_status = is_verified
        evnt.update_admin()
    elif entity_type.lower() == 'story':
        story = Story.get(story_id)
        print(story.verification_status)
        story.parental_rating = details['parental_ratings']
        story.verifier_id = getUid()
        story.reviewer_comments = reviewer_comment
        if StoryDecision.check_verify(story_id) and StoryLocation.check_verify(story_id) and StoryObject.check_verify(story_id) and StoryEvent.check_verify(story_id):
            story.verification_status = is_verified
            story.story_in_store = True
        if int(is_verified) == 2:
            story.verification_status = is_verified
            story.story_in_store = False
        story.update_verify()
    else:
        loc_id = details['loc_id']
        dec = StoryDecision.get(story_id, loc_id, ent_id)
        dec.reviewer_comments = reviewer_comment
        dec.verification_status = is_verified
        dec.update_admin()
    return '{"status":"ok"}'


@verification.route("/verification/status")
@authentication_required
@check_header
def verification_story():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story = Story.get(int(request.args['story_id']))
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    story_id = request.args["story_id"]
    locations = StoryLocation.loc_list(story_id)
    decisions = StoryDecision.dec_list_story(story_id)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("verification/status.html", events=events, story=story, locations=locations, decisions=decisions, objects=objects)


@verification.route("/verification/submit", methods=["POST"])
@authentication_required
@check_header
def verification_submit():
    details = request.args
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    story.verification_status = 1
    story.update_verify()
    decs = StoryDecision.dec_list_story(story_id)
    for dec in decs:
        if dec.verification_status != 3:
            dec.verification_status = 1
            dec.update_admin()
    evts = StoryEvent.event_list(story_id)
    for evt in evts:
        if evt.verification_status != 3:
            evt.verification_status = 1
            evt.update_admin()
    locs = StoryLocation.loc_list(story_id)
    for loc in locs:
        if loc.verification_status != 3:
            loc.verification_status = 1
            loc.update_admin()
    objs = StoryObject.obj_list(story_id)
    for obj in objs:
        if obj.verification_status != 3:
            obj.verification_status = 1
            obj.update_admin()
    return '{"status":"ok"}'


@verification.route("/story/treeview")
@authentication_required
@check_header
def treeview():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    locations = StoryLocation.loc_list(story_id)
    loc_id = request.args.get('location_id')
    decisions = []
    location = None
    if loc_id is not None:
        decisions = StoryDecision.dec_list_for_story_loc(story_id, loc_id)
        location = StoryLocation.get(story_id, loc_id)
    else:
        loc_id = 0
    return render_template("story/treeview.html", StoryLocation=StoryLocation, loc_id=loc_id, locations=locations, location=location, decisions=decisions, story=story)


@verification.route("/verification/treeview")
@authentication_required
@check_header
def verify_treeview():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    story_id = request.args['story_id']
    story = Story.get(story_id)
    locations = StoryLocation.loc_list(story_id)
    loc_id = request.args.get('location_id')
    decisions = []
    if loc_id is not None:
        decisions = StoryDecision.dec_list_for_story_loc(story_id, loc_id)

    location = StoryLocation.get(story_id, loc_id)
    return render_template("verification/treeview.html", StoryLocation=StoryLocation, loc_id=loc_id, locations=locations, location=location, decisions=decisions, story=story)


@verification.route("/story/run")
@authentication_required
@check_header
def story_run():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    loc_id = request.args.get("location_id")
    location = None
    if loc_id is None:
        loc_id = story.starting_loc
    location = StoryLocation.get(story_id, loc_id)
    decisions = StoryDecision.dec_list_for_story_loc(story_id, loc_id)
    objects = StoryObject.obj_list_loc(story_id, loc_id)

    cookies = request.cookies
    rundata = cookies.get("rundata")
    inv = []
    evts = []
    triggered = []
    backs = []
    if not rundata is None:
        obj = json.loads(rundata)
        for itm in obj['items']:
            inv.append(StoryObject.get(story_id, itm))
        for ent in obj['events']:
            evts.append(StoryEvent.get(story_id, ent))
        triggered = obj['decs']
        for back in obj['back']:
            backs.append(StoryLocation.get(story_id, back))

    return render_template("story/run.html", inv=inv, evts=evts, triggered=triggered, backs=backs, objects=objects, decisions=decisions, StoryEvent=StoryEvent, StoryLocation=StoryLocation, StoryObject=StoryObject, story=story, location=location)


@verification.route("/help/verification")
@check_header
def vhelp():
    return render_template("help/verification.html")


@verification.route("/help/treeview")
@check_header
def treeview_help():
    return render_template("help/treeview.html")
