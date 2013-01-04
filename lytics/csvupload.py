# -*- coding: utf-8 -*-
"""
CSV   [file]    Read a csv file and upload to lytics:

                lytics csv file.csv

                # optional stream name
                lytics --stream=streamName csv file.csv 
"""
import sys, json, datetime, time, urllib, os, logging, csv
import requests
from config import options


log = logging.getLogger("lytics")

def csvupload(cli, name):
    """
    Sync a raw text csv file
    """
    if len(options.key) < 10 or len(options.api) < 4:
        log.error("MUST HAVE KEY and API key=%s, api=%s" % (options.key,options.api))
        return
    filePath = os.path.normpath(name)
    csvdata = csv.reader(open(filePath, 'r'), delimiter=',')
    cols = csvdata.next()
    jdata = []
    for row in csvdata:
        rd, ct = {}, 0
        for col in cols:
            rd[col] = row[ct]
            ct += 1
        log.debug(rd)
        jdata.append(rd)

    url = '%s/c/%s/%s' % (options.api, options.key, options.stream)

    log.warn("connecting to %s rowct=%d" % (url,len(jdata)))
    r = requests.post(url, data=json.dumps(jdata), 
        headers={'content-type': 'application/json'})
    print(dir(r))
    log.info("Status =%s" % (r.status_code))
        
    try:
        pass
    except Exception, e:
        log.error(e)