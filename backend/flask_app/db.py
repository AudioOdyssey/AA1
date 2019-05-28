import mysql.connector

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if "db" not in g:
        mydb = mysql.connector.connect(
            host="audio-adventures-dev.cjzkxyqaaqif.us-east-2.rds.amazonaws.com",
            user="AA_admin",
            passwd="z9QC3pvQ"
        )
        g.db.row_factory = mysql.row_factory

    mycursor = mydb.cursor()

