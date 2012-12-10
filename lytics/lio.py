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
import requests
import tornado
from tornado import database
from tornado.options import options, define
from tornado.httpclient import HTTPClient

import config
import csvupload
import qry
import db


define("api",default="http://api.lytics.io",type=str,help="api url")
define("key",default="",type=str,help="Lytics.io api access token key for api (mandatory) or use LIOKEY env")
define("aid",default="",type=str,help="Lytics.io account id (mandatory) or use LIOAID env ")
define("dbhost",default="localhost",type=str,help="mysql db host")
define("db",default="test",type=str,help="db name to connect to")
define("config",default=".lytics",type=str,help="config file")
define("stream",default="default",type=str,help="Stream to send this data to")
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
    aid = os.environ["LIOAID"]
    if len(aid) > 0:
        options.aid = aid
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

#console.grab_console()
config.openConfig()



class clcmd(object):

    def valid(self):
        ret = True
        if len(options.key) < 10:
            log.error("MUST HAVE KEY key=%s" % (options.key))
            ret = False
        elif len(options.api) < 4:
            log.error("MUST HAVE API api=%s" % (options.api))
            ret = False
        #elif len(options.aid) < 1:
        #    log.error("MUST HAVE AID aid=%s" % (options.aid))
        #    ret = False
        return ret

    def help(self):
        "print help documentation"
        options.print_help()
        print __doc__
        for p in dir(self):
            if p[:1] != "_":
                print("%s  %s" % (p,getattr(self,p).__doc__ or ""))

    def http(self,file):
        """
        test out the http 
        """
        pass 

    def syncq(self,file):
        """
        Sync a raw text query file:

            lytics syncq qry.txt
        """
        if self.valid():
            qry.syncq(self, file)

    def csv(self,file):
        """
        Read a csv file and upload to lytics:

            lytics csv file.csv

            # optional stream name
            lytics --stream=streamName csv file.csv 
        """
        csvupload.csvupload(self, file)

    def showconfig(self):
        "Show the config settings"
        for n in options:
            print "%s=%s" % (n,options[n].value())

    def hello(self):
        print "hello"

    def setconfig(self,name,value):
        """
        Set a configuration setting for given parameter:

            lytics setconfig name value
        """
        # write out config file
        config.setConfig(name,value)

    def sendjson(self,rawdata):
        """
        sends the data to collection servers via http
        """
        http = HTTPClient()
        url = ""
        if len(options.aid) > 0:
            url = options.api +"/c/%s/%s" % (options.aid, options.stream)
        elif len(options.key) > 0:
            url = options.api +"/c/%s/%s" % (options.key, options.stream)
        data = json.dumps(rawdata)
        log.debug(url)
        #log.debug(data)
        response = http.fetch(url, 
            method="POST", body=data, headers={'user-agent':APIAGENT},
            request_timeout=60,connect_timeout=60)
        print response
    
    def db(self,username,pwd=""):
        """
        read info from a database table and send to lio.   

        lytics --dbhost=localhost --db=mydbname --aid=123456 --key=mysecret db root rootpwd
        """
        if self.valid():
            db.senddb(self,username,pwd)
    
    def collect(self):
        """posts arbitrary data for collection (json or name/value)

        open this as a process in your app and start writing to it using stdout

        tail -F myfile.log | python lytics --aid=123456 --key=mysecret collect
        """
        if len(options.key) < 1 or len(options.aid) < 1:
            options.print_help()
            raise Error('Aid and key are required')
        #print("""You can start sending data by typing it in, format as QS nv pairs, or valid json""")
        http = HTTPClient()
        jsondata = None
        line = ""
        data = None
        url = options.api  + "/c/%s/%s?key=%s" % (options.aid, options.stream, options.key)

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
                data = line
                url = options.api + "/c/%s/%s?key=" % (options.aid,options.stream)
            
            log.debug("SENDING '%s'" % (data))
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

        











































