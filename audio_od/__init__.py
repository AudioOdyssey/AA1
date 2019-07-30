import os

from flask import Flask

app = Flask(__name__)

import config

app.config['SECRET_KEY'] = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['UPLOAD_FOLDER']=config.upload_folder
app.config['MAIL_SERVER'] = config.mail_server
app.config['MAIL_PORT'] = config.mail_port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.mail_name
app.config['MAIL_PASSWORD'] = config.mail_pass
mail = Mail(app)

app.config['GOOGLE_CLIENT_ID']=config.google_client_id
app.config['GOOGLE_CLIENT_SECRET']=config.google_client_secret

app.config['FACEBOOK_CLIENT_ID'] = config.facebook_client_id
app.config['FACEBOOK_CLIENT_SECRET'] = config.facebook_client_secret

from audio_od import home

from audio_od.Auth.routes import auth as auth_bp
from audio_od.Home.routes import home as home_bp
from audio_od.Verification.routes import verif_bp

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(verif_bp)


