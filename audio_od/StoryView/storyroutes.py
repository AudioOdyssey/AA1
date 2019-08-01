#Python standard libraries
import os
import sys
import json
import base64

#Third-party libraries
from flask import redirect, render_template, request, Blueprint

#Internal imports
from models import Story, StoryObject, StoryLocation, StoryEvent
from audio_od.utils import authentication_required, check_header, checkEditorAdmin, getUid

story_view = Blueprint("story", __name__)

@story_view.route("/story/update", methods=["GET"])
@authentication_required
@check_header
def story_update():
    """Endpoint for updating objects. If the wrong user is accessing the story, a 403 will be thrown. 
    If the story does not exist, a 404 will be thrown."""
    story = Story.get(int(request.args['story_id']))
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    objects = StoryObject.obj_list(request.args['story_id'])
    events = StoryEvent.event_list(request.args['story_id'])
    locations = StoryLocation.loc_list(request.args['story_id'])
    coverimage = story.get_image_base64().decode("utf-8")
    return render_template("story/update.html", StoryLocation=StoryLocation, story=story, objects=objects, events=events, locations=locations, coverimage=coverimage)



@story_view.route("/story/image")
@authentication_required
@check_header
def story_image():
    """Endpoint for viewing story covers images. If the wrong user is accessing the story,
    a 403 will be thrown. If the story does not exist, a 404 will be thrown. """
    story = Story.get(int(request.args['story_id']))
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    return story.get_image_base64()


valid_genres = {"Mystery", "Romance", "Sci-Fi", "Fantasy", "Historical Fiction", "Drama",
                "Horror", "Thriller", "Comedy", "Adventure", "Sports", "Non-Fiction", "Other Fiction"}


@story_view.route("/story/update", methods=["POST"])
@authentication_required
def story_update_post():
    """Endpoint for updating stories. If the wrong user is accessing the story,
    a 403 will be thrown. If the story does not exist, a 404 will be thrown. The GET and POST methods are done asynchrously."""
    details = request.form
    story_id = request.form.get('story_id')
    story = Story.get(story_id)
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    story_title = details['story_title']
    story_synopsis = details['story_synopsis']
    story_price = details['story_price']
    genre = details.get('genre')
    if genre is None or genre not in valid_genres:
        genre = "Miscellaneous"
    story.length_of_story = details['length_of_story']
    story.inventory_size = details.get('inventory_size')
    story.starting_loc = details.get('starting_loc')
    story.story_id = story_id
    filename = ''
    file = request.files['cover']
    if file.filename == '':
        pass
    if file and allowed_file(file):
        filename = str(story_id) + ".jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'covers', filename))
    story.verification_status = 0
    story.update_verify()
    story.update(story_title, "", story_price, 0, genre, story_synopsis)
    #story_title, story_author, story_price, story_language_id, length_of_story, genre, story_synopsis, inventory_size
    return '{"status":"ok"}'


@story_view.route("/story/destroy", methods=["POST"])
@authentication_required
def story_destroy():
    """Endpoint for destroying.If the wrong user is accessing the story,
    a 403 will be thrown. If the story does not exist, a 404 will be thrown."""
    story = Story.get(request.args['story_id'])
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkAdmin(getUid()):
        abort(403)
    Story.destroy(request.args['story_id'])
    return '{"status":"ok"}'


valid_mimetypes = ['image/jpeg', 'image/png', 'image/bmp']


def allowed_file(file):
    mimetype = file.content_type
    return mimetype in valid_mimetypes


@story_view.route("/story/new", methods=["POST"])
@authentication_required
def story_new():
    """Endpoint for creating new stories. A json with the story_id and status is returned."""
    uid = getUid()
    story = Story(user_creator_id=uid)
    story.story_synopsis = ""
    story.add_to_server()
    return '{"status":"ok", "story": {"story_id":' + str(story.story_id) + '}}'


@story_view.route("/app/story/info", methods=['GET'])
def app_story_logistics():
    """Returns all the objects, locations, decisions, events in the story. Also, returns the story cover. This endpoint is for the app."""
    return Story.get_entities(int(request.args.get('story_id')))


@story_view.route("/app/store", methods=["GET"])
def app_store_info():
    """Endpoint for app. Sends all the stories ready for the store. Returns basic info, such as price, author, genre, synopsis of the story"""
    return Story.display_for_store()


@story_view.route("/store/story/info", methods=['GET'])
def app_store_expand():
    """Endpoint for app. If user taps on the story, more info about the story will be given."""
    details = request.json
    story_id = details.get("story_id")
    return Story.get_info(story_id)


@story_view.route("/story/publish", methods=["POST"])
@authentication_required
@check_header
def story_publish():
    """Endpoint for allowing users to publish stories. IF successful, will return a json with the status"""
    story = Story.get(int(request.args['story_id']))
    if story is None:
        abort(404)
    if story.user_creator_id != getUid() and not checkEditorAdmin(getUid()):
        abort(403)
    if story.verification_status != 3:
        abort(403)
    story.story_in_store = 1
    story.update_verify()
    return '{"status":"ok"}'

@story_view.route("/story/treeview")
@authentication_required
@check_header
def treeview():
    """This allows the writer to see all the story in a treeview, rather than the conventional in-line mode. 
    Users can click on the decisions to see what the next locations will contain.If the user does not have correct permissions, then a 403 will be thrown.
    If the story does not exist, a 404 will be thrown."""
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


@story_view.route("/story/run")
@authentication_required
@check_header
def story_run():
    """Allows the user to test the way the story plays. Functions the same the execution cycle in the app functions. The writer can play the story with this endpoint. 
    If the user doesn't have correct permissions, then a 403 will be thrown. If the story does not exist, then a 404 will be thrown."""
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
