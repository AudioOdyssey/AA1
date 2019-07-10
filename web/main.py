from models.storyobject import StoryObject
from models.User import User
from models.story import Story
from models.storyevent import StoryEvent
from models.storylocation import StoryLocation
from models.storydecision import StoryDecision

from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify, session, flash, send_from_directory, abort
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, login_url

from werkzeug.utils import secure_filename

import pymysql
import pymysql.cursors

import os
import sys

import random
import hashlib
import binascii

import json

from datetime import datetime, timedelta

import jwt

UPLOAD_FOLDER = '/var/www/pictures/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.secret_key = b"jk_\xf7\xa7':\xea$/\x88\xc0\xa3\x0e:d"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "session/new.html"
login_manager.login_message = "Please login"

REGION = 'us-east-2b'

rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
name = "AA_admin"
rds_password = "z9QC3pvQ"
db_name = "audio_adventures_dev"

random.seed()


@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    return render_template("index.html")


@app.route("/user/new", methods=['GET', 'POST'])
def user_new():  # fix later
    if request.method == "POST":
        details = request.form
        username = details['username']
        raw_password = details['password']
        email = details['email_address']
        gender = int(details['gender'])
        country_of_origin = (details['country_of_origin'])
        profession = details['profession']
        disabilities = details.get('disabilities')
        if disabilities is None:
            disabilities_bool = 0
        else:
            disabilities_bool = 1
        language = int(details['language-id'])
        first_name = details['first_name']
        last_name = details['last_name']
        date_of_birth = datetime.strptime(
            details['birth-year'] + "-" + details['birth-month'] + "-" + details['birth-day'], '%Y-%m-%d')
        usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin,
                   profession_input=profession, disabilities_input=disabilities_bool, date_of_birth_input=date_of_birth,
                   first_name_input=first_name, last_name_input=last_name, language=language)
        usr.add_to_server()
    return render_template("user/new.html")


@app.route("/app/user/new", methods=['POST', 'GET'])
def app_user_new():
    result = {}
    if request.method == "POST":
        details = request.get_json(force=True)
        user_id = sign_up(details)
        if user_id:
            result['user_id'] = str(user_id)
            result['message'] = "Successfully registered"
        else:
            result['message'] = 'Username already exists'
    return make_response(json.dumps(result))


def sign_up(details_dict):
    username = details_dict['username']
    raw_password = details_dict['password']
    email = details_dict['email_address']
    gender = int(details_dict['gender'])
    country_of_origin = details_dict['country_of_origin']
    profession = details_dict['profession']
    disabilities = bool(details_dict['disabilities'])
    if disabilities:
        disabilities_bool = 1
    else:
        disabilities_bool = 0
    language = int(details_dict['language_id'])
    first_name = details_dict['first_name']
    last_name = details_dict['last_name']
    # date_of_birth = datetime.strptime(details_dict['date_of_birth'], '%Y-%m-%d')
    usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin,
               profession_input=profession, disabilities_input=disabilities_bool,
               first_name_input=first_name, last_name_input=last_name, language=language)
    if usr.add_to_server():
        return usr.get_id()
    else:
        return None


