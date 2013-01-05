# -*- coding: utf-8 -*-
"""

DB    Operations on local db's to upload/sync data
----------------------------------------------------
DB [OPTIONS] UPLOAD < file.sql # set of sql queries to run against db and upload 

lytics --dbhost=localhost \\
                --db=mydbname \\
                --dbuser=root \\
                --dbpwd=rootpwd \\
            db upload < upload.sql

"""
import sys, json, datetime, time, os, logging
import requests
from tornado import database

from config import options
from .input import InputHelper

BATCH_SIZE = 50

log = logging.getLogger("lytics")


def senddb(cli):
    """
    Sync query from db
    """

    ih = InputHelper()
    ql = ih.parse()

    db = database.Connection(options.dbhost, options.db, user=options.dbuser, password=options.dbpwd)

    rows = []
    for query in ql:
        for row in db.query(query[1]):
            newrow = {}
            for col, colval in row.iteritems():
                #print col, colval
                if type(colval) == datetime.datetime:
                    #print("is datetime %s" % (colval))
                    newrow[col] = time.mktime(colval.timetuple())
                else:
                    #print("type = %s" % (type(colval)))
                    newrow[col] = colval
            rows.append(newrow)
            if len(rows) > BATCH_SIZE :
                cli.sendjson(rows)
    
    if len(rows) > 0 :
        cli.sendjson(rows)