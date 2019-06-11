import pymysql
import pymysql.cursors
import sys

import json

class Story:
    story_id = 0
    story_title = ''
    story_author = ''
    story_synopsis = ''
    story_price = 0
    author_paid = False
    length_of_story = 0
    number_of_locations = 0
    number_of_decisions = 0
    story_verified = False
    story_verification_date = None
    name_of_verifier = ''
    story_ratings = 0
    story_language_id = 0
    storage_size = 0
    obj_verification_status = ''
    event_verification_status = ''
    genre =  ''

    def __init__(self, story_id= 0, story_title = '', story_author= '', story_synopsis = '', story_price = 0, 
                author_paid = False, genre = '', length_of_story = 0, number_of_locations = 0, number_of_decisions = 0, 
                story_verified = False, story_verification_date = '', name_of_verifier = '', verification_status = '', 
                story_ratings = 0, story_language_id = 1, storage_size = 0, obj_verification_status = '', event_verification_status = ''):
        if story_id > 0:
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