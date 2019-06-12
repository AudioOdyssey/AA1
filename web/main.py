from models.storyobject import StoryObject
from models.User import User
from models.story import Story
from models.storyevent import StoryEvent
from models.storylocation import StoryLocation
from models.storydecision import StoryDecision
from flask import Flask, redirect, render_template, request, session, url_for, make_response, jsonify

from flask_login import LoginManager

import pymysql
import pymysql.cursors
import sys

import random
import hashlib
import binascii

import json

from datetime import datetime

app = Flask(__name__)
app.secret_key = b"jk_\xf7\xa7':\xea$/\x88\xc0\xa3\x0e:d"

login_manager = LoginManager()
login_manager.init_app(app)

REGION = 'us-east-2b'

rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
name = "AA_admin"
rds_password = "z9QC3pvQ"
db_name = "audio_adventures_dev"

story_id = 1

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

@app.route("/app/user/new", methods=['POST'])
def app_user_new():
    details = request.get_json(force=True)
    user_id = sign_up(details)
    if user_id:
        result = {}
        result['user_id']=user_id
        return make_response(json.dumps(result),201)
    else:
        result = {}
        result['message']='Username already exists'
        return make_response(json.dumps(result),409)

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
    date_of_birth = datetime.strptime(details_dict['date_of_birth'], '%Y-%m-%d')
    usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin, 
            profession_input=profession, disabilities_input=disabilities_bool, 
            first_name_input=first_name, last_name_input=last_name, language=language, date_of_birth_input=date_of_birth)
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
            usr = load_user(str(result['user_id']).encode('utf-8').decode('utf-8'))
            if(usr.authenticate(details['password'])):
                session['username'] = username
                return True
            else:
                return False
    return True

@app.route("/app/session/new", methods =['POST'])
def app_session_new():
    details = request.json
    details_dict = json.loads(details)
    if authenticate(details_dict):
        return {'message': 'log-in is successful'},201
    return {'message': 'username/password not successful'},400


@app.route("/story/show")
def story_show():
    stories = [Story(5, "Story Title", "Brian", "Short Synopsis", 50, True, "Fiction", 3, 30, 50, False, None, None, "not verified", 0.0, 1, 16.3, False, False)]
    return render_template("story/show.html", stories=stories)

@app.route("/story/update")
def story_update():
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

@app.route("/story/object/show")
def object_show():
    objects = StoryObject.obj_list(story_id)
    return render_template("story/object/show.html", objects=objects, story_id=1)

@app.route("/app/story/object/show", methods = ["GET"])
def app_object_show():
    objects = StoryObject.obj_list_json(story_id)
    return make_response(objects, 200)

@app.route("/story/object/update", methods = ['POST'])
def object_update():
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
def object_new():
    details = request.form
    story_id = details['story_id']
    obj = StoryObject(story_id)
    obj.add_to_server()
    return redirect(url_for("object_show"))

@app.route("/story/event/show", methods = ['GET'])
def event_show():
    events= StoryEvent.event_list(story_id)
    return render_template("story/event/show.html", events=events, story_id=story_id)

@app.route('/story/event/update', methods = ['POST'])
def event_update():
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
def event_new():
    details = request.form
    story_id = details['story_id']
    evnt = StoryEvent(story_id)
    evnt.add_to_server()
    return redirect(url_for('event_show'))

@app.route("/story/location/show")
def location_show():
    locations= StoryLocation.loc_list(story_id)
    return render_template("story/location/show.html", locations=locations, story_id=story_id)

@app.route("/story/location/decision/show")
def decision_show():
    decisions = [StoryDecision()]
    return render_template("story/location/decision/show.html", decisions=decisions, story_id=story_id, location_id=1)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@login_manager.user_loader
def load_user(user_id):
    usr = User()
    return usr.get(user_id)

@app.route("/verification/view")
def verification_view():
    stories = [Story(5, "Story Title", "Brian", "Short Synopsis", 50, True, "Fiction", 3, 30, 50, False, None, None, "not verified", 0.0, 1, 16.3, False, False)]
    return render_template("verification/view.html" , stories=stories)

if __name__=='__main__':
	app.run()