@app.route("/session/new", methods=['GET', 'POST'])
def session_new():
    error = None
    if request.method == 'POST':
        details = request.form
        if authenticate(details):
            resp = make_response(redirect(url_for('story_show')))
            if 'remember' in details:
                selector = os.urandom(16).decode('latin-1')
                validator = os.urandom(16).decode('latin-1')
                expired_date = datetime.utcnow() + timedelta(days = 30)
                resp.set_cookie("remember_", (selector + ":" + validator), expires = expired_date)
                rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
                name = "AA_admin"
                rds_password = "z9QC3pvQ"
                db_name = "audio_adventures_dev"
                conn = pymysql.connect(
                    rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
                with conn.cursor() as cur:
                    hashedValidator = hashlib.sha256(validator.encode()).digest()
                    hashed_validator_hexstring = binascii.b2a_hex(hashedValidator)
                    cur.execute(("SELECT userid from `auth_tokens`"))
                    query_data = cur.fetchall()
                    if query_data[0] != session['user_id']:
                        cur.execute(("INSERT INTO `auth_tokens`(selector, hashedValidator, userid, expires) VALUES (%s, %s, %s, %s)"),
                                    (selector, hashed_validator_hexstring, session['user_id'], expired_date))
                        cur.commit()
                conn.close()
            return resp
        else:
            error = "Username and/or password not valid"
    return render_template("session/new.html", error=error)

def authentication_required():
    def func_wrapper():
        if 'user_id' not in session:
            remember_me = request.cookies.get('remember_')
            
        

def authenticate(details):
    conn = pymysql.connect(rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5,
                           cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        username = details['username']
        cur.execute(("SELECT * FROM users WHERE username = %s"), username)
        result = cur.fetchone()
        if(result is None):
            return False
        else:
            usr = load_user(result['user_id'])
            if(usr.authenticate(details['password'])):
                session['logged_in'] = True
                session['user_id'] = result['user_id']
                return True
            else:
                return False
    return True


@app.route("/app/session/new", methods=['POST', 'GET'])
def app_session_new():
    message = None
    result = None
    if request.method == 'POST':
        details = request.json
        if authenticate(details):
            session['platform'] = 'app'
        else:
            message = "Username and/or password is not valid"
    if message is None:
        result = {
            'user_id': str(session['user_id']),
            'auth_token': encode_auth_token(str(session['user_id']))
        }
    else:
        result = {
            'message': message
        }
    return jsonify(result)


def encode_auth_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=7, seconds=5),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        app.secret_key,
        algorithm='HS256'
    )


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, app.secret_key)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. please log in again'


@app.route("/app/session/logout")
def app_logout():
    session.pop("logged_in", None)
    session.pop("user_id", None)
    session.pop("platform", None)
    return redirect(url_for("home"))


