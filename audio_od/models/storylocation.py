#Python standard libraries
import sys
import json
from datetime import datetime


#Third-party libraries
import pymysql
import pymysql.cursors

#Internal imports
from audio_od import config
from .storydecision import StoryDecision


class StoryLocation:
    story_id = 0
    location_id = 0
    location_name = ""
    original_description = ""
    short_description = ""
    post_event_description = ""
    location_event_id = 0
    next_loc_id = 0
    reviewer_comments = ''
    verification_status = False

    def __init__(self, story_id=0, location_id=0, location_name='', original_description='', short_description='', post_event_description='', location_event_id=0, next_loc_id=0, reviewer_comments='', verification_status=False):
        self.story_id = story_id
        self.location_id = location_id
        self.location_name = location_name
        self.original_description = original_description
        self.short_description = short_description
        self.post_event_description = post_event_description
        self.location_event_id = location_event_id
        self.next_loc_id = next_loc_id
        self.reviewer_comments = reviewer_comments
        self.verification_status = verification_status

    def add_to_server(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            self.location_id = self.get_last_id(self.story_id)
            cur.execute(("INSERT INTO locations(story_id, location_id) VALUES (%s, %s)"),
                        (self.story_id, self.location_id))
            conn.commit()
        conn.close()

    def get_id(self):
        id = (self.story_id, self.location_id)
        return id

    @classmethod
    def get(cls, story_id, location_id):
        result_location = None
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `locations` WHERE story_id = %s AND location_id = %s"), (story_id, location_id))
            result = cur.fetchone()
            if result is None:
                return None
            result_location = cls(story_id, location_id, result['location_name'], result['original_description'], result['short_description'], result['post_event_description'],
                                  result['location_event_id'], result['next_loc_id'], result['reviewer_comments'], result['verification_status'])
        conn.close()
        return result_location

    def update(self, story_id, location_id, name, original_description, short_description, post_event_description, location_event_id, next_loc_id):
        self.location_name = name
        self.original_description = original_description
        self.short_description = short_description
        self.post_event_description = post_event_description
        self.location_event_id = location_event_id
        self.next_loc_id = next_loc_id

        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `locations` SET location_name = %s, original_description = %s, short_description = %s, post_event_description = %s, location_event_id = %s, next_loc_id = %s WHERE story_id = %s and location_id = %s"),
                        (self.location_name, self.original_description, self.short_description, self.post_event_description, self.location_event_id, self.next_loc_id, story_id, location_id))
            conn.commit()
        conn.close()

    def update_admin(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `locations` SET verification_status = %s, reviewer_comments = %s WHERE story_id = %s AND location_id = %s"),
                        (self.verification_status, self.reviewer_comments, self.story_id, self.location_id))
            conn.commit()
        conn.close()

    def show_info(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `locations` WHERE story_id = %s AND location_id = %s"),
                        (self.story_id, self.location_id))
            result = cur.fetchone()
            if result is None:
                return None
            else:
                return json.dumps(result)

    @classmethod
    def loc_del(cls, story_id, location_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("DELETE FROM `locations` WHERE `story_id` = %s AND `location_id` = %s"), (story_id, location_id))
            conn.commit()
        conn.close()

    @classmethod
    def loc_list(cls, story_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        loc_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM locations WHERE story_id = %s"), (story_id))
            results = cur.fetchall()
            for row in results:
                loc_list.append(
                    cls(row['story_id'], row['location_id'], row['location_name'], row['original_description'], row['short_description'], row['post_event_description'], next_loc_id=row['next_loc_id'], reviewer_comments=row['reviewer_comments'], verification_status=row['verification_status']))
        return loc_list

    @classmethod
    def loc_list_json(cls, story_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        result = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM locations WHERE story_id = %s"), (story_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                loc_dict = {'loc_id': row['location_id'], 'location_name': row['location_name'], 'original_description': row['original_description'], 'short_description': row['short_description'],
                            'post_event_description': row['post_event_description'], 'location_event_id': row['location_event_id'], 'next_loc_id': row['next_loc_id'],
                            'decisions': StoryDecision.decs_list_json(story_id, row['location_id'])}
                result.append(loc_dict)
        return result

    @classmethod
    def get_last_id(cls, story_id):
        last_id = 0
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT MAX(location_id)+1 FROM locations"))
            query_data = cur.fetchone()
            last_id = query_data[0]
        conn.close()
        if last_id is None:
            last_id = 1
        return last_id

    @classmethod
    def check_verify(cls, story_id):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT COUNT(location_id) FROM locations WHERE story_id = %s AND verification_status != 3"), (story_id))
            results = cur.fetchone()
            if results is None:
                return None
            return results['COUNT(location_id)'] == 0
