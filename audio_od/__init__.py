import os

from flask import Flask

app = Flask(__name__)

from audio_od import auth, main, config, home, userprofile

app.config['SECRET_KEY'] = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['UPLOAD_FOLDER']=config.upload_folder