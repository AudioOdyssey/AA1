import pymysql
import pymysql.cursors

import sys
import os

import simplejson as json

from .storyobject import StoryObject
from .storyevent import StoryEvent
from .storylocation import StoryLocation
from .storydecision import StoryDecision

from decimal import Decimal

from datetime import datetime, date

import base64


class Story:
    story_id = 0
    story_title = ''
    story_author = ''
    story_synopsis = ''
    story_price = Decimal(0)
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
    genre = ''
    user_creator_id = 0
    reviewer_comments = ''
    verification_status = 0
    inventory_size = 0
    parental_ratings = 0.0
    updated_at = None

    def __init__(self, story_id=0, story_title='', story_author='', story_synopsis='', story_price=0,
                 author_paid=False, genre='', length_of_story=0, number_of_locations=0, number_of_decisions=0, story_in_store=False,
                 story_verification_date='', name_of_verifier='', verification_status='',
                 story_ratings=0, story_language_id=1, storage_size=0, user_creator_id=0, reviewer_comments='', starting_loc=0, inventory_size=0, parental_ratings=0.0):
        if story_id:
            self.story_id = story_id
        self.story_title = story_title
        self.story_author = story_author
        self.story_synopsis = story_synopsis
        self.story_price = Decimal(story_price)
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
        self.user_creator_id = user_creator_id
        self.reviewer_comments = reviewer_comments
        self.starting_loc = starting_loc
        self.inventory_size = inventory_size
        self.parental_ratings = parental_ratings

    def add_to_server(self):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(("INSERT INTO master_stories(story_title, story_author, story_price, user_creator_id) VALUES(%s, %s, %s, %s)"),
                        (self.story_title, self.story_author, self.story_price, self.user_creator_id))
            conn.commit()
            # unlike the other IDs, this table has an auto-incrememntal primary ID. So no +1 - Sonny
            cur.execute(("SELECT MAX(story_id) FROM master_stories"))
            query_data = cur.fetchone()
            self.story_id = query_data[0]
            conn.commit()
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
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE story_id = %s"), (story_id))
            results = cur.fetchone()
            if results is None:
                return None
            else:
                return cls(story_id=story_id, story_title=results["story_title"], story_author=results["story_author"], story_synopsis=results["story_synopsis"],
                           story_price=results["story_price"], author_paid=results[
                               "author_paid"], genre=results['genre'], length_of_story=results["length_of_story"],
                           number_of_locations=results["number_of_location"], number_of_decisions=results[
                               "number_of_decisions"], story_in_store=results["story_in_store"],
                           story_verification_date=results["story_verification_date"], name_of_verifier=results[
                               "name_of_verifier"], verification_status=results['verification_status'], story_ratings=results["story_ratings"],
                           story_language_id=results["story_language_id"], storage_size=results[
                               "storage_size"], user_creator_id=results["user_creator_id"],
                           reviewer_comments=results['reviewer_comments'], starting_loc=results['starting_loc'], inventory_size=results['inventory_size'], parental_ratings=results['parental_ratings'])

    def update(self, story_title, story_author, story_price, story_language_id, genre, story_synopsis):
        self.story_title = story_title
        self.story_author = story_author
        self.story_price = story_price
        self.story_language_id = story_language_id
        self.genre = genre
        self.story_synopsis = story_synopsis
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"

        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `master_stories` SET story_title = %s, story_author = %s, story_price = %s, story_language_id = %s, genre = %s, story_synopsis = %s, inventory_size = %s, starting_loc = %s, length_of_story = %s WHERE story_id = %s"),
                        (self.story_title, self.story_author, self.story_price, self.story_language_id, self.genre, self.story_synopsis, self.inventory_size, self.starting_loc, self.length_of_story, self.story_id))
            conn.commit()
        conn.close()

    def update_admin(self, reviewer_comments, parental_ratings, name_of_verifier):
        self.reviewer_comments = reviewer_comments
        self.parental_ratings = parental_ratings
        self.name_of_verifier = name_of_verifier
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE master_stories SET story_ratings = %s, story_verification_date = %s, obj_verification_status = %s, event_verification_status = %s, storage_size = %s, reviewer_comments = %s, updated_at = NOW(), story_verification_date = CURDATE(), name_of_verifier = %s WHERE story_id = %s"),
                        (self.story_ratings, self.story_verification_date, self.storage_size, self.reviewer_comments, self.name_of_verifier, self.story_id))
            conn.commit()
            cur.execute(
                ("SELECT updated_at, story_verification_date WHERE story_id = %s"), (self.story_id))
            query_data = cur.fetchall()
            self.updated_at = query_data['updated_at']
            self.story_verification_date = query_data['story_verification_date']
        conn.close()

    def get_image_base64(self):
        upload_folder = '/var/www/pictures/'
        cover_file = str(self.story_id) + ".jpg"
        result = ''
        try:
            with open(os.path.join(upload_folder, cover_file), 'rb') as image_file:
                result = base64.b64encode(image_file.read())
        except FileNotFoundError:
            return ''
        return result

    @classmethod
    def story_list_by_creator(cls, user_creator_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE user_creator_id = %s"), (user_creator_id))
            results = cur.fetchall()
            for row in results:
                story_list.append(
                    cls(row[0], row[1], row[2], row[3], row[4], row[6], user_creator_id=row[19]))
        conn.close()
        return story_list

    @classmethod
    def story_list_for_purchase(cls):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE verification_status = 3"))
            results = cur.fetchall()
            for row in results:
                story_list.append(
                    cls(row[0], row[1], row[2], row[3], row[4], row[6], user_creator_id=row[19]))
        conn.close()
        return story_list

    @classmethod
    def story_list_purchased_by_user(cls, user_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE story_id in (SELECT story_id FROM user_downloads WHERE user_id = %s) union all SELECT * FROM `master_stories` WHERE story_id in (SELECT story_id FROM user_downloads WHERE company_id = (SELECT company_id FROM users WHERE user_id = %s))"), (user_id, user_id))
            results = cur.fetchall()
            for row in results:
                story_list.append(
                    cls(row[0], row[1], row[2], row[3], row[4], row[6], user_creator_id=row[19]))
        conn.close()
        return story_list

    @classmethod
    def json_story_library(cls, user_id):
        library = cls.story_list_purchased_by_user(user_id)
        result = []
        for story in library:
            stry_schema = {
                "story_id": story.story_id,
                "story_title": story.story_title,
                "story_author": story.story_author,
                "story_synopsis": story.story_synopsis,
                "story_price": story.story_price,
                "genre": story.genre,
                "cover": story.get_image_base64()
            }
            result.append(stry_schema)
        return json.dumps(result)

    @classmethod
    def story_list_ready_for_verification(cls):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                "SELECT story_id, story_title FROM `master_stories` WHERE verification_status = 1 ORDER BY updated_at ASC LIMIT 20")
            results = cur.fetchall()
            for row in results:
                story_list.append(cls(row[0], row[1]))
        conn.close()
        return story_list

    @classmethod
    def story_list_master(cls):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                "SELECT story_id, story_title FROM `master_stories`")
            results = cur.fetchall()
            for row in results:
                story_list.append(cls(row[0], row[1]))
        conn.close()
        return story_list

    @classmethod
    def story_list_json(cls, user_creator_id):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        result = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE user_creator_id = %s"), (user_creator_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                story_dict = {'story_id': row[0], 'story_title': row[1], 'story_author': row[2], 'story_synopsis': row[3], 'story_price': row[4],
                              'author_paid': row[5], 'genre': row[6], 'length_of_story': row[7], 'number_of_locations': row[8],
                              'number_of_decisions': row[9], 'story_in_store': row[10], 'story_verification_date': row[11], 'name_of_verifier': row[12],
                              'verification_status':  row[13], 'story_ratings': row[14], 'story_language_id': row[15], 'storage_size': row[16],
                              'obj_verification_status': row[17], 'event_verification_status': row[18], 'user_creator_id': row[19]}
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
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            # unlike the other IDs, this table has an auto-incrememntal primary ID. So no +1 - Sonny
            cur.execute(
                ("SELECT MAX(story_id) FROM master_stories"))
            result = cur.fetchone()
            last_id = result[0]
        conn.close()
        return last_id

    @classmethod
    def get_story_count(cls):
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        last_id = 0
        conn = pymysql.connect(
            rds_host, user=name, passwd=rds_password, db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT COUNT(story_id) FROM master_stories"))
            result = cur.fetchone()
            last_id = result[0]
        conn.close()
        return last_id

    @classmethod
    def get_info(cls, story_id):
        stry = Story.get(story_id)
        result = {
            'story_title': stry.story_title,
            'story_author': stry.story_author,
            'story_synopsis': stry.story_synopsis,
            'length_of_story': stry.length_of_story,
            'number_of_locations': stry.number_of_locations,
            'number_of_decisions': stry.number_of_decisions,
            'genre': stry.genre
        }
        return json.dumps(result)

    @classmethod
    def get_entities(cls, story_id):
        result = {
            'story_id': story_id,
            'objects': StoryObject.obj_list_json(story_id),
            'events': StoryEvent.event_list_json(story_id),
            'locations': StoryLocation.loc_list_json(story_id)
        }
        return json.dumps(result)

    @classmethod
    def display_for_store(cls):
        result = []
        rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
        name = "AA_admin"
        rds_password = "z9QC3pvQ"
        db_name = "audio_adventures_dev"
        conn = pymysql.connect(rds_host, user=name, passwd=rds_password,
                               db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT story_id, story_title, story_author, story_synopsis, story_price, genre FROM `master_stories`"))
            query_data = cur.fetchall()
            for row in query_data:
                stry = cls.get(row[0])
                stry_info = {'story_id': row[0], 'story_title': row[1],
                             'story_author': row[2], 'story_synopsis': row[3],
                             'story_price': row[4], 'genre': row[5],
                             'cover': stry.get_image_base64()}
                result.append(stry_info)
        storefront = {"stories": result}
        return json.dumps(storefront)
