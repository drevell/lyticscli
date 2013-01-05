# -*- coding: utf-8 -*-
import sys
import json
import datetime
import time 
import random
import urllib
import os 
import logging
#from argparse import FileType, OPTIONAL, ZERO_OR_MORE, SUPPRESS
import requests
from colorama import init as coloramainit
from termcolor import colored

import config
import csvupload
import query
import db
import collect 
import httpapi

import httpiecolor
from httpapi import build_url
from pretty import pprint_table


log = logging.getLogger("lytics")
APIAGENT = "LioCLI"
BATCH_SIZE = 50

coloramainit()

modules = {"query":query,"db":db,"csv":csvupload,"api":httpapi,"collect":collect}
#module_keys = ["query","db","csv", "api","collect"]


def get_doc(method=None):
    "Get doc for a specific module or all"
    if not method:
        return '\n'.join([modules[n].__doc__ for n in module_keys])
    else:
        if type(method) == list:
            if len(method) == 1:
                method = method[0]
            else:
                method = "invalid"
        if method in modules:
            return modules[method].__doc__.strip()
    return ""

def _(text):
    """Normalize whitespace."""
    return ' '.join(text.strip().split())

class LioCommands(object):

    def __init__(self, args):
        "init"
        config.options.load(args)  # config.options = config.LioOptions(args)
        self.args = args 

    def _error(self,msg):
        print("lytics error:  %s" % msg)

    def _arg(self,pos):
        if type(self.args.args) == list:
            if len(self.args.args) > pos:
                #log.debug(self.args.args)
                return self.args.args[pos]
        return ""

    def valid(self, argsreq=0):
        if len(self.args.api) < 2:
            self._error("Requires Api and is missing")
            return False
        if len(self.args.key) < 10:
            self._error("Requires apikey and is missing")
            return False
        if argsreq > 0:
            if len(self.args.args) < argsreq:
                doc = get_doc(self.args.method)
                self._error("%s requires additional arg and is missing\n\n%s" % (
                    self.args.method, doc))
                return False
        return True

    def api(self):
        """call arbitrary api
        """
        if not self.valid():
            return
        url = self._arg(0)
        if len(url) < 1:
            log.error("Requires url arg:    lytics api account  [user,account,query,meta etc]")
            return
        url = build_url(url)
        log.debug(url)
        httpiecolor.console_response(httpapi.doapi(url))

    def user(self):
        """
        Get list of Users or a specific one
        """
        if not self.valid(1):
            return
        method = self._arg(0).lower()

        uid = self._arg(0)
        url = "" 
        if len(uid) == 0 :
            url = build_url("user")
        else:
            url = build_url("user/" + uid)
        log.debug(url)
        if self.args.format == 'json':
            httpiecolor.console_response(httpapi.doapi(url))
        else:
            resp = httpapi.doapi(url)
            if resp.status_code < 400:
                data = json.loads(resp.text)
                out = [['Name', "Email","Roles"]]
                if "data" in data:
                    if isinstance(data["data"],dict):
                        httpiecolor.console_response(resp)
                    else:
                        for u in data["data"]:
                            roles = ""
                            if "roles" in u and type(u["roles"]) == list:
                                roles = ",".join(u['roles'])
                            out.append([u["name"],u["email"],roles])
                        print("")
                        pprint_table(sys.stdout,out)

    def query(self):
        """Query Ops"""
        if not self.valid(1):
            return
        method = self._arg(0)
        if method == "sync":
            query.sync(self)
        elif method == "list":
            query.list(self)

    def csv(self):
        """
        Read a csv file and upload to lytics:

            lytics csv file.csv

            # optional stream name
            lytics --stream=streamName csv file.csv 
        """
        fa = self._arg(0)
        if len(fa) < 2:
            log.error("no file supplied")
        csvupload.csvupload(self, fa)

    def showconfig(self):
        "Show the config settings"
        print(config.options.help())

    def sendjson(self,rawdata):
        """
        sends the data to collection servers via http
        """
        url = ""
        aid = self.args.aid 
        if len(aid) == 0:
            aid = self.args.key
        if len(self.args.stream) > 0:
            url = self.args.api +"/c/%s/%s" % (aid, self.args.stream)
        else :
            url = self.args.api +"/c/%s" % (aid)

        log.debug(url)
        if self.args.preview:
            print("would have sent %s data=\n%s" % (url, rawdata))
            return 
        if self.args.format == 'json':
            httpiecolor.console_response(httpapi.doapi(url, data=rawdata))
        else:
            httpiecolor.console_response(httpapi.doapi(url, data=rawdata))
        #print response
    
    def db(self):
        """
        read info from a database table and send to lio.   
        """
        if not self.valid(1):
            return
        method = self._arg(0).lower()
        if method == "upload":
            db.senddb(self)
    
    def collect(self):
        """posts arbitrary data for collection"""
        if not self.valid(0):
            return
        collect.stdin(self)
    














































