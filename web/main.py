from models.storyobject import StoryObject
from models.User import User
from models.story import Story
from models.storyevent import StoryEvent
from models.storylocation import StoryLocation
from models.storydecision import StoryDecision
from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify

from flask_login import LoginManager, login_required, login_user, logout_user, current_user, login_url

import pymysql
import pymysql.cursors
import sys

import random
import hashlib
import binascii

import json

from datetime import datetime, timedelta

import jwt

app = Flask(__name__)
secret_key = b"jk_\xf7\xa7':\xea$/\x88\xc0\xa3\x0e:d"

login_manager = LoginManager()
login_manager.init_app(app)
#login_manager.login_view = "session/new.html"
#login_manager.login_message = "Please login"

session = {}

REGION = 'us-east-2b'

rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
name = "AA_admin"
rds_password = "z9QC3pvQ"
db_name = "audio_adventures_dev"

story_id = 1
location_id = 1

random.seed()

@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    return render_template("index.html")

@app.route("/user/new", methods=['GET', 'POST'])
def user_new(): #fix later
    if request.method == "POST":
        details = request.form 
        username = details['username']
        raw_password = details['password']
        email = details['email_address']
        gender = int(details['gender'])
        country_of_origin = int(details['country_of_origin'])
        profession = details['profession']
        disabilities = details.get('disabilities')
        if disabilities is None:
            disabilities_bool = 0
        else:
            disabilities_bool = 1
        language = int(details['language-id'])
        first_name = details['first_name']
        last_name = details['last_name']
        date_of_birth = datetime.strptime(details['date_of_birth'], '%Y-%m-%d')
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
            result['user_id']= str(user_id)
            result['message'] = "Successfully registered"
        else:
            result['message']='Username already exists'
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
        disabilities_bool =0
    language = int(details_dict['language_id'])
    first_name = details_dict['first_name']
    last_name = details_dict['last_name']
    #date_of_birth = datetime.strptime(details_dict['date_of_birth'], '%Y-%m-%d')
    usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin, 
            profession_input=profession, disabilities_input=disabilities_bool, 
            first_name_input=first_name, last_name_input=last_name, language=language)
    if usr.add_to_server():
        return usr.get_id()
    else:
        return None        

@app.route("/session/new", methods =['GET', 'POST'])
def session_new():
    error = None
    if request.method == 'POST':
        details = request.form
        if authenticate(details):
            session['platform'] = 'web'
            return redirect(url_for("story_show"))
        else:
            error = "Username and/or password not valid"
    return render_template("session/new.html", error=error)

def authenticate(details):
    conn = pymysql.connect(rds_host, user=name, passwd = rds_password, db= db_name, connect_timeout=5, 
                            cursorclass = pymysql.cursors.DictCursor)
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

@app.route("/app/session/new", methods =['POST', 'GET'])
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
            'user_id' : str(session['user_id']),
            'auth_token' : encode_auth_token(str(session['user_id']))
        }
    else:
        result = {
            'message' : message
        }
    return jsonify(result)

def encode_auth_token(user_id):
    payload = {
        'exp' : datetime.utcnow() + timedelta(days = 7, seconds = 5),
        'iat' : datetime.utcnow(),
        'sub' : user_id
    }
    return jwt.encode(
        payload,
        secret_key,
        algorithm='HS256'
    )

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, secret_key)
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

@app.route("/session/logout")
#@login_required
def logout():
    if "logged_in" in session:
        session.pop("logged_in", None)
        usr = User.get(session.get('user_id'))
        usr.is_authenticated = False
        return redirect(url_for("home"))
    else:
        return redirect(url_for("session_new"))

@app.route("/story/show")
#@login_required
def story_show():
   # if "logged in" not in session:
    #    return redirect(url_for("session_new"))
    stories = [Story(5, "Story Title", "Brian", "Short Synopsis", 50, True, "Fiction", 3, 30, 50, False, None, None, "not verified", 0.0, 1, 16.3, False, False)]
    return render_template("story/show.html", stories=stories)

@app.route("/story/update")
#@login_required
def story_update():
  #  if "logged in" not in session:
   #     return redirect(url_for("session_new"))
    objects = StoryObject.obj_list(story_id)
    events = StoryEvent.event_list(story_id)
    locations= StoryLocation.loc_list(story_id)
    return render_template("story/update.html", objects=objects, events=events, locations=locations)

# @app.route("/story/new", methods = ['POST'])
# def story_new():
#     details = request.form
#     creator_id = details['user_creator_id']
#     new_story = Story(user_creator_id = creator_id)
#     new_story.add_to_server()
#     return redirect(url_for("story_update"))



#### THIS WORKS #####
@app.route("/story/object/show")
#@login_required
def object_show():
   # if "logged in" not in session:
    #    return redirect(url_for("session_new"))
    objects = StoryObject.obj_list(story_id)
    return render_template("story/object/show.html", objects=objects, story_id=1)

@app.route("/app/story/info", methods = ['GET'])
def app_story_logistics():
    details = request.json
    in_story_id = details.get("story_id")
    return Story.get_entities(in_story_id)

@app.route("/store/story/info", methods = ['GET'])
def app_store_expand():
    in_story_id = 0
    details = request.json
    in_story_id = details.get("story_id")
    return Story.get_info(in_story_id)

