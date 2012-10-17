lytics CLI Tool
==================

Command line tool for sending data to Lytics.io and managing the api (queries/analysis) etc.

Data collection
=======================
This allows collection of 2 general types of data

1.  Event data:  a user visits, views, clicks etc type data

2.  Entity Data:   Information about a user, company, etc.

examples:
    
    # start an interactive command line to type in name=value pairs for collection
    # sends one request per line
    lytics --aid=123456  --key=myapikey collect

    # tail a file, sending each new line as a lytics.io data point
    tail -F myfile.log | lytics --aid=123456 --key=mysecret collect

    # write to stdout
    myscript.py | lytics --aid=123456 --key=mysecret collect

    # or the same
    lytics --aid=123456 --key=mysecret collect < myscript.py 

    # read from a database table and send one entry per row
    lytics db username pwd < myscript.sql 


Management
=======================
Manage your queries (analysis)

    
    # sync the qry.txt files to the api
    lytics setconfig key yourkey
    lytics syncq qry.txt


Configuration Options
=======================
You can pass parameters such as *aid* (accountid) or *key* (apikey) on the command line or create a configuration file for them by using the **setconfig** command

Creates a *.lytics* file in current folder


    # Set the aid setting permanently to 123456 in current folder
    lytics setconfig aid 123456

    lytics setconfig key myapikey

Also, there are two environment varials that can be used
    
    LIOAID # aid

    LIOKEY # api key
