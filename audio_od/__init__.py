import os

from flask import Flask

import config

app = Flask(__name__)

app.config['SECRET_KEY'] = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

app.config['UPLOAD_FOLDER']=config.upload_folder
app.config['MAIL_SERVER'] = config.mail_server
app.config['MAIL_PORT'] = config.mail_port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.mail_name
app.config['MAIL_PASSWORD'] = config.mail_pass

app.config['DB_HOST'] = config.db_host
app.config['USER'] = config.db_user
app.config['DB_PASSWORD']= config.db_password
app.config['DB_NAME'] = config.db_name

app.config['GOOGLE_CLIENT_ID']=config.google_client_id
app.config['GOOGLE_CLIENT_SECRET']=config.google_client_secret

app.config['FACEBOOK_CLIENT_ID'] = config.facebook_client_id
app.config['FACEBOOK_CLIENT_SECRET'] = config.facebook_client_secret

from audio_od.Auth.routes import auth as auth_bp
from audio_od.Home.routes import home as home_bp
from audio_od.Verification.routes import verification as verif_bp
from audio_od.Users.routes import userprofile as user_bp

from audio_od.StoryView.decisionroutes import dec_view as dec_bp
from audio_od.StoryView.eventroutes import ev_view as ev_bp
from audio_od.StoryView.locationroutes import loc_view as loc_bp
from audio_od.StoryView.storyobjectroutes import obj_view as obj_bp
from audio_od.StoryView.storyroutes import story_view as story_bp
from audio_od.Dashboard.routes import dash_view as dash_db

from audio_od.Help.routes import helper as help_bp

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(verif_bp)
app.register_blueprint(user_bp)
app.register_blueprint(dec_bp)
app.register_blueprint(ev_bp)
app.register_blueprint(loc_bp)
app.register_blueprint(obj_bp)
app.register_blueprint(story_bp)
app.register_blueprint(dash_db)
app.register_blueprint(help_bp)


from audio_od import utils