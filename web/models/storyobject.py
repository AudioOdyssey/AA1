class StoryObject:
    def __init__(self, story_id, obj_id, obj_name, obj_description, can_pickup_obj, obj_starting_loc, is_hidden, unhide_event_id):
        self.story_id = story_id
        self.obj_id = obj_id
        self.obj_name = obj_name
        self.obj_description = obj_description
        self.can_pickup_obj = can_pickup_obj
        self.obj_starting_loc = obj_starting_loc
        self.is_hidden = is_hidden
        self.unhide_event_id = unhide_event_id