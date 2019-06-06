from flask_restful import Resource
from flask_jwt import jwt_required
from flask.views import MethodView
from models.storyobject import StoryObjectModel

class StoryObjectResource(MethodView):
    
    @jwt_required
    def get(self, story_id, obj_id):
        obj = StoryObjectModel()
        obj_result = obj.get(story_id, obj_id)
        if obj_result:
            return obj_result.show_info(), 201
        return {"message" : "Story object does not exist"}, 400