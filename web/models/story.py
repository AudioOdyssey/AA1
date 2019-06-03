class Story:
    def __init__(self, story_id, story_title, story_author, story_synopsis, story_price, 
                author_paid, genre, length_of_story, number_of_locations, number_of_decisions, 
                story_verified, story_verification_date, name_of_verifier, verification_status, 
                story_ratings, story_language_id, storage_size, obj_verification_status, event_verification_status):
        self.story_id = story_id
        self.story_title = story_title
        self.story_author = story_author
        self.story_synopsis = story_synopsis
        self.story_price = story_price
        self.author_paid = author_paid
        self.genre = genre
        self.length_of_story = length_of_story
        self.number_of_locations = number_of_locations
        self.number_of_decisions = number_of_decisions
        self.story_verified = story_verified
        self.story_verification_date = story_verification_date
        self.name_of_verifier = name_of_verifier
        self.story_ratings = story_ratings
        self.story_language_id = story_language_id
        self.storage_size = storage_size
        self.obj_verification_status = obj_verification_status
        self.event_verification_status = event_verification_status