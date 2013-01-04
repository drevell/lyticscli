# -*- coding: utf-8 -*-
import sys, os, logging


class InputHelper(object):
    "Stdin iterator for parsing contents"
    def __init__(self,*args,**kwargs):
        pass

    def parse(self,cb=None):
        """
        Parse input into seperate entities defined by new lines
        """
        ql = []
        txt = ""
        comment = ""
        inComment = False
        done = False
        def handle_row():
            if len(txt) > 3:
                ql.append((comment, txt ))
                if cb is not None:
                    cb((comment,txt))
        while not done:
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                break

            if not line:
                break

            #line = line.strip()
            #print("comment='%s' txt='%s'" % (comment,txt))
            if len(line) > 1 and line[0:2] == "/*":
                inComment = True
                comment += line
            elif len(line) > 1 and line[0:2] == "*/":
                inComment = False
                comment += line
            elif len(line) > 0 and line[0] == "#":
                comment += line
            elif len(line) > 1 and line[0:2] == "--":
                inComment = False
                comment += line
            elif len(line) > 1 and inComment:
                comment += line
            elif len(line) == 0 and inComment:
                comment += line
            elif len(line) > 1:
                txt += line
            else:
                # empty line is a seperator, mark as new query
                handle_row()
                txt = ""
                comment = ""

        handle_row()

        return ql





