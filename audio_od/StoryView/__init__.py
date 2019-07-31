from flask import Blueprint

from audio_od import app

sv = Blueprint('StoryView', __name__)

from StoryView import decisionroutes, eventroutes, locationroutes, storyobjectroutes, storyroutes