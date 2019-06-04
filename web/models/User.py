import pymysql
import pymysql.cursors
import sys

import random
import hashlib
import binascii

from datetime import date

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
    user_id = ""

    REGION = 'us-east-2b'

    rds_host = "audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com"
    name = "AA_admin"
    rds_password = "z9QC3pvQ"
    db_name = "audio_adventures_dev"
    
    def __init__(self, username_input = "", password_input = "", password_salt_input = "", email_input = "", first_name_input = "", last_name_input = "", 
                gender_input = 0, country_of_origin_input = 1, profession_input = "", disabilities_input = 0, date_of_birth_input = date.min, language = 0):
        
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

    #Generates a salt for storing passwords
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
        conn = pymysql.connect(self.rds_host, user=self.name, passwd = self.rds_password, db= self.db_name, connect_timeout=5, cursorclass = pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            password_input = self.password
            self.password = self.encrypt_password(password_input, self.password_salt)
            cur.execute("INSERT INTO users(username, password, password_salt, email_address, profession, gender, country_of_origin, disabilities, language_id, first_name, last_name, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (self.username, self.password, self.password_salt, self.email, 
            self.profession, self.gender, self.country_of_origin, self.disabilities, self.language_id, self.first_name, self.last_name, self.date_of_birth))
            conn.commit()
            cur.execute("SELECT `user_id` FROM users WHERE `username` = %s", (self.username))
            result = cur.fetchone()
            raw_user_id = result['user_id']
            self.user_id = str(raw_user_id).encode('utf-8').decode('utf-8')
        conn.close()

    def get_id(self):
        return self.user_id


    def get(self, user_id):
        int_user_id = int(user_id)
        conn = pymysql.connect(self.rds_host, user=self.name, passwd = self.rds_password, db= self.db_name, connect_timeout=5, cursorclass = pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute(("SELECT `user_id` FROM users WHERE `user_id` = %s"), (int_user_id))
        result = cur.fetchone()
        int_user_id = result['user_id']
        if(int_user_id is None):
            return None
        cur.execute(("SELECT `username`, `password`, `password_salt` FROM users WHERE `user_id` = %s"), (int_user_id))
        result = cur.fetchone()
        result = User(result['username'], result['password'], result['password_salt'])
        conn.close()
        return result

    def authenticate(self, password_input):
        result = self.encrypt_password(password_input, self.password_salt)
        if result == self.password:
            self.is_authenticated = True
            self.is_anonymous = False
        else:
            self.is_authenticated = False
            self.is_anonymous = True
        
        return self.is_authenticated
