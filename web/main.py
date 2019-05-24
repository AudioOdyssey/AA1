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