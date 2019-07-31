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
    uid = getUid()
    story = Story(user_creator_id=uid)
    story.story_synopsis = ""
    story.add_to_server()
    return '{"status":"ok", "story": {"story_id":' + str(story.story_id) + '}}'


@story_view.route("/app/story/info", methods=['GET'])
def app_story_logistics():
    return Story.get_entities(int(request.args.get('story_id')))


@story_view.route("/app/store", methods=["GET"])
def app_store_info():
    return Story.display_for_store()


@story_view.route("/store/story/info", methods=['GET'])
def app_store_expand():
    details = request.json
    story_id = details.get("story_id")
    return Story.get_info(story_id)


@story_view.route("/help/story")
@check_header
def help():
    return render_template("help/story.html")


@story_view.route("/story/publish", methods=["POST"])
@authentication_required
@check_header
def story_publish():
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