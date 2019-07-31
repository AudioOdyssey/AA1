# Python standard libraries
import os

# Third-party libraries
from flask import redirect, render_template, request, url_for, session, Blueprint

# Internal imports
from audio_od import app
from audio_od.utils import authentication_required, check_header, decode_auth_token

