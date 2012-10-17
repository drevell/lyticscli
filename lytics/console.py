# -*- coding: utf-8 -*-
import sys, os, threading, logging 

import __builtin__

log = logging.getLogger("lytics")

_consoles = threading.local()


def setSignals():
    """Define new built-ins 'quit' and 'exit'.
    These are simply strings that display a hint on how to exit.

    """
    if os.sep == ':':
        eof = 'Cmd-Q'
    elif os.sep == '\\':
        eof = 'Ctrl-Z plus Return'
    else:
        eof = 'Ctrl-D (i.e. EOF)'

    class Quitter(object):
        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return 'Use %s() or %s to exit' % (self.name, eof)

        def __call__(self, code=None):
            # If executed with our interactive console, only raise the
            # SystemExit exception but don't close sys.stdout as we are
            # not the owner of it.

            if hasattr(_consoles, 'active'):
                raise SystemExit(code)

            # Shells like IDLE catch the SystemExit, but listen when their
            # stdin wrapper is closed.

            try:
                sys.stdin.close()
            except:
                pass
            raise SystemExit(code)

    __builtin__.quit = Quitter('quit')
    __builtin__.exit = Quitter('exit')

class ConsoleWrapper(object):
    def __init__(self, wrapped):
        self._instance = wrapped

    def flush(self):
        try:
            return self._instance.flush()
        except:
            log.error("can't flush")

    def write(self, data):
        try:
            return self._instance.write(data)
        except:
            log.error("can't write %s" % data)

    def writelines(self, data):
        try:
            return self._instance.writelines(data)
        except:
            log.error("can't writelines %s" % data)

def grab_console():
    "Grab the stdin/out console info"
    setSignals()

    sys.stdout = ConsoleWrapper(sys.stdout)
    sys.stderr = ConsoleWrapper(sys.stderr)
