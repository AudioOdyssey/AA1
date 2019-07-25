#Python standard libraries
import os
import sys
from decimal import Decimal
from datetime import datetime, date
import base64
sys.path.append("..")

#Third-party libraries
import pymysql
import pymysql.cursors
import simplejson as json


#Internal imports
import config
from .storydecision import StoryDecision
from .storyevent import StoryEvent
from .storylocation import StoryLocation
from .storyobject import StoryObject
from .User import User


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
    verifier_id = 0
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
    starting_loc = 0
    author_name = ''

    def __init__(self, story_id=0, story_title='', story_author='', story_synopsis='', story_price=0,
                 author_paid=False, genre='', length_of_story=0, number_of_locations=0, number_of_decisions=0, story_in_store=False,
                 story_verification_date='', verifier_id=0, verification_status='',
                 story_ratings=0, story_language_id=1, storage_size=0, user_creator_id=0, reviewer_comments='', starting_loc=0, inventory_size=0, parental_ratings=0.0, updated_at=None, author_name=''):
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
        self.verifier_id = verifier_id
        self.story_ratings = story_ratings
        self.story_language_id = story_language_id
        self.storage_size = storage_size
        self.user_creator_id = user_creator_id
        self.reviewer_comments = reviewer_comments
        self.starting_loc = starting_loc
        self.inventory_size = inventory_size
        self.parental_ratings = parental_ratings
        self.verification_status = verification_status
        self.updated_at = updated_at
        self.author_name = author_name

    def add_to_server(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5)
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
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
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
                           number_of_locations=results["number_of_locations"], number_of_decisions=results[
                               "number_of_decisions"], story_in_store=results["story_in_store"],
                           story_verification_date=results["story_verification_date"], verifier_id=results[
                               "verifier_id"], verification_status=results['verification_status'], story_ratings=results["story_ratings"],
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

        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `master_stories` SET story_title = %s, story_author = %s, story_price = %s, story_language_id = %s, genre = %s, story_synopsis = %s, inventory_size = %s, starting_loc = %s, length_of_story = %s WHERE story_id = %s"),
                        (self.story_title, self.story_author, self.story_price, self.story_language_id, self.genre, self.story_synopsis, self.inventory_size, self.starting_loc, self.length_of_story, self.story_id))
            conn.commit()
        conn.close()

    def update_verify(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE master_stories SET story_in_store = %s, parental_ratings = %s, verification_status = %s, verifier_id = %s, reviewer_comments = %s, story_verification_date = CURDATE() WHERE story_id = %s"),
                        (self.story_in_store, self.parental_ratings, self.verification_status, self.verifier_id, self.reviewer_comments, self.story_id))
            conn.commit()
        conn.close()

    def get_image_base64(self):
        cover_file = str(self.story_id) + ".jpg"
        result = ''
        try:
            with open(os.path.join(config.upload_folder, "covers", cover_file), 'rb') as image_file:
                result = base64.b64encode(image_file.read())
        except FileNotFoundError:
            return b''
        return result

    @classmethod
    def story_list_by_creator(cls, user_creator_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE user_creator_id = %s"), (user_creator_id))
            results = cur.fetchall()
            for row in results:
                story_list.append(
                    cls(row["story_id"], row["story_title"], row["story_author"], row["story_synopsis"], row["story_price"], row["genre"], user_creator_id=row["user_creator_id"], verification_status=row["verification_status"]))
        conn.close()
        return story_list

    @classmethod
    def story_list_by_creatordate(cls, user_creator_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE user_creator_id = %s ORDER BY updated_at DESC"), (user_creator_id))
            results = cur.fetchall()
            for row in results:
                story_list.append(
                    cls(row["story_id"], row["story_title"], row["story_author"], row["story_synopsis"], row["story_price"], row["genre"], user_creator_id=row["user_creator_id"], verification_status=row["verification_status"],updated_at=row['updated_at']))
        conn.close()
        return story_list

    @classmethod
    def story_list_for_purchase(cls):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE verification_status = 3"))
            results = cur.fetchall()
            for row in results:
                story_list.append(
                    cls(row["story_id"], row["story_title"], row["story_author"], row["story_synopsis"], row["story_price"], row["genre"], user_creator_id=row["user_creator_id"]))
        conn.close()
        return story_list

    @classmethod
    def story_list_purchased_by_user(cls, user_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE story_id in (SELECT story_id FROM user_downloads WHERE user_id = %s) union all SELECT * FROM `master_stories` WHERE story_id in (SELECT story_id FROM user_downloads WHERE company_id = (SELECT company_id FROM users WHERE user_id = %s))"), (user_id, user_id))
            results = cur.fetchall()
            for row in results:
                story_list.append(
                    cls(row["story_id"], row["story_title"], row["story_author"], row["story_synopsis"], row["story_price"], row["genre"], user_creator_id=row["user_creator_id"]))
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
        library_dict = {'stories' : result}
        return json.dumps(library_dict)

    @classmethod
    def story_list_ready_for_verification(cls):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                "SELECT story_id, story_title FROM `master_stories` WHERE verification_status = 1 ORDER BY updated_at ASC LIMIT 20")
            results = cur.fetchall()
            for row in results:
                story_list.append(cls(row["story_id"], row["story_title"]))
        conn.close()
        return story_list

    @classmethod
    def story_list_master(cls):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                "SELECT story_id, story_title FROM `master_stories`")
            results = cur.fetchall()
            for row in results:
                story_list.append(cls(row["story_id"], row["story_title"]))
        conn.close()
        return story_list

    @classmethod
    def story_list_json(cls, user_creator_id):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        result = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT * FROM `master_stories` WHERE user_creator_id = %s"), (user_creator_id))
            query_data = cur.fetchall()
            if query_data is None:
                return None
            for row in query_data:
                story_dict = {'story_id': row['story_id'], 'story_title': row['story_title'], 'story_author': row['story_author'], 'story_synopsis': row['story_synopsis'], 'story_price': row['story_price'],
                              'author_paid': row['author_paid'], 'genre': row['genre'], 'length_of_story': row['length_of_story'], 'number_of_locations': row['number_of_locations'],
                              'number_of_decisions': row['number_of_decisions'], 'story_in_store': row['story_in_store'], 'story_verification_date': row['story_verification_date'], 'name_of_verifier': row['name_of_verifier'],
                              'verification_status':  row['verification_status'], 'story_ratings': row['story_ratings'], 'story_language_id': row['story_language_id'], 'storage_size': row['storage_size'],
                              'obj_verification_status': row['obj_verification_status'], 'event_verification_status': row['event_verification_status'], 'user_creator_id': row['user_creator_id']}
                result.append(story_dict)
        conn.close()
        return json.dumps(result)

    @classmethod
    def get_last_story_id(cls, user_creator_id):
        last_id = 0
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5)
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
        last_id = 0
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5)
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
        stry = cls.get(story_id)
        result = {
            'story_id': story_id,
            'starting_loc' : stry.starting_loc,
            'inventory_size' : stry.inventory_size,
            'objects': StoryObject.obj_list_json(story_id),
            'events': StoryEvent.event_list_json(story_id),
            'locations': StoryLocation.loc_list_json(story_id)
        }
        return json.dumps(result)

    @classmethod
    def display_for_store(cls):
        result = []
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT story_id, story_title, story_author, story_synopsis, story_price, genre FROM `master_stories`"))
            query_data = cur.fetchall()
            for row in query_data:
                stry = cls.get(row['story_id'])
                stry_info = {'story_id': row['story_id'], 'story_title': row['story_title'],
                             'story_author': row['story_author'], 'story_synopsis': row['story_synopsis'],
                             'story_price': row['story_price'], 'genre': row['genre'],
                             'cover': stry.get_image_base64()}
                result.append(stry_info)
        storefront = {"stories": result}
        return json.dumps(storefront)

    @classmethod
    def destroy(cls, story_id):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(("DELETE FROM `master_stories` WHERE `story_id` = %s"), (story_id))
            conn.commit()
        conn.close()

    @classmethod
    def story_shares_by_uid(cls, uid):
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        story_list = []
        with conn.cursor() as cur:
            cur.execute(
                "SELECT story_id, story_title, user_creator_id FROM `master_stories` WHERE `story_id` IN (SELECT `story_id` FROM `story_shares` WHERE user_id = %s)", (uid))
            results = cur.fetchall()
            for row in results:
                auth = User.get(row['user_creator_id'])
                if auth is None:
                    author_name = ""
                else:
                    author_name = auth.username
                story_list.append(cls(row["story_id"], row["story_title"], author_name=author_name))
        conn.close()
        return story_list