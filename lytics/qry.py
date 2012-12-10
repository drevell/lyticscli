# -*- coding: utf-8 -*-
import sys, json, datetime, time, os, logging
import requests
import tornado
from tornado.options import options
from tornado.httpclient import HTTPClient

import config

log = logging.getLogger("lytics")

def syncq(cli, name):
    """
    Sync a raw text query file
    """
    base = os.getcwd()
    file = os.path.abspath("%s/%s" % (base,name))
    if len(options.key) < 10:
        log.error("MUST HAVE KEY key=%s" % (options.key))
        return
    #print("opening query file %s" % file)
    try:
        qf = open(file, 'r')
        ql = []
        txt = ""
        inComment = False
        for line in qf:
            #line = line.strip()
            #log.info(line)
            if len(line) > 1 and line[0:2] == "/*":
                inComment = True
                txt += line
            elif len(line) > 1 and line[0:2] == "*/":
                inComment = False
                txt += line
            elif len(line) > 0 and line[0] == "#":
                pass
            elif len(line) > 1 or inComment:
                txt += " " + line
            else:
                if len(txt) > 3:
                    ql.append(txt.strip())
                    txt = ""
        if len(txt) > 3:
            ql.append(txt)
        log.info(len(ql))
        #log.warn(ql)
        url = '%s/api/query?key=%s' % (options.api, options.key)
        log.warn("connecting to %s" % (url))
        payload = []
        for q in ql:
            payload.append({'peg': q, "idx":0})
            #log.info(q)
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        try:
            jsdata = json.loads(r.text)
            print(json.dumps(jsdata, sort_keys=True, indent=2))
        except Exception, e:
            log.error(e)
        

    except Exception, e:
        log.error(e)