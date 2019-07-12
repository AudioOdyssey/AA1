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
    reviewer_comments = ''
    verification_status = False

    REGION = 'us-east-2b'

    rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
    name = "AA_admin"
    rds_password = "z9QC3pvQ"
    db_name = "audio_adventures_dev"
    

    def __init__(self, story_id = 0, obj_id = 0, obj_name = "", obj_description = "", can_pickup_obj = 0, obj_starting_loc = 0, is_hidden = 0, unhide_event_id = 0, reviewer_comments = '', verification_status = False):
        self.story_id = story_id

        self.obj_id = obj_id

        self.obj_name = obj_name

        self.obj_description = obj_description

        self.can_pickup_obj = can_pickup_obj

        self.obj_starting_loc = obj_starting_loc

        self.is_hidden = is_hidden

        self.unhide_event_id = unhide_event_id

        self.reviewer_comments = reviewer_comments

        self.verification_status = verification_status

    def add_to_server(self):
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            self.obj_id = self.get_last_id(self.story_id)
            cur.execute(("INSERT INTO objects(story_id, obj_id) VALUES (%s, %s)"), (self.story_id, self.obj_id))
            conn.commit()
        conn.close()

    def get_id(self):
        id = (self.story_id, self.obj_id)
        return id

    @classmethod
    def get(cls, story_id, obj_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `objects` WHERE story_id = %s AND obj_id = %s"), (story_id, obj_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return cls(story_id, results['obj_id'], results["obj_name"], results["obj_description"], results["can_pickup_obj"], results["obj_starting_loc"], results["is_hidden"], results["unhide_event_id"], results['reviewer_comments'], results['verification_status'])
    
    def update(self, story_id, object_id, name, starting_loc, desc, can_pickup_obj, is_hidden):
        self.obj_name = name
        self.obj_starting_loc = starting_loc
        self.obj_description = desc
        self.can_pickup_obj = can_pickup_obj
        self.is_hidden = is_hidden
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `objects` SET obj_name = %s, obj_starting_loc = %s, obj_description = %s, can_pickup_obj=%s, is_hidden = %s WHERE story_id = %s AND obj_id= %s"),
                        (self.obj_name, self.obj_starting_loc, self.obj_description, self.can_pickup_obj, self.is_hidden, story_id, object_id))
            conn.commit()
        conn.close()
        
    def update_admin(self, verification_status, reviewer_comments):
        self.verification_status = verification_status
        self.reviewer_comments = reviewer_comments
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `objects` SET verification_status = %s, reviewer_comments = %s WHERE story_id = %s AND obj_id = %s"), (self.verification_status, self.reviewer_comments, self.story_id, self.obj_id))
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
    def obj_del(cls, obj_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        with conn.cursor() as cur:
            cur.execute(("DELETE FROM `objects` WHERE `obj_id` = %s"), (obj_id))
            conn.commit()
        conn.close()

    @classmethod
    def obj_list(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass=pymysql.cursors.DictCursor)
        objs_list = []
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `objects` WHERE story_id = %s"), (story_id))
            results = cur.fetchall()
            for row in results:
                objs_list.append(cls(row['story_id'], row['obj_id'], row['obj_name'], row['obj_description'], row['can_pickup_obj'], row['obj_starting_loc'], row['is_hidden'], row['unhide_event_id'], row['reviewer_comments'], row['verification_status']))
        conn.close()
        return objs_list
    
    @classmethod
    def obj_list_loc(cls, story_id, location_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass=pymysql.cursors.DictCursor)
        objs_list = []
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `objects` WHERE obj_starting_loc = %s"), (location_id))
            results = cur.fetchall()
            for row in results:
                objs_list.append(cls(row['story_id'], row['obj_id'], row['obj_name'], row['obj_description'], row['can_pickup_obj'], row['obj_starting_loc'], row['is_hidden'], row['unhide_event_id'], row['reviewer_comments'], row['verification_status']))
        conn.close()
        return objs_list

    @classmethod
    def obj_list_json(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        result = []
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `objects` WHERE story_id = %s"), (story_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                is_hidden_bool = False
                if row[6] == 0:
                    is_hidden_bool = False
                else:
                    is_hidden_bool = True
                can_pickup_bool = False
                if row[5] == 0:
                    can_pickup_bool = False
                else:
                    can_pickup_bool = True
                obj_info = {"obj_id" : row[1], "obj_starting_loc" : row[2], "obj_name" : row[3], "obj_description" : row[4], 
                "can_pickup" : can_pickup_bool, "is_hidden" : is_hidden_bool, "unhide_event_id" : row[7]}
                result.append(obj_info)
        return result

    @classmethod
    def get_last_id(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        last_id = 0
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        with conn.cursor() as cur:
            cur.execute(("SELECT MAX(obj_id)+1 FROM `objects`"))
            query_data = cur.fetchone()
            last_id = query_data[0]
        conn.close()
        return last_id
         
    @classmethod
    def check_verify(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT COUNT(obj_id) FROM objects WHERE story_id = %s AND verification_status != 3"), (story_id))
            results = cur.fetchone()
            if results is None:
                return None
            return results['COUNT(obj_id)'] == 0