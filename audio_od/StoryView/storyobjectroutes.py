#Python standard libraries
import os
import sys

#Third-party libraries
from flask import render_template, request, Blueprint

#Internal imports
from models import Story, StoryObject, StoryLocation, StoryEvent
from audio_od.utils import authentication_required, check_header, checkEditorAdmin, getUid

obj_view = Blueprint("obj", __name__)

@obj_view.route("/story/object/show")
@authentication_required
@check_header
def object_show():
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    objects = StoryObject.obj_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/object/show.html", locations=locations, events=events, objects=objects, story_id=story_id)


@obj_view.route("/story/object/update", methods=['POST'])
@authentication_required
def object_update():
    details = request.form
    story_id = details['story_id']
    story = Story.get(story_id)
    if story is None:
        abort(404)
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
    if obj is None:
        abort(404)
    obj.unhide_event_id = unhide_event_id
    obj.verification_status = 0
    obj.update_admin()
    story.verification_status = 0
    story.update_verify()
    obj.update(story_id, object_id, name=name, starting_loc=starting_loc,
               desc=desc, can_pickup_obj=can_pickup_obj, is_hidden=is_hidden)
    return "ok"


@obj_view.route("/story/object/new", methods=['POST'])
@authentication_required
def object_new():
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    obj = StoryObject(story_id)
    obj.add_to_server()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","object":{"obj_id":' + str(obj.obj_id) + '}}'


@obj_view.route("/story/object/destroy", methods=['POST'])
@authentication_required
def object_destroy():
    story = Story.get(request.form['story_id'])
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    StoryObject.obj_del(request.form['story_id'], request.form['obj_id'])
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@obj_view.route("/story/object/indiv")
@authentication_required
@check_header
def object_indiv():
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    object_id = request.args["object_id"]
    obj = StoryObject.get(story_id, object_id)
    if obj is None:
        abort(404)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/object/indiv.html", obj=obj, locations=locations, story_id=story_id, object_id=object_id, events=events)
