#Python standard libraries
import os
import sys

#Third-party libraries
from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify, session, flash, send_from_directory, abort, g, Blueprint


#Internal imports
from audio_od.models import Story, StoryLocation, StoryDecision, StoryObject, StoryEvent
from audio_od.utils import authentication_required, check_header, checkEditorAdmin, getUid

dec_view = Blueprint("dec", __name__)


@dec_view.route("/story/location/decision/show")
@authentication_required
@check_header
def decision_show():
    """Endpoint for viewing all the  decisions. If the story of the decision isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the decision does not exist, a 404 will be thrown."""
    story = Story.get(request.args['story_id'])
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    decisions = StoryDecision.dec_list_for_story_loc(request.args['story_id'], request.args['location_id'])
    locations = StoryLocation.loc_list(request.args['story_id'])
    location = StoryLocation.get(request.args['story_id'], request.args['location_id'])
    objects = StoryObject.obj_list(request.args['story_id'])
  #  print(objects)
   # print(objects[0].obj_name)
    events = StoryEvent.event_list(
        request.args['story_id'])
    return render_template("story/location/decision/show.html", StoryLocation=StoryLocation, decisions=decisions, events=events, objects=objects, story_id=request.args['story_id'], locations=locations, location=location)


@dec_view.route("/story/location/decision/update", methods=['POST'])
@authentication_required
def decision_update():
    """Endpoint for updating decisions. If the story of the decision isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the decision does not exist, a 404 will be thrown."""
    details = request.form
    story_id = details["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
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
    transition = details.get('transition', False)
    if transition is not None:
        transition = True
    transition_loc_id = details.get("transition_loc_id", 0)
    is_hidden = details.get('hidden', False)
    if is_hidden is not None:
        is_hidden = True
    show_event_id = details.get("show_event_id", 0)
    show_object_id = details.get("show_object_id", 0)
    is_locked = details.get("locked", False)
    if is_locked is not None:
        is_locked = True
    locked_descr = details.get('locked_descr', '')
    unlock_event_id = details.get('unlock_event_id', 0)
    unlock_obj_id = details.get("unlock_object_id", 0)
    aftermath_desc = details['aftermath_desc']
    cause_event = details.get('cause_event', False)
    if cause_event is not None:
        cause_event = True
    effect_event_id = details.get('effect_event_id', 0)
    dec_description = details['dec_description']
    can_occur_once = details.get("can_occur_once", False)
    if can_occur_once is not None:
        can_occur_once = True
    is_locked_by_event_id = details.get("is_locked_by_event_id", 0)
    locked_by_event_desc = details.get("locked_by_event_description", '')
    reset_story = details.get("reset_story", False)
    if reset_story is not None:
        reset_story = True
    dec = StoryDecision.get(story_id, location_id, decision_id)
    if dec is None:
        abort(404)
    dec.update(story_id, decision_id, location_id, sequence, decision_name, transition, transition_loc_id, is_hidden, is_locked, dec_description, show_event_id,
               show_object_id, unlock_event_id, unlock_obj_id, locked_descr, aftermath_desc, 
               cause_event, effect_event_id, can_occur_once, is_locked_by_event_id, locked_by_event_desc, reset_story)
    dec.verification_status = 0
    dec.update_admin()
    loc = StoryLocation.get(story_id, location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok"}'


@dec_view.route("/story/location/decision/new", methods=['POST'])
@authentication_required
def decision_new():
    """Endpoint for creating new decisions. If the story of the decision isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the decision does not exist, a 404 will be thrown."""
    details = request.args
    story_id = details["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = details["location_id"]
    loc = StoryLocation.get(story_id, location_id)
    if loc is None:
        abort(404)
    dec = StoryDecision(story_id, location_id)
    dec.add_to_server()
    loc = StoryLocation.get(story_id, location_id)
    loc.verification_status = 0
    loc.update_admin()
    story.verification_status = 0
    story.update_verify()
    return '{"status":"ok","decision":{"decision_id":' + str(dec.decision_id) + '}}'


@dec_view.route("/story/location/decision/destroy", methods=['POST'])
@authentication_required
def decision_destroy():
    """Endpoint for deleting individual decisions. If the story of the decision isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the decision does not exist, a 404 will be thrown."""
    story = Story.get(request.form['story_id'])
    if story is None:
        abort(404)
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


@dec_view.route("/story/location/decision/indiv")
@authentication_required
@check_header
def decision_indiv():
    """Endpoint for viewing individual decisions. If the story of the decision isn't first chosen, then a 404 will be thrown. If the wrong user is accessing the story,
    a 403 will be thrown. If the decision does not exist, a 404 will be thrown."""
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    location_id = request.args["location_id"]
    decision_id = request.args["decision_id"]
    decision = StoryDecision.get(story_id, location_id, decision_id)
    if decision is None:
        abort(404)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/location/decision/indiv.html", locations=locations, decision=decision, story_id=story_id, decision_id=decision_id, events=events, objects=objects)
