#Python standard libraries
import os
import sys

#Third-party libraries
from flask import redirect, render_template, request, Blueprint
#Internal imports
from audio_od.models import Story, StoryEvent, StoryLocation, StoryDecision
from audio_od.utils import authentication_required, check_header, checkEditorAdmin, getUid

ev_view = Blueprint("ev", __name__)

@ev_view.route("/story/event/show", methods=['GET'])
@authentication_required
@check_header
def event_show():
    """Endpoint for viewing all the events. If the story of the event isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the event does not exist, a 404 will be thrown."""
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/show.html", locations=locations, events=events, story_id=story_id)


@ev_view.route('/story/event/update', methods=['POST'])
@authentication_required
def event_update():
    """Endpoint for updating events. If the story of the events isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the event does not exist, a 404 will be thrown."""
    if request.method == 'POST':
        details = request.form
        story_id = details['story_id']
        story = Story.get(story_id)
        if story is None:
            abort(404)
        if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
            abort(403)
        event_id = details['event_id']
        if event_id == '':
            event_id = StoryEvent.get_last_id(story_id)
        name = details['event_name']
        location = details.get('event_loc', 0)
        desc = details['ev_description']
        is_global = details.get('is_global', False)
        if is_global != False: 
            is_global = True
        evnt = StoryEvent.get(story_id, event_id)
        if evnt is None:
            abort(404)
        evnt.verification_status = 0
        evnt.update_admin()
        story.verification_status = 0
        story.update_verify()
        evnt.update(story_id, event_id, name, location, desc, is_global)
    return '{"status":"ok"}'


@ev_view.route('/story/event/new', methods=['POST'])
@authentication_required
def event_new():
    """Endpoint for creating new events. If the story of the event isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the event does not exist, a 404 will be thrown."""
    details = request.args
    story_id = details['story_id']
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    evnt = StoryEvent(story_id)
    evnt.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","event":{"event_id":' + str(evnt.event_id) + '}}'


@ev_view.route("/story/event/destroy", methods=['POST'])
@authentication_required
def event_destroy():
    """Endpoint for deleting individual events. If the story of the event isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the event does not exist, a 404 will be thrown."""
    story = Story.get(request.form['story_id'])
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryEvent.event_del(request.form['story_id'], request.form['event_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@ev_view.route("/story/event/indiv")
@authentication_required
@check_header
def event_indiv():
    """Endpoint for viewing individual events. If the story of the event isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the event does not exist, a 404 will be thrown."""
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    event_id = request.args["event_id"]
    event = StoryEvent.get(story_id, event_id)
    if event is None:
        abort(404)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/indiv.html", StoryLocation=StoryLocation, event=event, locations=locations, story_id=story_id, event_id=event_id)
