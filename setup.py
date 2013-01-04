# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

version = '0.0.7'

setup(name='lytics',
      version=version,
      description="Python CLI for Lytics.io api",
      long_description="""
Lytics.io CLI Tools
===========================

`Lytics.io <http://lytics.io>`_ is an analytics service.  This tool provides
command line access to uploading data, syncing queries, etc.   See 
http://developer.lytics.io/doc#cli

Download and Installation
-------------------------

::

  > pip install lytics

""",
    classifiers=["Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ], 
    keywords='python',
    author='Aaron Raddon',
    author_email='aaron@lytics.io',
    url='http://github.com/lytics/lyticscli',
    install_requires=["nose>=0.10.4","requests>=0.10.1","tornado",
       "httpie>=0.3","colorama","termcolor"],
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples']),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'lytics = lytics.cli:main',
        ],
    },
)
