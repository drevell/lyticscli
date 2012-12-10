# -*- coding: utf-8 -*-
import sys, os, logging
from tornado.options import options

log = logging.getLogger("lytics")

conf_file = None
config_lines = []

def setConfig(name,value):
    """
    Given a name/value pair, sets or updates in config file 
    (.lytics of cur dir) as well as (.env of current dir) 
    """
    lines, found = [], False
    log.debug("SETCONFIG   %s:%s" %(name,value))
    def setConfLine():
        if not name in options:
            options.print_help()
            raise Error('Unrecognized command line option: %r' % name)
        option = options.get(name) #_options[name]
        if option:
            option.parse(value)
            if option.type == str:
                lines.append(name + '="' + str(value) + '"')
            elif options.type == bool:
                val2 = value.lower()
                if val2 in ['true', '1', 't', 'y', 'yes', 'True']:
                    lines.append(name + '=True')
                else:
                    lines.append(name + '=False')


    for line in config_lines:
        #log.info(line)
        if len(line) > 1:
            if line.startswith(name + "="):
                found = True
                setConfLine()
            else:
                lines.append(line)
    if not found:
        setConfLine()
    f = open(conf_file, 'w')
    f.write("\n".join(lines))
    f.close()
    #log.debug("".join(lines))
    openConfig()


def openConfig(name=".lytics"):
    global config_lines
    global conf_file
    conf_file = os.path.expanduser("%s/%s" % (os.getcwd(),name))
    #log.debug("opening conf file %s" % conf_file)
    try:
        config_lines = []
        f = open(conf_file, 'r')
        #log.info("OPENED %s for reading" %(conf_file))
        for line in f:
            config_lines.append(line)
        #log.debug("".join(config_lines))
        f.close()
    except Exception, e:
        f = open(conf_file, 'w')
        config_lines = ["#Lytics Config File"]
        f.write("#Lytics Config File")
        f.close()
        log.error("Creating Config file %s" % (conf_file))


