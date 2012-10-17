# -*- coding: utf-8 -*-
import signal

_signames = dict((getattr(signal, signame), signame) \
                    for signame in dir(signal) \
                    if signame.startswith('SIG') and '_' not in signame)


def signal_name(signum):
    # Hackety-hack-hack: is there really no better way to reverse lookup the
    # signal name?  If you read this and know a way: please provide a patch :)
    try:
        return _signames[signum]
    except KeyError:
        return 'SIG_UNKNOWN'