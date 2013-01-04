# -*- coding: utf-8 -*-
"""
QUERY    Operations on queries
----------------------------------------
QUERY LIST 
QUERY SYNC < file.lql    # sync lql formated file
QUERY DELETE name 

"""
import sys, json, datetime, time, os, logging
import requests
import tornado
from tornado.httpclient import HTTPClient
from colorama import init as coloramainit
from termcolor import colored


#import config
from config import options
from .input import InputHelper

log = logging.getLogger("lytics")

def sync(cli):
    """
    Sync queries up, those that are kept in raw text files of .lql type 
    It assumes each query is seperated by at least one blank line
    """
    ih = InputHelper()
    ql = ih.parse()
    log.debug("Syncing %s Queries " % len(ql))
    
    if options.preview:
        for q in ql:
            print(q[0] + "\n" + q[1])
        return
    payload = []
    for q in ql:
        payload.append({'peg': q, "idx":0})
        #log.info(q)

    url = '%s/api/query?key=%s' % (options.api, options.key)
    log.warn("connecting to %s" % (url))
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    try:
        jsdata = json.loads(r.text)
        errors = []
        #print(json.dumps(jsdata, sort_keys=True, indent=2))
        if 'data' in jsdata:
            for qry in jsdata['data']:
                if "status" in qry and qry['status'] == "error":
                    errors.append(qry)
                elif 'peg' in qry:
                    print colored(qry['peg'] + "\n\n", 'green')
            for err in errors:
                print colored("FAILED TO PARSE\n" + qry['peg'] + "\n\n", 'red')
        else:
            print(json.dumps(jsdata, sort_keys=True, indent=2))
    except Exception, e:
        if options.traceback:
            raise
        log.error(e)
        
