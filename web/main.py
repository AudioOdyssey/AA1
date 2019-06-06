from models.storyobject import StoryObject
from models.User import User
from models.story import Story
from models.storyevent import StoryEvent
from models.storylocation import StoryLocation
from flask import Flask, redirect, render_template, request, session, url_for

from flask_login import LoginManager

import pymysql
import pymysql.cursors
import sys

import random
import hashlib
import binascii

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

random.seed()

@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    return render_template("index.html")

@app.route("/user/new", methods=['GET', 'POST'])
def user_new():
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
        #flash("Successful login!")
    return render_template("user/new.html")

@app.route("/session/new", methods =['GET', 'POST'])
def session_new():
    error = None
    if request.method == 'POST':
        conn = pymysql.connect(rds_host, user=name, passwd = rds_password, db= db_name, connect_timeout=5, 
                                cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            details = request.form
            username = details['username']
            cur.execute(("SELECT * FROM users WHERE username = %s"), username)
            result = cur.fetchone()
            if(result is None):
                error = "Username and/or password not valid"
            else:
                usr = load_user(str(result['user_id']).encode('utf-8').decode('utf-8'))
                is_authenticated = usr.authenticate(details['password'])
                if(is_authenticated):
                    session['username'] = username
                    return redirect(url_for("story_show"))
                else:
                    error = "Username and/or password not valid"
    return render_template("session/new.html", error=error)

@app.route("/story/show")
def story_show():
    stories = [Story(5, "Story Title", "Brian", "Short Synopsis", 50, True, "Fiction", 3, 30, 50, False, None, None, "not verified", 0.0, 1, 16.3, False, False)]
    return render_template("story/show.html", stories=stories)

@app.route("/story/update")
def story_update():
    objects = [StoryObject(15,"Adam's Water Bottle", "Constantly Empty", True, 7, False, 0),
                StoryObject(15,"Different Obj", "Constantly Empty", False, 7, False, 0)]
    events = [StoryEvent(1, 1, "FieldDay", "KidsGoOutside", 1, False)]
    return render_template("story/update.html", objects=objects, events=events)

@app.route("/story/object/show")
def object_show():
    objects = StoryObject.obj_list
    return render_template("story/object/show.html", objects=objects, story_id=1)

@app.route("/story/object/update", methods = ['POST'])
def object_update(story_id, object_id):
    details = request.form
    name = details['obj_name']
    desc = details['obj_description']
    starting_loc = details['obj_starting_loc']
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
    unhide_event_id = details['unhide_event_id']
    obj = StoryObject()
    obj_result = obj.get(story_id, object_id)
    obj_result.update(story_id, object_id, name, starting_loc, desc, can_pickup_obj, is_hidden, unhide_event_id)
    
@app.route("/story/object/new", methods = ['POST'])
def object_new():
    details = request.form
    name = details['obj_name']
    starting_loc = details['obj_starting_loc']
    desc = details['obj_description']
    story_id = details['story_id']
    obj = StoryObject(story_id, name, desc, obj_starting_loc = starting_loc)
    obj.add_to_server()



@app.route("/story/event/show")
def event_show():
    events= [StoryEvent(1, 1, "Field Day", "Kids Go Outside", 1, False)]
    return render_template("story/event/show.html", events=events, story_id=1)

@app.route("/story/location/show")
def location_show():
    locations= [StoryLocation(1, 1, "zoe's house", "its in solon", "solon", "its gone", 1, False, 1, True,0, 8, 1)]
    return render_template("story/location/show.html", locations=locations, story_id=1)

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
