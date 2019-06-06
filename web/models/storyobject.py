import pymysql
import pymysql.cursors
import sys

import json
class StoryObject:
    story_id = 0
    obj_id = 0
    obj_name = ""
    obj_description = ""
    can_pickup_obj = 0
    obj_starting_loc = 0
    is_hidden = 0
    unhide_event_id = 0

    REGION = 'us-east-2b'

    rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
    name = "AA_admin"
    rds_password = "z9QC3pvQ"
    db_name = "audio_adventures_dev"
    

    def __init__(self, story_id = 0, obj_name = "", obj_description = "", can_pickup_obj = 0, obj_starting_loc = 0, is_hidden = 0, unhide_event_id = 0):
        self.story_id = story_id

        self.obj_name = obj_name

        self.obj_description = obj_description

        self.can_pickup_obj = can_pickup_obj

        self.obj_starting_loc = obj_starting_loc

        self.is_hidden = is_hidden

        self.unhide_event_id = unhide_event_id

    def add_to_server(self):
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT count(*) FROM `objects` WHERE story_id = %s"), (self.story_id))
            results = cur.fetchone()
            self.obj_id = results["count(*)"] + 1
            cur.execute(("INSERT INTO objects(story_id, obj_id, obj_starting_loc, obj_name, obj_description, can_pickup_obj, is_hidden, unhide_event_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s")
                        , (self.story_id, self.obj_id, self.obj_starting_loc, self.obj_name, self.obj_description, self.can_pickup_obj, self.is_hidden, self.unhide_event_id))
            conn.commit()
        conn.close()

    def get_id(self):
        id = (self.story_id, self.obj_id)
        return id

    def get(self, story_id, obj_id):
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `objects` WHERE story_id = %s AND obj_id = %s"), (story_id, obj_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return StoryObject(story_id, results["obj_name"], results["obj_description"], results["can_pickup_obj"], results["obj_starting_loc"], results["is_hidden"], results["unhide_event_id"])
    
    def update(self, story_id, obj_id, name, starting_loc, desc, can_pickup_obj, is_hidden, unhide_event_id):
            self.name = name
            self.obj_starting_loc = starting_loc
            self.obj_description = desc
            self.can_pickup_obj = can_pickup_obj
            self.is_hidden = is_hidden
            self.unhide_event_id = unhide_event_id
            conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
            with conn.cursor() as cur:
                cur.execute(("UPDATE `objects` SET obj_name = %s, obj_starting_loc = %s, obj_description = %s, can_pickup_obj=%s, is_hidden = %s, unhide_event_id=%s WHERE story_id = %s AND obj_id"),
                            (self.name, self.obj_starting_loc, self.obj_description, self.can_pickup_obj, self.is_hidden, self.unhide_event_id, story_id, obj_id))
                conn.commit()
            conn.close()
        
    def show_info(self):
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `objects` WHERE story_id = %s AND obj_id = %s"), (self.story_id, self.obj_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return json.dumps(results)

    @classmethod
    def obj_list(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        objs_list = []
        with conn.cursor() as cur:
            cur(("SELECT * FROM `objects` WHERE story_id = %s"), (story_id))
            results = cur.fetchall()
            for row in results:
                objs_list.append(cls(row[0], row[3], row[4], row[5], row[2], row[6], row[7]))
        conn.close()
        return objs_list