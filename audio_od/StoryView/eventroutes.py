#Python standard libraries
import os
import sys

#Third-party libraries
from flask import redirect, render_template, request, url_for

#Internal imports
from audio_od import app
import StoryView
import config
from models import Story, StoryEvent, StoryLocation, StoryDecision
from auth import authentication_required, check_header, checkEditorAdmin, getUid


@StoryView.route("/story/event/show", methods=['GET'])
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


@StoryView.route('/story/event/update', methods=['POST'])
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


@StoryView.route('/story/event/new', methods=['POST'])
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


@StoryView.route("/story/event/destroy", methods=['POST'])
@authentication_required
def event_destroy():
    story = Story.get(request.form['story_id'])
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryEvent.event_del(request.form['story_id'], request.form['event_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@StoryView.route("/story/event/indiv")
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
