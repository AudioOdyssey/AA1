from models.storyobject import StoryObject
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    return render_template("index.html")

@app.route("/user/new")
def user_new():
    return render_template("user/new.html")

@app.route("/session/new")
def session_new():
    return render_template("session/new.html")

@app.route("/story/object/show")
def event_show():
    objects = [StoryObject(15, 1, "Adam's Water Bottle", "Constantly Empty", True, 7, False, 0),
                StoryObject(15, 5, "Different Obj", "Constantly Empty", False, 7, False, 0)]
    return render_template("story/object/show.html", objects=objects)