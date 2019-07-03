import pymysql
import pymysql.cursors
import sys

import json

from datetime import datetime

from .storydecision import StoryDecision


class StoryLocation:
    story_id = 0
    location_id = 0
    location_name = ""
    original_description = ""
    short_description = ""
    post_event_description = ""
    location_event_id = 0
    auto_goto = 0
    next_loc_id = 0
    reviewer_comments = ''
    is_verified = False

    rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
    name = "AA_admin"
    rds_password = "z9QC3pvQ"
    db_name = "audio_adventures_dev"

    def __init__(self, story_id=0, location_id=0, location_name='', original_description='', short_description='', post_event_description='', location_event_id=0, auto_goto=False, next_loc_id=0, reviewer_comments = '', is_verified = False):
        self.story_id = story_id
        self.location_id = location_id
        self.location_name = location_name
        self.original_description = original_description
        self.short_description = short_description
        self.post_event_description = post_event_description
        self.location_event_id = location_event_id
        self.auto_goto = auto_goto
        self.next_loc_id = next_loc_id
        self.reviewer_comments = reviewer_comments
        self.is_verified = is_verified

    def add_to_server(self):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            self.location_id = self.get_last_id(self.story_id)
            print(self.location_id)
            cur.execute(("INSERT INTO locations(story_id, location_id) VALUES (%s, %s)"),
                        (self.story_id, self.location_id))
            conn.commit()
        conn.close()

    def get_id(self):
        id = (self.story_id, self.location_id)
        return id

    @classmethod
    def get(cls, story_id, location_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        result_location = None
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `locations` WHERE story_id = %s AND location_id = %s"), (story_id, location_id))
            result = cur.fetchone()
            if result is None:
                return None
            result_location = cls(story_id, location_id, result['location_name'], result['original_description'], result['short_description'], result['post_event_description'],
                                  result['location_event_id'], result['auto_goto'], result['next_loc_id'], result['reviewer_comments'], result['is_verified'])
        conn.close()
        return result_location

    def update(self, story_id, location_id, name, original_description, short_description, post_event_description, location_event_id, auto_goto, next_loc_id):
        self.location_name = name
        self.original_description = original_description
        self.short_description = short_description
        self.post_event_description = post_event_description
        self.location_event_id = location_event_id
        self.auto_goto = auto_goto
        self.next_loc_id = next_loc_id

        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `locations` SET location_name = %s, original_description = %s, short_description = %s, post_event_description = %s, location_event_id = %s, auto_goto = %s, next_loc_id = %s WHERE story_id = %s and location_id = %s"),
                        (self.location_name, self.original_description, self.short_description, self.post_event_description, self.location_event_id, self.auto_goto, self.next_loc_id, story_id, location_id))
            conn.commit()
        conn.close()

    def update_admin(self, is_verified, reviewer_comments):
        self.is_verified = is_verified
        self.reviewer_comments = reviewer_comments
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `locations` SET is_verified = %s, reviewer_comments = %s WHERE story_id = %s AND location_id = %s"), (self.is_verified, self.reviewer_comments, self.story_id, self.location_id))
            conn.commit()
        conn.close()

    def show_info(self):
        conn = pymysql.connect(self.rds_host, user=self.name, passwd=self.rds_password,
                               db=self.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `locations` WHERE story_id = %s AND location_id = %s"),
                        (self.story_id, self.location_id))
            result = cur.fetchone()
            if result is None:
                return None
            else:
                return json.dumps(result)

    @classmethod
    def loc_del(cls, location_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("DELETE FROM `locations` WHERE `location_id` = %s"), (location_id))
            conn.commit()
        conn.close()

    @classmethod
    def loc_list(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        loc_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM locations WHERE story_id = %s"), (story_id))
            results = cur.fetchall()
            for row in results:
                loc_list.append(
                    cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return loc_list

    @classmethod
    def loc_list_json(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        result = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM locations WHERE story_id = %s"), (story_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                auto_goto_bool = False
                if row[7] == 0:
                    auto_goto_bool = False
                else:
                    auto_goto_bool = True
                loc_dict = {'loc_id' : row[1], 'location_name': row[2], 'original_description': row[3], 'short_description': row[4],
                                          'post_event_description': row[5], 'location_event_id': row[6], 'auto_goto': auto_goto_bool, 'next_loc_id': row[8],
                                          'decisions': StoryDecision.decs_list_json(story_id, row[1])}
                result.append(loc_dict)
        return result

    @classmethod
    def get_last_id(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        last_id = 0
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT MAX(location_id)+1 FROM locations"))
            query_data = cur.fetchone()
            last_id = query_data[0]
        conn.close()
        return last_id
