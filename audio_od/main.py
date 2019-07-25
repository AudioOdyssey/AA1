#Python standard libraries
import os
import sys
import random
import hashlib
import binascii
import json
from datetime import datetime, timedelta
from functools import wraps
import base64
import re


#Third-party libraries
from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify, session, flash, send_from_directory, abort, g
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, login_url
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename
import pymysql
import pymysql.cursors
import jwt
import requests
from bs4 import BeautifulSoup as bs
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, Facebook, Google

#Internal imports
from audio_od import app
import config
from models import *
from auth import authentication_required, check_header

app = Flask(__name__)
app.secret_key = config.secret_key  
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024



UPLOAD_FOLDER = config.upload_folder

# oauth = OAuth(app)



random.seed()

@app.before_first_request
def load_id():
    token = request.cookies.get('remember_')
    if token is None:
        return redirect(url_for('home'))
    uid = decode_auth_token(token)
    if uid == 0 or uid == 'Signature expired. Please log in again.' or uid == 'Invalid token. please log in again':
        return redirect(url_for('session_new'))
    resp = make_response(url_for('home'))
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(days = 30)
    new_token = encode_auth_token(uid, current_time, expiry_time)
    resp.set_cookie("remember_", new_token, expires=expiry_time)
    return resp











@app.route("/story/object/show")
@authentication_required
@check_header
def object_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    objects = StoryObject.obj_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/object/show.html", locations=locations, events=events, objects=objects, story_id=story_id)







@app.route("/story/object/update", methods=['POST'])
@authentication_required
def object_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    object_id = details['obj_id']
    if object_id == '':
        object_id = StoryObject.get_last_id(story_id)
    name = details['obj_name']
    desc = details['obj_description']
    starting_loc = details.get('obj_starting_loc')
    if starting_loc is None:
        starting_loc = 0
    can_pickup_obj = details.get('can_pickup_obj')
    if can_pickup_obj:
        can_pickup_obj = 1
    else:
        can_pickup_obj = 0
    is_hidden = details.get('is_hidden')
    if is_hidden:
        is_hidden = 1
    else:
        is_hidden = 0
    unhide_event_id = details.get('unhide_event_id')
    if unhide_event_id is None:
        is_hidden = 0
    # unhide_event_id = details['unhide_event_id']
    obj = StoryObject.get(story_id, object_id)
    obj.unhide_event_id = unhide_event_id
    obj.verification_status = 0
    obj.update_admin()
    story.verification_status = 0
    story.update_verify()
    obj.update(story_id, object_id, name=name, starting_loc=starting_loc,
               desc=desc, can_pickup_obj=can_pickup_obj, is_hidden=is_hidden)
    # return redirect(url_for("object_show"))
    return "ok"


@app.route("/story/object/new", methods=['POST'])
@authentication_required
def object_new():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    obj = StoryObject(story_id)
    obj.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","object":{"obj_id":' + str(obj.obj_id) + '}}'


