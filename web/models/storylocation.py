class StoryLocation:
    def __init__(self, story_id, location_id, location_name, origin_description, short_description, post_event_description, location_event_id, auto_goto, next_loc_id, location_verified, location_verif_status, location_timestamp, verification_userid): 
        self.story_id = story_id
        self.location_id = location_id
        self.location_name = location_name
        self.origin_description = origin_description
        self.short_description = short_description
        self.post_event_description = post_event_description
        self.location_event_id = location_event_id
        self.auto_goto = auto_goto
        self.next_loc_id = next_loc_id
        self.location_verified = location_verified
        self.location_verif_status =location_verif_status
        self.location_timestamp = location_timestamp
        self.verification_userid = verification_userid
