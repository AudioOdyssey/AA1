import pymysql
import pymysql.cursors
import sys

import json


class StoryEvent:
    #event_location_name = ""
    story_id = 0
    event_id = 0
    event_name = ""
    event_description = ""
    event_location_id = 0
    event_is_global = False
    reviewer_comments = ''
    verification_status = False
    rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
    name = "AA_admin"
    rds_password = "z9QC3pvQ"
    db_name = "audio_adventures_dev"

    def __init__(self, story_id=0, event_id=0, event_name=0, event_description='', event_location_id=0, event_is_global=False, reviewer_comments='', verification_status=False):
        self.story_id = story_id
        self.event_id = event_id
        self.event_name = event_name
        self.event_description = event_description
        self.event_location_id = event_location_id
        self.event_is_global = event_is_global
        self.reviewer_comments = reviewer_comments
        self.verification_status = verification_status

    def add_to_server(self):
        conn = pymysql.connect(self.rds_host, user=self.name, passwd=self.rds_password,
                               db=self.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            self.event_id = self.get_last_id(self.story_id)
            cur.execute(("INSERT INTO events(story_id, event_id) VALUES (%s, %s)"),
                        (self.story_id, self.event_id))
            conn.commit()
        conn.close()

    def get_id(self):
        id = (self.story_id, self.event_id)
        return id

    @classmethod
    def get(cls, story_id, event_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `events` WHERE story_id = %s AND event_id = %s"), (story_id, event_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return cls(story_id, results["event_id"], results["event_name"], results["event_description"], results["event_location_id"], results["event_is_global"], results['reviewer_comments'], results['verification_status'])

    def update(self, story_id, event_id, name, location_id, description, is_global):
        self.event_name = name
        self.event_location_id = location_id
        self.event_description = description
        self.event_is_global = is_global
        conn = pymysql.connect(self.rds_host, user=self.name, passwd=self.rds_password,
                               db=self.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `events` SET event_name = %s, event_location_id = %s, event_description = %s, event_is_global=%s WHERE story_id = %s AND event_id= %s"),
                        (self.event_name, self.event_location_id, self.event_description, self.event_is_global, story_id, event_id))
            conn.commit()
        conn.close()

    def update_admin(self):
        conn = pymysql.connect(self.rds_host, user=self.name, passwd=self.rds_password,
                               db=self.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `events` SET reviewer_comments = %s, verification_status = %s WHERE story_id = %s AND event_id = %s"),
                        (self.reviewer_comments, self.verification_status, self.story_id, self.event_id))
            conn.commit()
        conn.close()

    def show_info(self):
        conn = pymysql.connect(self.rds_host, user=self.name, passwd=self.rds_password,
                               db=self.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `events` WHERE story_id = %s AND event_id = %s"),
                        (self.story_id, self.event_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return json.dumps(results)

    @classmethod
    def event_del(cls, story_id, event_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("DELETE FROM `events` WHERE `story_id` = %s AND `event_id` = %s"), (story_id, event_id))
            conn.commit()
        conn.close()

    @classmethod
    def event_list(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        events_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `events` WHERE story_id = %s"), (story_id))
            results = cur.fetchall()
            for row in results:
                events_list.append(cls(row['story_id'], row['event_id'], row['event_name'], row['event_description'],
                                       row['event_location_id'], row['event_is_global'], row['reviewer_comments'], row['verification_status']))
        conn.close()
        return events_list

    @classmethod
    def event_list_json(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        result = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `events` WHERE story_id = %s"), (story_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                event_is_global_bool = False
                if row["event_is_global"] == 0:
                    event_is_global_bool = False
                else:
                    event_is_global_bool = True
                event_dict = {"event_id": row["event_id"], "event_name": row["event_name"], "event_description": row["event_description"], "event_location_id": row["event_location_id"],
                              "event_is_global": event_is_global_bool}
                result.append(event_dict)
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
            cur.execute(("SELECT MAX(event_id)+1 FROM `events`"))
            query_data = cur.fetchall()
            last_id = query_data[0][0]
        conn.close()
        return last_id

    @classmethod
    def check_verify(cls, story_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT COUNT(event_id) FROM events WHERE story_id = %s AND verification_status != 3"), (story_id))
            results = cur.fetchone()
            if results is None:
                return None
            return results['COUNT(event_id)'] == 0
