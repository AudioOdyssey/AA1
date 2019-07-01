import pymysql
import pymysql.cursors
import sys

import json

class StoryDecision:
    story_id = 0
    loc_id = 0
    sequence_num = 0
    decision_id = 0
    decision_name = ""
    transition = True
    transition_loc_id = 0
    hidden = False
    locked = False
    decision_description = ""
    show_event_id = 0
    show_object_id = 0
    unlock_event_id = 0
    unlock_object_id = 0
    locked_descr = ""
    aftermath_descr = ""
    cause_event= False
    effect_event_id = 0
    can_occur_once = False
    is_locked_by_event_id = 0
    locked_by_event_description = 0

    rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
    name = "AA_admin"
    rds_password = "z9QC3pvQ"
    db_name = "audio_adventures_dev"

    def __init__(self, story_id =0, loc_id = 0, sequence_num = 0, decision_id = 0, decision_name = "", transition = False, transition_loc_id = 0, hidden = False, locked = False, decision_description = "", show_event_id = 0, show_object_id = 0, unlock_event_id = 0, unlock_object_id = 0, locked_descr = "", aftermath_descr = "", cause_event = False, effect_event_id = 0, can_occur_once = False, is_locked_by_event_id = 0, locked_by_event_description = ""):
        self.story_id = story_id
        self.loc_id = loc_id
        self.sequence_num =  sequence_num
        self.decision_id = decision_id
        self.decision_name = decision_name
        self.transition = transition
        self.transition_loc_id = transition_loc_id
        self.hidden = hidden 
        self.locked = locked
        self.decision_description = decision_description
        self.show_event_id = show_event_id
        self.show_object_id = show_object_id  
        self.unlock_event_id = unlock_event_id    
        self.unlock_object_id = unlock_object_id
        self.locked_descr = locked_descr
        self.aftermath_descr = aftermath_descr
        self.cause_event = cause_event
        self.effect_event_id = effect_event_id
        self.can_occur_once = can_occur_once
        self.is_locked_by_event_id = is_locked_by_event_id
        self.locked_by_event_description = locked_by_event_description

    def add_to_server(self):
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT count(*) FROM `decisions`"), ())
            results = cur.fetchone()
            self.decision_id = results["count(*)"] + 1
            cur.execute(("INSERT INTO decisions(story_id, loc_id, decision_id) VALUES (%s, %s, %s)"), (self.story_id, self.loc_id, self.decision_id))
            conn.commit()
        conn.close()  

    def get_id(self):
        id = (self.story_id, self.decision_id)
        return id

    @classmethod
    def get(cls, story_id, location_id, decision_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `decisions` WHERE story_id = %s AND decision_id = %s AND loc_id = %s"), (story_id, decision_id, location_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return cls(story_id, results["loc_id"], results["sequence_num"], results["decision_id"], results["transition"], results["transition_loc_id"], results["hidden"], results["locked"], results["decision_description"], results["show_event_id"], results["show_object_id"], results["unlock_event_id"], results["unlock_object_id"], results["locked_descr"], results["aftermath_descr"], results["cause_event"], results["effect_event_id"], results["can_occur_once"], results["is_locked_by_event_id"], results["locked_by_event_description"])
    
    def update(self, story_id, decision_id, loc_id, sequence_num, decision_name, transition, transition_loc_id, hidden, locked, decision_description, show_event_id, show_object_id, unlock_event_id, unlock_object_id, locked_descr, aftermath_descr, cause_event, effect_event_id, can_occur_once, is_locked_by_event_id, locked_by_event_description):
        self.sequence_num =  sequence_num
        self.decision_name = decision_name
        self.transition = transition
        self.transition_loc_id = transition_loc_id
        self.hidden = hidden 
        self.locked = locked
        self.decision_description = decision_description
        self.show_event_id = show_event_id
        self.show_object_id = show_object_id  
        self.unlock_event_id = unlock_event_id    
        self.unlock_object_id = unlock_object_id
        self.locked_descr = locked_descr
        self.aftermath_descr = aftermath_descr
        self.cause_event = cause_event
        self.effect_event_id = effect_event_id
        self.can_occur_once = can_occur_once
        self.is_locked_by_event_id = is_locked_by_event_id
        self.locked_by_event_description = locked_by_event_description
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `decisions` SET sequence_num = %s, decision_name=%s, transition = %s, transition_loc_id = %s, hidden = %s,  locked = %s, decision_description = %s, show_event_id = %s, show_object_id = %s, unlock_event_id = %s, unlock_object_id = %s, locked_descr = %s, aftermath_descr = %s, cause_event = %s, effect_event_id = %s, can_occur_once = %s, is_locked_by_event_id = %s, locked_by_event_description = %s WHERE story_id = %s AND decision_id= %s AND loc_id = %s"),
                        (self.sequence_num, self.decision_name, self.transition, self.transition_loc_id, self.hidden, self.locked, self.decision_description, self.show_event_id, self.show_object_id, self.unlock_event_id, self.unlock_object_id, self.locked_descr, self.aftermath_descr, self.cause_event, self.effect_event_id, self.can_occur_once, self.is_locked_by_event_id, self.locked_by_event_description, story_id, decision_id, loc_id))
            conn.commit()
        conn.close()

    def show_info(self):
        conn = pymysql.connect(self.rds_host, user = self.name, passwd = self.rds_password, db = self.db_name, connect_timeout = 5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `decisions` WHERE story_id = %s AND decision_id = %s"), (self.story_id, self.decision_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return json.dumps(results)

    @classmethod
    def dec_del(cls, dec_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("DELETE FROM `decisions` WHERE `decision_id` = %s"), (dec_id))
            conn.commit()
        conn.close()
    
    @classmethod
    def dec_list(cls, story_id, loc_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        decs_list = []
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `decisions` WHERE story_id = %s AND loc_id = %s"), (story_id, loc_id))
            results = cur.fetchall()
            for row in results:
                decs_list.append(cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20]))
        conn.close()
        return decs_list

    @classmethod
    def decs_list_json(cls, story_id, loc_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user = name, passwd = rds_password, db = db_name, connect_timeout = 5)
        result = []
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `decisions` WHERE story_id = %s AND loc_id = %s"), (story_id, loc_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                is_hidden_bool = False
                if row[7] == 1:
                    is_hidden_bool = True
                else:
                    is_hidden_bool = False
                is_locked_bool = False
                if row[8] == 1:
                    is_locked_bool = True
                else:
                    is_locked_bool = False
                cause_event_bool = False
                if row[16] == 0:
                    cause_event_bool = False
                else:
                    cause_event_bool = True
                can_occur_once_bool = False
                if row[18] == 0:
                    can_occur_once_bool = False
                else:
                    can_occur_once_bool = True
                transition_bool = True
                if row[5] == 0:
                    transition_bool = False
                desc_dict = {'dec_id' : row[3], 'sequence_num' : row[2], 'decision_name' : row[4], 'transition' : transition_bool, 
                'transition_loc_id'  : row[6], 'hidden' : is_hidden_bool, 'locked' : is_locked_bool, 
                'decision_description' : row[9], 'show_event_id' : row[10], 'show_object_id' : row[11], 
                'unlock_event_id'  : row[12], 'unlock_object_id'  :row[13], 'locked_descr' :row[14], 'aftermath_descr'  :row[15], 
                'cause_event' : cause_event_bool, 'effect_event_id'  :row[17], 'can_occur_once'  : can_occur_once_bool, 'is_locked_by_event_id'  :row[19], 
                'locked_by_event_description'  :row[20]}
                result.append(desc_dict)
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
            cur.execute(("SELECT count(*) FROM `decisions` WHERE story_id = %s"), story_id)
            query_data = cur.fetchone()
            last_id = query_data[0]
        conn.close()
        return last_id