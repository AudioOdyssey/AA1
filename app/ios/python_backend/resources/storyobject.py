from flask_restful import Resource
from flask_jwt import jwt_required
from models.storyobject import StoryObjectModel

class StoryObjectResource:
    
    @jwt_required
    def post(self, story_id, obj_id):
        obj = StoryObjectModel()
        obj_result = obj.get(story_id, obj_id)
        if obj_result:
            return obj_result.show_info()
        return {"message" : "Story object does not exist"}, 400