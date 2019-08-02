#Python standard libraries
import os
import sys

#Third-party libraries
from flask import render_template, request, Blueprint

#Internal imports
from audio_od.models import Story, StoryLocation, StoryEvent
from audio_od.utils import authentication_required, check_header, checkEditorAdmin, getUid

loc_view = Blueprint("loc", __name__)

@loc_view.route("/story/location/show")
@authentication_required
@check_header
def location_show():
    """Endpoint for viewing all the locations. If the story of the location isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the location does not exist, a 404 will be thrown."""
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/show.html", locations=locations, events=events, story_id=story_id)

@loc_view.route('/story/location/update', methods=['POST'])
@authentication_required
def location_update():
    """Endpoint for updating locations. If the story of the location isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the location does not exist, a 404 will be thrown."""
    details = request.form
    story_id = details['story_id']
    story = Story.get(story_id)
    if story is None:
        abort(404)
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
    if loc is None:
        abort(404)
    loc.update(story_id, loc_id, name, original_desc, short_desc,
               post_event_description, event_id, next_location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@loc_view.route('/story/location/new', methods=['POST'])
@authentication_required
def location_new():
    """Endpoint for creating new locations. If the story of the location isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the location does not exist, a 404 will be thrown."""
    story_id = request.args['story_id']
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    loc = StoryLocation(story_id)
    loc.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","location":{"location_id":' + str(loc.location_id) + '}}'





@loc_view.route("/story/location/destroy", methods=['POST'])
@authentication_required
def location_destroy():
    """Endpoint for deleting individual locations. If the story of the locations isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the locations does not exist, a 404 will be thrown."""
    story = Story.get(request.form['story_id'])
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryLocation.loc_del(request.form['story_id'], request.form['loc_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@loc_view.route("/story/location/indiv")
@authentication_required
@check_header
def location_indiv():
    """Endpoint for viewing individual locations. If the story of the locations isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the location does not exist, a 404 will be thrown."""
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = request.args["location_id"]
    location = StoryLocation.get(story_id, location_id)
    if location is None:
        abort(404)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/indiv.html", location=location, locations=locations, events=events, story_id=story_id, location_id=location_id)