@app.route("/story/object/destroy", methods=['POST'])
@authentication_required
def object_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryObject.obj_del(request.form['story_id'], request.form['obj_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/event/show", methods=['GET'])
@authentication_required
@check_header
def event_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/show.html", locations=locations, events=events, story_id=story_id)


@app.route('/story/event/update', methods=['POST'])
@authentication_required
def event_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    if request.method == 'POST':
        details = request.form
        story_id = details['story_id']
        story = Story.get(story_id)
        if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
            abort(403)
        event_id = details['event_id']
        if event_id == '':
            event_id = StoryEvent.get_last_id(story_id)
        name = details['event_name']
        location = details.get('event_loc')
        if location is None:
            location = 0
        desc = details['ev_description']
        is_global = details.get('is_global')
        if is_global is None:
            is_global = False
        else:
            is_global = True
        evnt = StoryEvent.get(story_id, event_id)
        evnt.verification_status = 0
        evnt.update_admin()
        story.verification_status = 0
        story.update_verify()
        evnt.update(story_id, event_id, name, location, desc, is_global)
    return '{"status":"ok"}'


@app.route('/story/event/new', methods=['POST'])
@authentication_required
def event_new():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.args
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    evnt = StoryEvent(story_id)
    evnt.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","event":{"event_id":' + str(evnt.event_id) + '}}'


@app.route("/story/event/destroy", methods=['POST'])
@authentication_required
def event_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryEvent.event_del(request.form['story_id'], request.form['event_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/location/show")
@authentication_required
@check_header
def location_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/show.html", locations=locations, events=events, story_id=story_id)


@app.route("/story/location/indiv")
@authentication_required
@check_header
def location_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = request.args["location_id"]
    location = StoryLocation.get(story_id, location_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/indiv.html", location=location, locations=locations, events=events, story_id=story_id, location_id=location_id)


@app.route("/story/object/indiv")
@authentication_required
@check_header
def object_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    object_id = request.args["object_id"]
    obj = StoryObject.get(story_id, object_id)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/object/indiv.html", obj=obj, locations=locations, story_id=story_id, object_id=object_id, events=events)


@app.route("/story/location/decision/indiv")
@authentication_required
@check_header
def decision_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = request.args["location_id"]
    decision_id = request.args["decision_id"]
    decision = StoryDecision.get(story_id, location_id, decision_id)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/location/decision/indiv.html", locations=locations, decision=decision, story_id=story_id, decision_id=decision_id, events=events, objects=objects)


@app.route("/story/event/indiv")
@authentication_required
@check_header
def event_indiv():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    event_id = request.args["event_id"]
    event = StoryEvent.get(story_id, event_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/indiv.html", StoryLocation=StoryLocation, event=event, locations=locations, story_id=story_id, event_id=event_id)


@app.route('/story/location/update', methods=['POST'])
@authentication_required
def location_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    loc_id = details['loc_id']
    if loc_id is None:
        loc_id = StoryLocation.get_last_id(story_id)
    name = details.get('location_name')
    original_desc = details['location_origin_description']
    short_desc = details['location_short_description']
    post_event_description = details['location_post_event_description']
    event_id = details.get("location_event_id")
    if event_id is None:
        event_id = 0
    next_location_id = details.get('next_loc_id')
    if next_location_id is None:
        next_location_id = 0
    loc = StoryLocation.get(story_id, loc_id)
    loc.update(story_id, loc_id, name, original_desc, short_desc,
               post_event_description, event_id, next_location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route('/story/location/new', methods=['POST'])
@authentication_required
def location_new():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    loc = StoryLocation(story_id)
    loc.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","location":{"location_id":' + str(loc.location_id) + '}}'


@app.route("/story/location/destroy", methods=['POST'])
@authentication_required
def location_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryLocation.loc_del(request.form['story_id'], request.form['loc_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/location/decision/show")
@authentication_required
@check_header
def decision_show():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story = Story.get(request.args['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    decisions = StoryDecision.dec_list_for_story_loc(
        request.args['story_id'], request.args['location_id'])
    locations = StoryLocation.loc_list(
        request.args['story_id'])
    location = StoryLocation.get(
        request.args['story_id'], request.args['location_id'])
    objects = StoryObject.obj_list(
        request.args['story_id'])
  #  print(objects)
   # print(objects[0].obj_name)
    events = StoryEvent.event_list(
        request.args['story_id'])
    return render_template("story/location/decision/show.html", StoryLocation=StoryLocation, decisions=decisions, events=events, objects=objects, story_id=request.args['story_id'], locations=locations, location=location)


@app.route("/story/location/decision/update", methods=['POST'])
@authentication_required
def decision_update():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    details = request.form
    story_id = details["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = details["location_id"]
    decision_id = details['decision_id']
    if decision_id == '':
        decision_id = StoryDecision.get_last_id(story_id, location_id)
    decision_name = details['decision_name']
    sequence = details['sequence_number']
    if sequence == '':
        sequence = 0
    transition = details.get('transition')
    if transition is None:
        transition = False
    else:
        transition = True
    transition_loc_id = details.get("transition_loc_id")
    if transition_loc_id is None:
        transition_loc_id = 0
    is_hidden = details.get('hidden')
    if is_hidden is None:
        is_hidden = False
    else:
        is_hidden = True
    show_event_id = details.get("show_event_id")
    if show_event_id is None:
        show_event_id = 0
    show_object_id = details.get("show_object_id")
    if show_object_id is None:
        show_object_id = 0
    is_locked = details.get("locked")
    if is_locked is None:
        is_locked = False
    else:
        is_locked = True
    locked_descr = details.get('locked_descr')
    if locked_descr is None:
        locked_descr = ''
    unlock_event_id = details.get('unlock_event_id')
    if unlock_event_id is None:
        unlock_event_id = 0
    unlock_obj_id = details.get("unlock_object_id")
    if unlock_obj_id is None:
        unlock_obj_id = 0
    aftermath_desc = details['aftermath_desc']
    cause_event = details.get('cause_event')
    if cause_event is None:
        cause_event = False
    else:
        cause_event = True
    effect_event_id = details.get('effect_event_id')
    if effect_event_id is None:
        effect_event_id = 0
    dec_description = details['dec_description']
    can_occur_once = details.get("can_occur_once")
    if can_occur_once is None:
        can_occur_once = False
    else:
        can_occur_once = True
    is_locked_by_event_id = details.get("is_locked_by_event_id")
    if is_locked_by_event_id is None:
        is_locked_by_event_id = 0
    locked_by_event_desc = details.get("locked_by_event_description")
    if locked_by_event_desc is None:
        locked_by_event_desc = ""
    dec = StoryDecision.get(story_id, location_id, decision_id)
    dec.update(story_id, decision_id, location_id, sequence, decision_name, transition, transition_loc_id, is_hidden, is_locked, dec_description, show_event_id,
               show_object_id, unlock_event_id, unlock_obj_id, locked_descr, aftermath_desc, cause_event, effect_event_id, can_occur_once, is_locked_by_event_id, locked_by_event_desc)
    dec.verification_status = 0
    dec.update_admin()
    loc = StoryLocation.get(story_id, location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@app.route("/story/location/decision/new", methods=['POST'])
@authentication_required
def decision_new():
    # if "logged_in" not in session:
        # return redirect(url_for("session_new"))
    details = request.args
    story_id = details["story_id"]
    story = Story.get(story_id)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = details["location_id"]
    dec = StoryDecision(story_id, location_id)
    dec.add_to_server()
    loc = StoryLocation.get(story_id, location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","decision":{"decision_id":' + str(dec.decision_id) + '}}'


@app.route("/story/location/decision/destroy", methods=['POST'])
@authentication_required
def decision_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryDecision.dec_del(
        request.form['story_id'], request.form['location_id'], request.form['decision_id'])
    loc = StoryLocation.get(
        request.form['story_id'], request.form['location_id'])
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'






@app.route("/verification/view")
@authentication_required
@check_header
def verification_view():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    if not checkEditorAdmin(getUid()):
        abort(403)
    stories = Story.story_list_ready_for_verification()
    return render_template("verification/view.html", stories=stories)


@app.route("/verification/review")
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
    return render_template("verification/review.html", StoryLocation=StoryLocation, StoryEvent=StoryEvent, story=story, story_id=story_id, objects=objects, locations=locations, events=events, decisions=decisions)


@app.route("/verification/review/update", methods=['POST'])
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
        obj.is_verified = is_verified
        obj.update_admin()
    elif entity_type.lower() == 'location':
        loc = StoryLocation.get(story_id, ent_id)
        loc.reviewer_comments = reviewer_comment
        loc.is_verified = is_verified
        loc.update_admin()
    elif entity_type.lower() == 'event':
        evnt = StoryEvent.get(story_id, ent_id)
        evnt.reviewer_comments = reviewer_comment
        evnt.is_verified = is_verified
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
            story.story_in_store=False
        story.update_verify()
    else:
        loc_id = details['loc_id']
        dec = StoryDecision.get(story_id, loc_id, ent_id)
        dec.reviewer_comments = reviewer_comment
        dec.is_verified = is_verified
        dec.update_admin()
    return '{"status":"ok"}'


@app.route("/verification/status")
@authentication_required
@check_header
def verification_story():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    uid = getUid()
    if not checkEditorAdmin(uid):
        abort(403)
    story_id = request.args["story_id"]
    locations = StoryLocation.loc_list(story_id)
    decisions = StoryDecision.dec_list_story(story_id)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("verification/status.html", events=events, story_id=story_id, locations=locations, decisions=decisions, objects=objects)


@app.route("/verification/submit", methods=["POST"])
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


@app.route("/story/treeview")
@authentication_required
@check_header
def treeview():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    story = Story.get(story_id)
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


@app.route("/verification/treeview")
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


@app.route("/story/run")
@authentication_required
@check_header
def story_run():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
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




@app.route("/verification/help")
@authentication_required
@check_header
def vhelp():
    return render_template("verification/help.html")


@app.route("/story/treeview_help")
@authentication_required
@check_header
def treeview_help():
    story_id = request.args['story_id']
    story = Story.get(story_id)
    return render_template("story/treeview_help.html", story=story)









# @login_manager.unauthorized_handler
# def unauthorized():
#     return redirect(url_for("session_new"))



