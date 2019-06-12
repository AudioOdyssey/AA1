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
    story_in_store = False
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
                author_paid = False, genre = '', length_of_story = 0, number_of_locations = 0, number_of_decisions = 0, story_in_store = False,
                story_verification_date = '', name_of_verifier = '', verification_status = '', 
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
        self.story_in_store = story_in_store
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
            cur.execute(("INSERT INTO master_stories(story_title, story_author, story_synopsis, story_price, author_paid, genre, length_of_story, number_of_locations, number_of_decisions, story_in_store, story_verified, story_verification_date, story_ratings, story_language_id, storage_size, obj_verification_status, event_verification_status, user_creator_id VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"), 
                        (self.story_title, self.story_author, self.story_synopsis, self.story_price, self.author_paid, self.genre, self.length_of_story, self.number_of_locations, self.number_of_decisions, self.story_in_store, self.story_verification_date, self.story_ratings, self.story_language_id, self.storage_size, self.obj_verification_status, self.event_verification_status, self.user_creator_id))
            conn.commit()
            cur.execute(("SELECT count(*) FROM master_stories WHERE `user_creator_id` = %s"), (self.user_creator_id))
            result = cur.fetchone()
            self.story_id = result['count(*)']
        conn.close()
    
    def get_id(self):
        id = (self.story_id)
        return id
    
    @classmethod
    def get(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `master_stories` WHERE story_id = %s"), (story_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return cls(story_id, results["story_title"], results["story_author"], results["story_synopsis"], results["story_price"], results["author_paid"], results["length_of_story"], results["number_of_locations"], results["number_of_decisions"], results["story_in_store"], results["story_verified"], results["story_verification_date"], results["name_of_verifier]"], results["story_ratings"], results["story_language_id"], results["storage_size"], results["obj_verification_status"], results["event_verification_status"], results["genre"], results["user_creator_id"])
    

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

    def update_admin(self, story_ratings, story_verification_date, obj_verification_status, event_verification_status, storage_size):
        self.story_ratings = story_ratings
        self.story_verification_date = story_verification_date
        self.obj_verification_status = obj_verification_status
        self.event_verification_status = event_verification_status
        self.storage_size = storage_size
        
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"

        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE master_stories SET story_ratings = %s, story_verification_date = %s, obj_verification_status = %s, event_verification_status = %s, storage_size = %s WHERE story_id = %s")
                        ,(self.story_ratings, self.story_verification_date, self.obj_verification_status, self.event_verification_status, self.storage_size, self.story_id))
            conn.commit()
        conn.close()

    @classmethod
    def story_list(cls, user_creator_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `master_stories` WHERE user_creator_id = %s"), (user_creator_id))
            results = cur.fetchall()
            for row in results:
                story_list.append(cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19]))
        conn.close()
        return story_list
 
    @classmethod
    def obj_list_json(cls, user_creator_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        result = []
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `master_stories` WHERE user_creator_id = %s"), (user_creator_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                story_dict = {'story_id' : row[0], 'story_title' : row[1], 'story_author' : row[2], 'story_synopsis' : row[3],'story_price' : row[4], 
                'author_paid' : row[5], 'genre' : row[6], 'length_of_story' : row[7], 'number_of_locations' : row[8], 
                'number_of_decisions' : row[9], 'story_in_store' : row[10], 'story_verification_date' : row[11], 'name_of_verifier' : row[12], 
                'verification_status' :  row[13], 'story_ratings' : row[14], 'story_language_id' : row[15], 'storage_size' : row[16], 
                'obj_verification_status' : row[17], 'event_verification_status' : row[18], 'user_creator_id' : row[19]}
                result.append(story_dict)
        conn.close()
        return json.dumps(result)

    @classmethod
    def get_last_story_id(cls, user_creator_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        last_id = 0
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        with conn.cursor() as cur:
            cur.execute(("SELECT count(*) FROM master_stories WHERE user_creator_id = %s"), (user_creator_id))
            result = cur.fetchone()
            last_id = result[0]
        conn.close()
        return last_id