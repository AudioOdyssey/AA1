from models.storyobject import StoryObject

from flask import Flask, render_template, request

#from flask_login import LoginManager

import pymysql
import sys

import random
import hashlib
import binascii

from datetime import datetime

app = Flask(__name__)

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
        conn = pymysql.connect(rds_host, user=name, passwd = rds_password, db= db_name, connect_timeout=5)
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
        password_salt = generate_password_salt()
        encrypted_password = encrypt_password(raw_password, password_salt)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users(username, password, password_salt, email_address, profession, gender, country_of_origin, disabilities, language_id, first_name, last_name, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(username, encrypted_password, password_salt, email, profession, gender, country_of_origin, disabilities_bool, language, first_name, last_name, date_of_birth))
            conn.commit()
            cur.close()
    return render_template("user/new.html")

@app.route("/session/new", methods =['GET', 'POST'])
def session_new():
    #login_manager = LoginManager()
    #login_manager.init_app(app)
    return render_template("session/new.html")

@app.route("/story/object/show")
def event_show():
    objects = [StoryObject(15, 1, "Adam's Water Bottle", "Constantly Empty", True, 7, False, 0),
                StoryObject(15, 5, "Different Obj", "Constantly Empty", False, 7, False, 0)]
    return render_template("story/object/show.html", objects=objects, story_id=1)

#Generates a salt for storing passwords
def generate_password_salt():
    salt_source = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz123456789' 
    salt = random.choice(salt_source)
    for i in range(15):
        salt += random.choice(salt_source)
    return salt

def encrypt_password(raw_password, password_salt):
    password = raw_password + password_salt 
    encrypted_password = hashlib.sha256(password.encode()).digest()
    password_hex_string = binascii.b2a_hex(encrypted_password)
    return password_hex_string