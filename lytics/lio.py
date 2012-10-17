# -*- coding: utf-8 -*-
"""
Command line tool for sending data to Lytics.io.  
See doc http://developer.lytics.io/doc


Data collection
=======================
This allows collection of 2 general types of data

1.  Event data:  a user visits, views, clicks etc type data

2.  Entity Data:   Information about a user, company, etc.

example::
    
    # start an interactive command line to type in name=value pairs for collection
    lytics --aid=123456  --key=myapikey collect
    >myname=value&name2=value2

    # tail a file, sending each new entry written
    tail -F myfile.log | lytics --aid=123456 --key=mysecret collect

    # write to stdout
    myscript.py | lytics --aid=123456 --key=mysecret collect

    # read from a database table

"""
import re, sys, json, datetime, time, random, urllib, os, logging
from threading import Thread
from pprint import pprint as pp
import requests
import tornado
from tornado import ioloop
from tornado import database
from tornado.options import options, define
from tornado.httpclient import HTTPClient

import console
import config


define("api",default="http://api.lytics.io",type=str,help="api url")
define("key",default="xxxx",type=str,help="Lytics.io api access token key for api")
define("aid",default="xxxx",type=str,help="Lytics.io account id")
define("dbhost",default="localhost",type=str,help="mysql db host")
define("db",default="rootpwd",type=str,help="db name")
define("config",default=".lytics",type=str,help="config file")
define("v",default=False,type=bool,help="verbose?")


tornado.options.parse_command_line()
if options.config != "":
    try:
        if options.config == ".lytics":
            conf_file = os.path.expanduser("%s/%s" % (os.getcwd(),options.config))
            tornado.options.parse_config_file(conf_file)
        else:
            tornado.options.parse_config_file(options.config)
    except:
        pass
    tornado.options.parse_command_line()

try:
    apikey = os.environ["LIOKEY"]
    if len(apikey) > 0:
        options.key = apikey
except:
    pass

try:
    apistr = os.environ["LIOAPI"]
    if len(apistr) > 0:
        #options.api = "http://localhost:8133"
        options.api = apistr
except:
    pass


log = logging.getLogger("lytics")
APIAGENT = "LioCLI"
BATCH_SIZE = 50

console.grab_console()
config.openConfig()



def syncq(name):
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
        for line in qf:
            #line = line.replace("\n","")
            #log.info(line)
            if len(line) > 0 and line[0] == "#":
                pass
            elif len(line) > 1:
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
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        try:
            jsdata = json.loads(r.text)
            print(json.dumps(jsdta, sort_keys=True, indent=2))
        except Exception, e:
            log.error(e)
        

    except Exception, e:
        log.error(e)

    

class clcmd(object):

    def help(self):
        "print help documentation"
        options.print_help()
        print __doc__
        for p in dir(self):
            if p[:1] != "_":
                print("%s  %s" % (p,getattr(self,p).__doc__ or ""))

    def syncq(self,file):
        """
        Sync a raw text query file:

            lytics --key="yourkey" syncq file.txt
        """
        syncq(file)

    def showconfig(self):
        for n in options:
            print "%s=%s" % (n,options[n].value())

    def hello(self):
        print "hello"

    def setconfig(self,name,value):
        """
        Set a configuration setting:

            lytics setconfig name value
        """
        # write out config file
        config.setConfig(name,value)

    def sendjson(self,command,rawdata):
        """
        sends the data to collection servers via http

        this is an event 
        """
        http = HTTPClient()
        url = options.api_url +"/" + command +"/%s?key=%s" % (options.aid,options.token)
        data = json.dumps(rawdata)
        #print(url)
        #print(data)
        response = http.fetch(url, 
            method="POST", body=data, headers={'user-agent':APIAGENT},
            request_timeout=60,connect_timeout=60)
        print response
    
    def db(self,username,pwd):
        """
        read info from a database table and send to lio.   

        lytics --dbhost=localhost db=mydbname --aid=123456 --token=mysecret db root rootpwd
        """
        db = database.Connection(options.dbhost, options.db, user=username, password=pwd)
        rows = []
        sql = "SELECT email, id as user_id FROM user"
        #sql = "SELECT email, id as user_id FROM user where last_update > CURRENT_TIMESTAMP - 10000"
        for row in db.query(sql):
            rows.append(row)
            if len(rows) > BATCH_SIZE :
                self.sendjson("cd", rows)
        
        if len(rows) > 0 :
            self.sendjson("cd", rows)

    def collect(self):
        """posts arbitrary data for collection (json or name/value)

        open this as a process in your app and start writing to it using stdout

        tail -F myfile.log | python lytics --aid=123456 --key=mysecret collect
        """
        if len(options.key) < 1 or len(options.aid) < 1:
            options.print_help()
            raise Error('Aid and key are required')
        print("""You can start sending data by typing it in, format as QS nv pairs, or valid json""")
        http = HTTPClient()
        jsondata = None
        line = ""
        data = None
        url = options.api + "/c/%s?key=%s" % (options.aid, options.key)

        # for each line from stdin
        while 1:
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                break

            if not line:
                break

            jsondata = None
            line = line.strip()
            if line[:1] == "{":
                line = "[" + line + "]"
            if line[:1] == "[":
                #jsondata = json.loads(line)
                #data = urllib.urlencode(jsondata)
                data = line
            else:
                # nv pairs:  p.name=nodejs&p.category=node.js&p.id=123
                data = line
                url = options.api + "/c/%s?key=" % options.aid
            
            #print(url)
            print("'%s'" % (data))
            response = http.fetch(url, 
                method="POST", body=data, headers={'user-agent':APIAGENT},
                request_timeout=60,connect_timeout=60)
            print response.body
    

def main():
    "Main Entry Point for CLI"
    args = [a for a in sys.argv if a[0:1] != "-"][1:]
    cl = clcmd()
    cmd = "help"
    
    if len(args) > 0:
        cmd = args[0]
    
    if len(args) > 2 and hasattr(cl,cmd):
        getattr(cl,cmd)(args[1],args[2])
    elif len(args) > 1 and hasattr(cl,cmd):
        getattr(cl,cmd)(args[1])
    elif cmd in dir():
        getattr(cl,cmd)()
    elif getattr(cl,cmd):
        getattr(cl,cmd)()
    else:
        cl.help()

if __name__ == "__main__":
    main()

        











































