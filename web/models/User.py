import pymysql
import pymysql.cursors
import sys

import web.config as config
from . import *

import random
import hashlib
import binascii

from datetime import datetime, date

from flask_login import UserMixin

import json


class User(UserMixin):
    username = ""
    password = ""
    password_salt = ""
    email = ""
    gender = 0
    country_of_origin = 0
    profession = ""
    disabilities = 0
    company_id = 0
    is_consumer = 0
    is_contributor = 0
    first_name = ""
    last_name = ""
    date_of_birth = date.min
    language_id = 0
    is_authenticated = False
    is_active = True
    is_anonymous = True
    user_id = 0
    is_editor = 0
    last_login_date = None

    REGION = 'us-east-2b'

    def __init__(self, username_input="", password_input="", password_salt_input="", email_input="", first_name_input="", last_name_input="",
                 gender_input=0, country_of_origin_input=1, profession_input="", disabilities_input=0, 
                 date_of_birth_input=date.min, language=0, user_type=0, user_id=0, last_login_date = 0):
        self.username = username_input
        if password_salt_input == "":
            self.password_salt = self.generate_password_salt()
        else:
            self.password_salt = password_salt_input
        self.password = password_input
        self.email = email_input
        self.gender = gender_input
        self.country_of_origin = country_of_origin_input
        self.first_name = first_name_input
        self.last_name = last_name_input
        self.gender = gender_input
        self.country_of_origin = country_of_origin_input
        self.profession = profession_input
        self.disabilities = disabilities_input
        self.date_of_birth = date_of_birth_input
        self.language_id = language
        self.user_type = user_type
        self.is_admin = False
        self.is_content_editor = False
        self.is_copy_editor = False
        if user_type & 0x04 == 0x04:
            self.is_admin = True
        if user_type & 0x02 == 0x02:
            self.is_content_editor = True
        if user_type & 0x01 == 0x01:
            self.is_copy_editor = True
        if user_id != 0:
            self.user_id = user_id
        self.last_login_date = last_login_date
    
    @staticmethod
    def generate_password_salt():
        salt_source = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz123456789'
        salt = random.choice(salt_source)
        for i in range(15):
            salt += random.choice(salt_source)
        return salt

    @staticmethod
    def encrypt_password(raw_password, password_salt):
        password = raw_password + password_salt
        encrypted_password = hashlib.sha256(password.encode()).digest()
        password_hex_string = binascii.b2a_hex(encrypted_password)
        return password_hex_string.decode('utf-8')

    def add_to_server(self):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            password_input = self.password
            self.password = self.encrypt_password(
                password_input, self.password_salt)
            cur.execute(("SELECT * FROM users WHERE username = %s"),
                        (self.username))
            results = cur.fetchone()
            if results:
                conn.close()
                return False
            self.user_type = 0
            if self.is_admin:
                self.user_type += 4
            if self.is_content_editor:
                self.user_type += 2
            if self.is_copy_editor:
                self.user_type += 1
            cur.execute("INSERT INTO users(username, password, password_salt, email_address, profession, gender, country_of_origin, disabilities, language_id, first_name, last_name, date_of_birth, user_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (self.username, self.password, self.password_salt, self.email,
                         self.profession, self.gender, self.country_of_origin, self.disabilities, self.language_id, self.first_name, self.last_name, self.date_of_birth, self.user_type))
            conn.commit()
            cur.execute(
                "SELECT `user_id` FROM users WHERE `username` = %s", (self.username))
            result = cur.fetchone()
            self.user_id = result['user_id']
        conn.close()
        return True

    def get_id(self):
        return self.user_id

    @classmethod
    def get(cls, user_id):
        if user_id == 0 or user_id == '':
            return None
        int_user_id = int(user_id)
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute(
            ("SELECT `username`, `password`, `password_salt`, `user_type`, `last_login_date` FROM users WHERE `user_id` = %s"), (int_user_id))
        result = cur.fetchone()
        if result['username'] is None:
            return None
        result = User(result['username'], result['password'],
                      result['password_salt'], user_type=result['user_type'], last_login_date=result['last_login_date'])
        conn.close()
        return result

    @classmethod
    def get_user_count(cls):
        last_id = 0
        conn = pymysql.connect(
            config.db_host, user=config.db_user, passwd=config.db_password, db=config.db_name, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT COUNT(user_id) FROM users"))
            result = cur.fetchone()
            last_id = result[0]
        conn.close()
        return last_id

    def authenticate(self, password_input):
        if self.password == self.encrypt_password(password_input, self.password_salt):
            self.is_authenticated = True
        else:
            self.is_authenticated = False
        return self.is_authenticated

    @classmethod
    def list_of_all_users(cls):
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        result = []
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT `username`, `user_type`, `user_id` FROM `users`"))
            query_data = cur.fetchall()
            for row in query_data:
                result.append(
                    cls(row['username'], user_type=row['user_type'], user_id=row['user_id']))
        return result

    def update_admin(self):
        self.user_type = 0
        if self.is_admin:
            self.user_type += 4
        if self.is_content_editor:
            self.user_type += 2
        if self.is_copy_editor:
            self.user_type += 1
        conn = pymysql.connect(config.db_host, user=config.db_user, passwd=config.db_password,
                               db=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            cur.execute(("UPDATE `users` SET username = %s, user_type = %s WHERE user_id = %s"),
                        (self.username, self.user_type, self.user_id))
            conn.commit()
        conn.close()

    def get_last_login_date(self):
        return self.last_login_date

    def user_profile_info(self):
        result = {
            'username' : self.username,
            'email' : self.email,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'profile_picture' : "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"
        }
        return json.dumps(result)