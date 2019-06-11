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
    user_creator_id = 0

    def __init__(self, story_id= 0, story_title = '', story_author= '', story_synopsis = '', story_price = 0, 
                author_paid = False, genre = '', length_of_story = 0, number_of_locations = 0, number_of_decisions = 0, 
                story_verified = False, story_verification_date = '', name_of_verifier = '', verification_status = '', 
                story_ratings = 0, story_language_id = 1, storage_size = 0, obj_verification_status = '', event_verification_status = '', user_creator_id = 0):
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
        self.user_creator_id = user_creator_id

    def add_to_server(self):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("INSERT INTO master_stories(story_title, story_author, story_synopsis, story_price, author_paid, genre, length_of_story, number_of_locations, number_of_decisions, story_verified, story_verification_date, story_ratings, story_language_id, storage_size, obj_verification_status, event_verification_status, user_creator_id VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"), 
                        (self.story_title, self.story_author, self.story_synopsis, self.story_price, self.author_paid, self.genre, self.length_of_story, self.number_of_locations, self.number_of_decisions, self.story_verified, self.story_verification_date, self.story_ratings, self.story_language_id, self.storage_size, self.obj_verification_status, self.event_verification_status, self.user_creator_id))
            conn.commit()
        conn.close()

    def update(self, story_title, story_author, story_price, story_language_id, length_of_story, genre):
        self.story_title = story_title
        self.story_author = story_author
        self.story_price = story_price
        self.story_language_id = story_language_id
        self.length_of_story = length_of_story
        self.genre = genre
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE master_stories SET story_title = %s, story_author = %s, story_price = %s, story_language_id = %s, genre = %s WHERE story_id = %s"), 
                        (self.story_title, self.story_author, self.story_price, self.story_language_id, self.genre, self.story_id))
            conn.commit()
        conn.close()

    def update_admin(self, story_ratings, story_verified, story_verification_date, obj_verification_status, event_verification_status, storage_size):
        pass