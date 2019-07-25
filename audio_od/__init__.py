import os

from flask import Flask

app = Flask(__name__)

from audio_od import auth, main, config, home, userprofile

app.config['SECRET_KEY'] = config.secret_key