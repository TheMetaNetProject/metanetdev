#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
.. module: add_jugments

run the case study sourcing pipeline from fetching documents -> creating final json


.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]\n

-q --queries          file with list of queries to issue
-s --start_point      what part of file to start from\n
-o --output           where to output urls to
-j --json             where to output json of urls
-r --result           where to output search results 1 per line to

"""

import json
import os
import re
import sys
import time
import urllib2
import urlparse

#from random import random
#from optparse import OptionParser
from time import sleep


# command line options
#parser = OptionParser()

#parser.add_option("-q", "--queries", dest="queries_filename", 
        #help="file with list of queries to issue")

#parser.add_option("-s", "--start", dest="start_point",
        #help="where to start in input file",default=0)

#parser.add_option("-o", "--output", dest="output_file",
        #help="what file to output links to")

#parser.add_option("-r", "--result_file", dest="result_file",
        #help="what file to output search results to",
        #default=None)

#parser.add_option("-j", "--json_file", dest="json_file",
        #help="what file to output json of results to",
        #default=None)

#(options,args) = parser.parse_args()

if __name__ =="__main__":
    from optparse import OptionParser
    #from yos.boss import ysearch
    from yahooboss import BossSearch
    consumer_key = "ADD YOUR CONSUMER KEY HERE"
    secret_key = "ADD YOUR SECRET KEY HERE"
    bs = BossSearch(consumer_key,secret_key)
    # command line options
    parser = OptionParser()

    parser.add_option("-q", "--queries", dest="queries_filename", 
            help="file with list of queries to issue")

    parser.add_option("-s", "--start", dest="start_point",
            help="where to start in input file",default=0)

    parser.add_option("-o", "--output", dest="output_file",
            help="what file to output links to")

    parser.add_option("-r", "--result_file", dest="result_file",
            help="what file to output search results to",
            default=None)

    parser.add_option("-j", "--json_file", dest="json_file",
            help="what file to output json of results to",
            default=None)

    (options,args) = parser.parse_args()
    # queries are stored one query per line in options.queries_filename
    # options.start_point is what line in input file to start with
    n = int(options.start_point)
    queries = file(options.queries_filename).read().split('\n')[n:-1]
    print queries
    # set up url opener
    
    # if json output is selected, make sure the file is ready
    # after each query, we're going to load the json, add the urls, and save the json
    if options.json_file:
        # see if there is already a json file present
        if os.path.isfile(options.json_file):
            try:
                # test that we can load whatever json is in the file
                overall_json = json.loads(file(options.json_file).read())
            except:
                # if there is an error exit, tell user to resolve file issue
                print "Error loading json file, please correct this issue before continuing!"
                print "Suggestion: You probably have a malformed file at this path, just delete it."
                sys.exit()
        else:
            # in this case which should be typical, there is no file there, make a blank overall json
            overall_json = {"urls": [], "query file": options.queries_filename,
                    "search engine": "yahoo"}
            json_output_file = file(options.json_file,"w")
            json_output_file.write(json.dumps(overall_json))
            json_output_file.close()
    # proceed through the queries
    queries_seen = 0
    for query in queries:
        # open up output file
        print "current query in file: "+str(int(options.start_point) + queries_seen)
        queries_seen += 1
        output_file = file(options.output_file,'a')
        if options.result_file:
            result_file = file(options.result_file,'a')
        else:
            result_file = None
        # keep track of number of queries processed so far
        #yahoo_results = ysearch.search(query,bucket="web", count=50,start=0,more={})
        yahoo_results = bs.search_web(query)
        overall_json = None
        if options.json_file:
            # there should be valid json in the json file path
            overall_json = json.loads(file(options.json_file).read())
        #for sl in yahoo_results['results']:
        for sl in yahoo_results:
            output_file.write('url:'+sl['url']+"\tquery:"+query+"\t0"+"\n")
            if result_file:
                result_json_string = json.dumps(sl)
                result_file.write(result_json_string+"\n")
                result_file.flush()
            if overall_json:
                result_dict = {'url': sl['url'] , 'title': sl['title'], 'snippet': sl['abstract'],
                        "query": query, "result": 0, "perspective": "unknown"}
                overall_json["urls"].append(result_dict)
        # write the results from this query to disk if json option selected
        if overall_json:
            # backup the json
            os.system('cp '+options.json_file+' '+options.json_file+'.backup')
            json_output_file = file(options.json_file,"w")
            json_output_file.write(json.dumps(overall_json))
            json_output_file.close()
        output_file.close()
        if result_file:
            result_file.close()