@app.route("/session/logout", methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        if "logged_in" in session:
            session.pop("logged_in", None)
            usr = User.get(session.get('user_id'))
            usr.is_authenticated = False
            return redirect(url_for("home"))
        else:
            return redirect(url_for("session_new"))


@app.route("/story/show")
def story_show():
    print(request.cookies.get('sucess'))
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    stories = Story.story_list_by_creator(session['user_id'])
    return render_template("story/show.html", stories=stories)


@app.route("/story/update", methods=["GET"])  # THIS NEEDS TO BE FINISHED
def story_update():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story = Story.get(int(request.args['story_id']))
    objects = StoryObject.obj_list(request.args['story_id'])
    events = StoryEvent.event_list(request.args['story_id'])
    locations = StoryLocation.loc_list(request.args['story_id'])
    return render_template("story/update.html", StoryLocation=StoryLocation, story=story, objects=objects, events=events, locations=locations)


@app.route("/story/image")
def story_image():
    story = Story.get(int(request.args['story_id']))
    # print(story.get_image_base64())
    return story.get_image_base64()


@app.route("/story/update", methods=["POST"])
def story_update_post():
    details = request.form
    story_id = request.form.get('story_id')
    story = Story.get(story_id)
    story_title = details['story_title']
    story_synopsis = details['story_synopsis']
    story_price = details['story_price']
    genre = details.get('genre')
    if genre is None:
        genre = "Miscellaneous"
    story.length_of_story = details['length_of_story']
    story.inventory_size = details.get('inventory_size')
    story.starting_loc = details.get('starting_loc')
    story.story_id = story_id
    filename = ''
    file = request.files['cover']
    if file.filename == '':
        pass
    if file and allowed_file(file.filename):
        filename = str(story_id) + ".jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    story.update(story_title, "", story_price, 0, genre, story_synopsis)

    #story_title, story_author, story_price, story_language_id, length_of_story, genre, story_synopsis, inventory_size
    return '{"status":"ok"}'


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/story/new", methods=["POST"])
def story_new():
    story = Story(user_creator_id=session['user_id'])
    story.story_synopsis = ""
    story.add_to_server()
    return '{"status":"ok", "story": {"story_id":' + str(story.story_id) + '}}'


#### THIS WORKS #####
@app.route("/story/object/show")
def object_show():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    objects = StoryObject.obj_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/object/show.html", locations=locations, events=events, objects=objects, story_id=story_id)


@app.route("/appmys/story/info", methods=['GET'])
def app_story_logistics():
    return Story.get_entities(int(request.args.get('story_id')))


@app.route("/app/store", methods=["GET"])
def app_store_info():
    return Story.display_for_store()


@app.route("/store/story/info", methods=['GET'])
def app_store_expand():
    details = request.json
    story_id = details.get("story_id")
    return Story.get_info(story_id)


@app.route("/app/library/", methods=['GET'])
def stories_show_owned_by_user():
    user_id = request.args.get("user_id")
    return Story.json_story_library(user_id)


@app.route("/story/object/update", methods=['POST'])
def object_update():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
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
    obj.update(story_id, object_id, name=name, starting_loc=starting_loc,
               desc=desc, can_pickup_obj=can_pickup_obj, is_hidden=is_hidden)
    # return redirect(url_for("object_show"))
    return "ok"


@app.route("/story/object/new", methods=['POST'])
def object_new():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    obj = StoryObject(story_id)
    obj.add_to_server()
    return '{"status":"ok","object":{"obj_id":' + str(obj.obj_id) + '}}'


@app.route("/story/object/destroy", methods=['POST'])
def object_destroy():
    StoryObject.obj_del(request.form['obj_id'])
    return '{"status":"ok"}'


#### STILL NEEDS WORK ####
@app.route("/story/event/show", methods=['GET'])
def event_show():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/show.html", locations=locations, events=events, story_id=story_id)


@app.route('/story/event/update', methods=['POST'])
def event_update():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    if request.method == 'POST':
        details = request.form
        story_id = details['story_id']
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
        evnt.update(story_id, event_id, name, location, desc, is_global)
    return '{"status":"ok"}'


@app.route('/story/event/new', methods=['POST'])
def event_new():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    details = request.args
    story_id = details['story_id']
    evnt = StoryEvent(story_id)
    evnt.add_to_server()
    return '{"status":"ok","event":{"event_id":' + str(evnt.event_id) + '}}'


@app.route("/story/event/destroy", methods=['POST'])
def event_destroy():
    StoryEvent.event_del(request.form['event_id'])
    return '{"status":"ok"}'


@app.route("/story/location/show")
def location_show():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/show.html", locations=locations, events=events, story_id=story_id)


@app.route("/story/location/indiv")
def location_indiv():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    location_id = request.args["location_id"]
    location = StoryLocation.get(story_id, location_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("story/location/indiv.html", location=location, locations=locations, events=events, story_id=story_id, location_id=location_id)


@app.route("/story/object/indiv")
def object_indiv():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    object_id = request.args["object_id"]
    obj = StoryObject.get(story_id, object_id)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/object/indiv.html", obj=obj, locations=locations, story_id=story_id, object_id=object_id, events=events)


@app.route("/story/location/decision/indiv")
def decision_indiv():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    location_id = request.args["location_id"]
    decision_id = request.args["decision_id"]
    decision = StoryDecision.get(story_id, location_id, decision_id)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/location/decision/indiv.html", locations=locations, decision=decision, story_id=story_id, decision_id=decision_id, events=events, objects=objects)


@app.route("/story/event/indiv")
def event_indiv():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    event_id = request.args["event_id"]
    event = StoryEvent.get(story_id, event_id)
    locations = StoryLocation.loc_list(story_id)
    return render_template("story/event/indiv.html", StoryLocation=StoryLocation, event=event, locations=locations, story_id=story_id, event_id=event_id)


@app.route('/story/location/update', methods=['POST'])
def location_update():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
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
    auto_goto = details.get('auto_goto')
    if auto_goto is None:
        auto_goto = 0
    else:
        auto_goto = 1
    next_location_id = details.get('next_loc_id')
    if next_location_id is None:
        next_location_id = 0
    loc = StoryLocation.get(story_id, loc_id)
    loc.update(story_id, loc_id, name, original_desc, short_desc,
               post_event_description, event_id, auto_goto, next_location_id)
    return '{"status":"ok"}'


@app.route('/story/location/new', methods=['POST'])
def location_new():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    loc = StoryLocation(story_id)
    loc.add_to_server()
    return '{"status":"ok","location":{"location_id":' + str(loc.location_id) + '}}'


@app.route("/story/location/destroy", methods=['POST'])
def location_destroy():
    StoryLocation.loc_del(request.form['loc_id'])
    return '{"status":"ok"}'


#### DECISIONS WORK ####
@app.route("/story/location/decision/show")
def decision_show():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
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
def decision_update():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    details = request.form
    story_id = details["story_id"]
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
    return '{"status":"ok"}'


@app.route("/story/location/decision/new", methods=['POST'])
def decision_new():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    details = request.args
    story_id = details["story_id"]
    location_id = details["location_id"]
    dec = StoryDecision(story_id, location_id)
    dec.add_to_server()
    return '{"status":"ok","decision":{"decision_id":' + str(dec.decision_id) + '}}'


@app.route("/story/location/decision/destroy", methods=['POST'])
def decision_destroy():
    StoryDecision.dec_del(request.form['decision_id'])
    return '{"status":"ok"}'


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/verification/view")
def verification_view():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    stories = Story.story_list_ready_for_verification()
    return render_template("verification/view.html", stories=stories)


@app.route("/verification/review")
def verification_review():
    story_id = request.args["story_id"]
    story = Story.get(story_id)
    objects = StoryObject.obj_list(story_id)
    locations = StoryLocation.loc_list(story_id)
    events = StoryEvent.event_list(story_id)
    decisions = StoryDecision.dec_list_story(story_id)
    return render_template("verification/review.html", story=story, story_id=story_id, objects=objects, locations=locations, events=events, decisions=decisions)


@app.route("/verification/review/update", methods=['POST'])
def review_update():
    details = request.form
    story_id = details['story_id']
    entity_type = details['type']
    ent_id = details['ent_id']
    is_verified = details.get('is_verified')
    if is_verified is None:
        is_verified = False
    else:
        is_verified = True
    reviewer_comment = details['comment']
    if entity_type.lower() == 'object':
        obj = StoryObject.get(story_id, ent_id)
        obj.update_admin(is_verified, reviewer_comment)
    elif entity_type.lower() == 'location':
        loc = StoryLocation.get(story_id, ent_id)
        loc.update_admin(is_verified, reviewer_comment)
    elif entity_type.lower() == 'event':
        evnt = StoryEvent.get(story_id, ent_id)
        evnt.update_admin(is_verified, reviewer_comment)
    elif entity_type.lower() == 'story':
        parental_rating = details['parental_ratings']
        usr = User.get(session['user_id'])
        verifier_name = usr.username
        stry = Story.get(story_id)
        stry.update_admin(reviewer_comment, parental_rating, verifier_name)
    else:
        loc_id = details['loc_id']
        dec = StoryDecision.get(story_id, loc_id, ent_id)
        dec.update_admin(reviewer_comment, is_verified)
    return '{"status":"ok"}'


@app.route("/verification/object")
def verification_object():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    object_id = request.args["object_id"]
    obj = StoryObject.get(story_id, object_id)
    return render_template("verification/object.html", obj=obj, story_id=story_id, object_id=object_id)


@app.route("/verification/location")
def verification_location():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    location_id = request.args["location_id"]
    location = StoryLocation.get(story_id, location_id)
    decisions = StoryDecision.dec_list_for_story_loc(story_id, location_id)
    return render_template("verification/location.html", location=location, story_id=story_id, location_id=location_id, decisions=decisions)


@app.route("/verification/event")
def verfication_event():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    event_id = request.args["event_id"]
    event = StoryEvent.get(story_id, event_id)
    return render_template("verification/event.html", event=event, story_id=story_id, event_id=event_id)


@app.route("/verification/story")
def verfication_story():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    locations = StoryLocation.loc_list(story_id)
    decisions = StoryDecision.dec_list_story(story_id)
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    return render_template("verification/story.html", events=events, story_id=story_id, locations=locations, decisions=decisions, objects=objects)


@app.route("/story/treeview")
def treeview():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    story = Story.get(story_id)
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
def verify_treeview():
    # if "logged_in" not in session:
    #     return redirect(url_for("session_new"))
    story_id = request.args['story_id']
    story = Story.get(story_id)
    locations = StoryLocation.loc_list(story_id)
    loc_id = request.args.get('location_id')
    decisions = []
    if loc_id is not None:
        decisions = StoryDecision.dec_list_for_story_loc(story_id, loc_id)

    location = StoryLocation.get(story_id, loc_id)
    return render_template("verification/treeview.html", StoryLocation=StoryLocation, loc_id=loc_id, locations=locations, location=location, decisions=decisions, story=story)


# @app.route("/verification/treeview/update", methods=['POST'])
# def verify_treeview_update():
#     details = request.form
#     story_id = details.get('story_id')
#     ent_type = details['type']
#     ent_id = details['ent_id']
#     reviewer_comment = details['comment']
#     is_verified = details.get("is_verified")
#     if is_verified is None:
#         is_verified = False
#     else:
#         is_verified = True
#     if ent_type.lower() == 'location':
#         loc = StoryLocation.get(story_id, ent_id)
#         loc.update_admin(is_verified, reviewer_comment)
#     else:
#         loc_id = details['loc_id']
#         dec = StoryDecision.get(story_id, loc_id, ent_id)
#         dec.update_admin(is_verified, reviewer_comment)
#     return '{"status":"ok"}'


@app.route("/story/run")
def story_run():
    if "logged_in" not in session:
        return redirect(url_for("session_new"))
    story_id = request.args["story_id"]
    story = Story.get(story_id)
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
        for decision in obj['decs']:
            triggered.append(StoryDecision.get(story_id, 0, decision))
        for back in obj['back']:
            backs.append(StoryLocation.get(story_id, back))

    return render_template("story/run.html", inv=inv, evts=evts, triggered=triggered, backs=backs, objects=objects, decisions=decisions, StoryEvent=StoryEvent, StoryLocation=StoryLocation, StoryObject=StoryObject, story=story, location=location)


@app.route("/story/help")
def help():
    return render_template("story/help.html")


@app.route("/verification/help")
def vhelp():
    return render_template("verification/help.html")


@app.route("/story/treeview_help")
def treeview_help():
    story_id = request.args['story_id']
    story = Story.get(story_id)
    return render_template("story/treeview_help.html", story=story)


@app.route("/admin")
def admin_index():
    uid = session['user_id']
    acct = User.get(uid)
    if not acct.is_admin:
        abort(403)
    stories = Story.get_story_count()
    users = User.get_user_count()
    return render_template("admin/index.html", stories=stories, users=users)


@app.route("/admin/users", methods=["GET", "POST"])
def admin_users():
    uid = session['user_id']
    acct = User.get(uid)
    if not acct.is_admin:
        abort(403)
    if request.method == "GET":
        users = User.list_of_all_users()
        return render_template("admin/users.html", users=users)
    else:
        user = User()
        user.user_id = request.form.get("user_id")
        user.username = request.form.get("username")
        user.is_admin = True
        user.is_content_editor = True
        user.is_copy_editor = True
        print(request.form.get("is_admin"))
        if request.form.get("is_admin") is None:
            user.is_admin = False
        if request.form.get("is_content_editor") is None:
            user.is_content_editor = False
        if request.form.get("is_copy_editor") is None:
            user.is_copy_editor = False
        print(user.username)
        print(user.user_id)
        user.update_admin()
        return '{"status":"ok"}'


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found_500(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("session_new"))


if __name__ == '__main__':
    app.run()
