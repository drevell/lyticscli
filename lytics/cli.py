#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The main entry point. Invoke as `lytics' or `python -m lytics'.
"""
import sys
from .lio import main


if __name__ == '__main__':
    sys.exit(main())