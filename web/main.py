from models.storyobject import StoryObject
from models.User import User
#from models.story import Story
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
    return render_template("story/show.html")

@app.route("/story/object/show")
def event_show():
    objects = [StoryObject(15, 1, "Adam's Water Bottle", "Constantly Empty", True, 7, False, 0),
                StoryObject(15, 5, "Different Obj", "Constantly Empty", False, 7, False, 0)]
    return render_template("story/object/show.html", objects=objects, story_id=1)

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