@app.route("/story/object/update", methods = ['POST'])
#@login_required
def object_update():
    #if "logged in" not in session:
     #   return redirect(url_for("session_new"))
    details = request.form
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
    #unhide_event_id = details['unhide_event_id']
    obj = StoryObject.get(story_id, object_id)
    obj.update(story_id, object_id, name=name, starting_loc=starting_loc, desc=desc, can_pickup_obj=can_pickup_obj, is_hidden=is_hidden)
    return redirect(url_for("object_show"))

@app.route("/story/object/new", methods = ['POST'])
#@login_required
def object_new():
 #   if "logged in" not in session:
  #      return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
    obj = StoryObject(story_id)
    obj.add_to_server()
    return redirect(url_for("object_show"))



#### STILL NEEDS WORK ####
@app.route("/story/event/show", methods = ['GET'])
#@login_required
def event_show():
  #  if "logged in" not in session:
   #     return redirect(url_for("session_new"))
    events= StoryEvent.event_list(story_id)
    return render_template("story/event/show.html", events=events, story_id=story_id)

@app.route('/story/event/update', methods = ['POST'])
#@login_required
def event_update():
    #if "logged in" not in session:
     #   return redirect(url_for("session_new"))
    if request.method == 'POST':
        details = request.form
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
    return redirect(url_for('event_show'))

@app.route('/story/event/new', methods = ['POST'])
#@login_required
def event_new():
    #if "logged in" not in session:
     #   return redirect(url_for("session_new"))
    details = request.form
    story_id = details['story_id']
    evnt = StoryEvent(story_id)
    evnt.add_to_server()
    events = StoryEvent.event_list(story_id)
    return render_template("story/event/show.html", events = events, story_id = story_id)



### LOCATION STILL NEEDS WORK ###
@app.route("/story/location/show")
#@login_required
def location_show():
    #if "logged in" not in session:
     #   return redirect(url_for("session_new"))
    locations= StoryLocation.loc_list(story_id)
    return render_template("story/location/show.html", locations=locations, story_id=story_id)

@app.route('/story/location/update', methods = ['POST'])
#@login_required
def location_update():
  #  if "logged in" not in session:
   #     return redirect(url_for("session_new"))
    details = request.form
    in_story_id = details['story_id']
    if story_id is None:
        in_story_id = story_id
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
    next_location_id = details.get('next_loc_id')
    if next_location_id is None:
        next_location_id = 0
    loc = StoryLocation.get(in_story_id, loc_id) #issue these arent set right 
    loc.update(in_story_id, loc_id, name, original_desc, short_desc, post_event_description, event_id, auto_goto, next_location_id)
    return redirect(url_for("location_show"))

@app.route('/story/location/new', methods = ['POST'])
#@login_required
def location_new():
   # if "logged in" not in session:
    #    return redirect(url_for("session_new"))
    details = request.form
    in_story_id = details['story_id']
    loc = StoryLocation(in_story_id)
    loc.add_to_server()
    return redirect(url_for("location_show"))



#### DECISIONS WORK ####
@app.route("/story/location/decision/show")
def decision_show():
    #if "logged in" not in session:
     #   return redirect(url_for("session_new"))
    decisions = StoryDecision.dec_list(story_id)
    return render_template("story/location/decision/show.html", decisions=decisions, story_id=story_id, location_id=1)

@app.route("/story/location/decision/update", methods = ['POST'])
def decision_update():
    #if "logged in" not in session:
     #   return redirect(url_for("session_new"))
    details = request.form
    decision_id = details['decision_id']
    if decision_id == '':
        decision_id = StoryDecision.get_last_id(story_id)
    decision_name = details['decision-name']
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
    unlock_obj_id = details.get("unlock_obj_id")
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
    dec.update(story_id, decision_id, location_id, sequence, decision_name, transition, transition_loc_id, is_hidden, is_locked, dec_description, show_event_id, show_object_id, unlock_event_id, unlock_obj_id, locked_descr, aftermath_desc, cause_event, effect_event_id, can_occur_once, is_locked_by_event_id, locked_by_event_desc)
    return redirect(url_for("decision_show"))

@app.route("/story/location/decision/new", methods = ['POST'])
def decision_new():
    if "logged in" not in session:
        return redirect(url_for("session_new"))
    details = request.form
    location_id = details.get('loc_id')
    dec = StoryDecision(story_id, location_id)
    dec.add_to_server()
    return redirect(url_for("decision_show"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/verification/view")
def verification_view():
    stories = [Story(5, "Story Title", "Brian", "Short Synopsis", 50, True, "Fiction", 3, 30, 50, False, None, None, "not verified", 0.0, 1, 16.3, False, False)]
    return render_template("verification/view.html" , stories=stories)

@app.route("/verification/review")
def verification_review():
    #uncomment when all this stuff works
    #objects = StoryObject.obj_list(story_id)
    #events = StoryEvent.event_list(story_id)
    #locations= StoryLocation.loc_list(story_id)
    #decisions = [StoryDecision()]
    #return render_template("verification/review.html", objects=objects, events=events, locations=locations, decisions=decisions)
    return render_template("verification/review.html")


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/story/help")
def help():
    return render_template("story/help.html")

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("session_new"))
    
@app.route("/user/newcorp")
def newcorp():
    return render_template("user/newcorp.html")

@app.route("/story/treeview")
def treeview():
    return render_template("story/treeview.html")




if __name__=='__main__':
	app.run()


