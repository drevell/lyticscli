# -*- coding: utf-8 -*-
import sys, json, datetime, time, os, logging
import requests
import tornado
from tornado.options import options
from tornado.httpclient import HTTPClient
from tornado import database

import config

BATCH_SIZE = 50

log = logging.getLogger("lytics")

def senddb(cli ,username,pwd):
    """
    Sync query from db
    """
    db = database.Connection(options.dbhost, options.db, user=username, password=pwd)
    rows = []
    queries = []
    #sql = "SELECT email, id as user_id FROM user"
    #sql = "SELECT email, id as user_id FROM user where last_update > CURRENT_TIMESTAMP - 10000"
    # for each line from stdin
    done = False
    sqlstr = ''
    while not done:
        try:
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            break

        if not line:
            break

        line = line.strip()
        #print line
        if line[:1] == ";":
            sqlstr = sqlstr + " " + line
            #print("SQLSTR = %s" % (sqlstr))
            queries.append(sqlstr)
            sqlstr = ''
        elif len(line) > 2:
            sqlstr += " " + line
        else:
            log.debug("ELSE %s" % (line))
    if len(sqlstr) > 0 :
        queries.append(sqlstr)

    #print queries
    for sql in queries:
        for row in db.query(sql):
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