import os

from flask import Flask

app = Flask(__name__)


from audio_od import config, auth, home, userprofile, verification, storyinfo, locationinfo, storyobjectinfo, eventinfo, decisioninfo

app.config['SECRET_KEY'] = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['UPLOAD_FOLDER']=config.upload_folder

import config
app.config['SECRET_KEY'] = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['UPLOAD_FOLDER']=config.upload_folder

from audio_od import home

from audio_od.Auth import bp as auth_bp
app.register_blueprint(auth_bp)

