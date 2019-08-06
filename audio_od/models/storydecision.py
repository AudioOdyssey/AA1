#Python standard libraries
import sys
import json
sys.path.append("..")


#Third-party libraries
import pymysql
import pymysql.cursors


#Internal imports
from audio_od import config
# from . import *


class StoryDecision:
    story_id = 0
    loc_id = 0
    sequence_num = 1
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
    cause_event = False
    effect_event_id = 0
    can_occur_once = False
    is_locked_by_event_id = 0
    locked_by_event_description = 0
    reviewer_comments = ''
    verification_status = False
    reset_story = False

    def __init__(self, story_id=0, loc_id=0, sequence_num=1, decision_id=0, decision_name="", transition=False, transition_loc_id=0, hidden=False, locked=False, 
                decision_description="", show_event_id=0, show_object_id=0, unlock_event_id=0, unlock_object_id=0, locked_descr="", aftermath_descr="", 
                cause_event=False, effect_event_id=0, can_occur_once=False, is_locked_by_event_id=0, locked_by_event_description="", 
                reviewer_comments='', verification_status=False, reset_story = False):
        self.story_id = story_id
        self.loc_id = loc_id
        self.sequence_num = sequence_num
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
        self.reviewer_comments = reviewer_comments
        self.verification_status = verification_status
        self.reset_story = reset_story

    def add_to_server(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            self.decision_id = self.get_last_id(self.story_id, self.loc_id)
            cur.execute(("INSERT INTO decisions(story_id, loc_id, decision_id, sequence_num) VALUES (%s, %s, %s, %s)"),
                        (self.story_id, self.loc_id, self.decision_id, self.sequence_num))
            conn.commit()
        conn.close()

    def get_id(self):
        id = (self.story_id, self.decision_id)
        return id

    @classmethod
    def get(cls, story_id, loc_id, decision_id):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `decisions` WHERE decision_id = %s AND story_id = %s AND loc_id = %s"),
                        (decision_id, story_id, loc_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return cls(story_id, results["loc_id"], results["sequence_num"], results["decision_id"], 
                    results['decision_name'], results["transition"], results["transition_loc_id"], 
                    results["hidden"], results["locked"], results["decision_description"], 
                    results["show_event_id"], results["show_object_id"], results["unlock_event_id"], 
                    results["unlock_object_id"], results["locked_descr"], results["aftermath_descr"], 
                    results["cause_event"], results["effect_event_id"], results["can_occur_once"], 
                    results["is_locked_by_event_id"], results["locked_by_event_description"], results['reviewer_comments'], 
                    results['verification_status'], results['reset_story'])

    def update(self, story_id, decision_id, loc_id, sequence_num, decision_name, 
            transition, transition_loc_id, hidden, locked, decision_description, show_event_id, 
            show_object_id, unlock_event_id, unlock_object_id, locked_descr, aftermath_descr, cause_event, 
            effect_event_id, can_occur_once, is_locked_by_event_id, locked_by_event_description, reset_story):
        self.sequence_num = sequence_num
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
        self.reset_story = reset_story
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `decisions` SET sequence_num = %s, decision_name=%s, transition = %s, transition_loc_id = %s, hidden = %s,  locked = %s, decision_description = %s, show_event_id = %s, show_object_id = %s, unlock_event_id = %s, unlock_object_id = %s, locked_descr = %s, aftermath_descr = %s, cause_event = %s, effect_event_id = %s, can_occur_once = %s, is_locked_by_event_id = %s, locked_by_event_description = %s, reset_story = %s WHERE decision_id= %s"),
                        (self.sequence_num, self.decision_name, self.transition, self.transition_loc_id, self.hidden, self.locked, self.decision_description, self.show_event_id, self.show_object_id, self.unlock_event_id, self.unlock_object_id, self.locked_descr, self.aftermath_descr, self.cause_event, self.effect_event_id, self.can_occur_once, self.is_locked_by_event_id, self.locked_by_event_description, reset_story, decision_id))
            conn.commit()
        conn.close()

    def update_admin(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `decisions` SET reviewer_comments = %s, verification_status = %s WHERE story_id = %s AND loc_id = %s AND decision_id = %s"),
                        (self.reviewer_comments, self.verification_status, self.story_id, self.loc_id, self.decision_id))
            conn.commit()
        conn.close()

    def show_info(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("SELECT * FROM `decisions` WHERE story_id = %s AND decision_id = %s"),
                        (self.story_id, self.decision_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return json.dumps(results)

    @classmethod
    def check_verify(cls, story_id):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT COUNT(decision_id) FROM decisions WHERE story_id = %s AND verification_status != 3"), (story_id))
            results = cur.fetchone()
            if results is None:
                return None
            return results['COUNT(decision_id)'] == 0

    @classmethod
    def dec_del(cls, story_id, loc_id, dec_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("DELETE FROM `decisions` WHERE `story_id` = %s AND `loc_id` = %s AND `decision_id` = %s"), (story_id, loc_id, dec_id))
            conn.commit()
        conn.close()

    @classmethod
    def dec_list_for_story_loc(cls, story_id, loc_id):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        decs_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `decisions` WHERE story_id = %s AND loc_id = %s ORDER BY sequence_num"), (story_id, loc_id))
            results = cur.fetchall()
            for row in results:
                decs_list.append(cls(row["story_id"], row["loc_id"], row["sequence_num"], row["decision_id"], row["decision_name"], row["transition"], row["transition_loc_id"], row["hidden"], row["locked"], row["decision_description"], row["show_event_id"], row["show_object_id"],
                                     row["unlock_event_id"], row["unlock_object_id"], row["locked_descr"], row["aftermath_descr"], row["cause_event"], row["effect_event_id"], row["can_occur_once"], row["is_locked_by_event_id"], row["locked_by_event_description"], row["reviewer_comments"], row["verification_status"]))
        conn.close()
        return decs_list

    @classmethod
    def dec_list_story(cls, story_id):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        decs_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `decisions` WHERE story_id = %s"), (story_id))
            results = cur.fetchall()
            for row in results:
                decs_list.append(cls(row['story_id'], row['loc_id'], row['sequence_num'],
                                     row['decision_id'], row['decision_name'], row['transition'],
                                     row['transition_loc_id'], row['hidden'], row['locked'],
                                     row['decision_description'], row['show_event_id'], row['show_object_id'],
                                     row['unlock_event_id'], row['unlock_object_id'], row['locked_descr'], row['aftermath_descr'],
                                     row['cause_event'], row['effect_event_id'], row['can_occur_once'],
                                     row['is_locked_by_event_id'], row['locked_by_event_description'],
                                     row['reviewer_comments'], row['verification_status']))
            conn.close()
        return decs_list

    @classmethod
    def decs_list_json(cls, story_id, loc_id):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        result = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `decisions` WHERE story_id = %s AND loc_id = %s"), (story_id, loc_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                is_hidden_bool = False
                if row["hidden"] == 1:
                    is_hidden_bool = True
                else:
                    is_hidden_bool = False
                is_locked_bool = False
                if row["locked"] == 1:
                    is_locked_bool = True
                else:
                    is_locked_bool = False
                cause_event_bool = False
                if row["cause_event"] == 0:
                    cause_event_bool = False
                else:
                    cause_event_bool = True
                can_occur_once_bool = False
                if row["can_occur_once"] == 0:
                    can_occur_once_bool = False
                else:
                    can_occur_once_bool = True
                transition_bool = True
                if row["transition"] == 0:
                    transition_bool = False
                reset_story_bool = True
                if row['reset_story'] == 0:
                    reset_story_bool = False
                desc_dict = {'dec_id': row['decision_id'], 'sequence_num': row['sequence_num'], 'decision_name': row['decision_name'], 'transition': transition_bool,
                             'transition_loc_id': row['transition_loc_id'], 'hidden': is_hidden_bool, 'locked': is_locked_bool,
                             'decision_description': row['decision_description'], 'show_event_id': row['show_event_id'], 'show_object_id': row['show_object_id'],
                             'unlock_event_id': row['unlock_event_id'], 'unlock_object_id': row['unlock_object_id'], 'locked_descr': row['locked_descr'], 'aftermath_descr': row['aftermath_descr'],
                             'cause_event': cause_event_bool, 'effect_event_id': row['effect_event_id'], 'can_occur_once': can_occur_once_bool, 'is_locked_by_event_id': row['is_locked_by_event_id'],
                             'locked_by_event_description': row['locked_by_event_description'], 'reset_story' : reset_story_bool}
                result.append(desc_dict)
        return result

    @classmethod
    def get_last_id(cls, story_id, loc_id):
        last_id = 0
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(("SELECT MAX(decision_id)+1 FROM `decisions`"))
            query_data = cur.fetchone()
            last_id = query_data[0]
        conn.close()
        return last_id
