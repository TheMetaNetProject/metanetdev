#!/usr/bin/python

"""
.. module: run_pipeline

run the case study sourcing pipeline from fetching documents -> creating final json

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]\n

-s --start_point      what part of pipeline to start from\n
-n --name             name of document bundle e.g. immigration_01_15\n
-p --path             path of data dir to store results\n

"""

import collections
import commands
import os
import re
import string
import time
import urllib
import urllib2
import urlparse

#from random import random
#from optparse import OptionParser
from time import sleep

# example naming convention

# given name is yahoo_gun_control

# Step 1: urls file
# case_study_sourcing/data/urls/yahoo_gun_control_urls.txt

# Step 2: html directory
# case_study_sourcing/data/html/yahoo_gun_control

# Step 3: document .txt file
# case_study_sourcing/data/documents/yahoo_gun_control.txt

# Step 4: pre sentence boundary working dir
# case_study_sourcing/data/pre_sbd/yahoo_gun_control

# Step 5: whole and split JSON
# case_study_sourcing/data/json/yahoo_gun_control.json
# case_study_sourcing/data/json/yahoo_gun_control

# command line options
#parser = OptionParser()

#parser.add_option("-s", "--start_point", dest="start_point",
        #help="which part of the pipeline to start at")

#parser.add_option("-n", "--name", dest="name",
        #help="name of this document set")

#parser.add_option("-p", "--path", dest="path",
        #help="path of data directory for intermediate steps")

#(options,args) = parser.parse_args()

# the steps, this is a work in progress so for now we assume you at least have links file

steps_array = ['fetch_documents', 'extract_natural_text', 'process_documents', 'run_sentence_splitting', 'build_mn_json',
               'split_apart_json']

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    parser.add_option("-s", "--start_point", dest="start_point",
            help="which part of the pipeline to start at")

    parser.add_option("-n", "--name", dest="name",
            help="name of this document set")

    parser.add_option("-p", "--path", dest="path",
            help="path of data directory for intermediate steps")

    (options,args) = parser.parse_args()
    step_index = steps_array.index(options.start_point)

    # first get documents from web
    if step_index <= 0:
        #links_file = options.path + "/urls/"+options.name+"_urls.txt"
        links_file = options.path + "/urls/"+options.name+".json"
        html_directory = options.path + "/html/"+options.name
        print "---"
        print "Fetching html from the web..."
        print "using link file: "+links_file
        print "outputting to: "+html_directory
        # issue command
        print "./fetch_documents.py -l %s -d %s" % (links_file,html_directory)
        os.system("./fetch_documents.py -l %s -d %s" % (links_file,html_directory))
        print "Done fetching documents..."

    # second extract natural text from html
    if step_index <= 1:
        html_directory = options.path + "/html/"+options.name
        documents_file = options.path + "/documents/"+options.name+".txt"
        json_file = options.path + "/documents/"+options.name+".json"
        print "---"
        print "Extracting natural text with boilerpipe..."
        print "using html directory "+html_directory
        print "outputting to "+documents_file
        # issue command
        print "./extract_natural_text.py -d %s -o %s" % (html_directory,documents_file)
        os.system("./extract_natural_text.py -d %s -o %s -j %s" % (html_directory,documents_file,json_file))
        print "Done extracting natural text..."

    # third prep documents for sentence splitting, clean up characters
    if step_index <= 2:
        documents_file = options.path + "/documents/"+options.name+".txt"
        pre_sbd_dir = options.path + "/pre_sbd/"+options.name
        print "Prepping documents for sentence splitting..."
        print "using document .txt file: "+documents_file
        print "outputting to: "+pre_sbd_dir
        # issue command
        print "./process_documents.py -f %s -d %s" % (documents_file,pre_sbd_dir)
        os.system("./process_documents.py -f %s -d %s" % (documents_file,pre_sbd_dir))
        print "Done prepping documents for sentence splitting..."

    # fourth run sentence splitting
    if step_index <= 3:
        pre_sbd_dir = options.path + "/pre_sbd/"+options.name
        print "Running sentence splitting with splitta..."
        print "using working dir "+pre_sbd_dir
        # issue command
        print "./run_sentence_splitting.py -d %s" % pre_sbd_dir
        os.system("./run_sentence_splitting.py -d %s" % pre_sbd_dir)
        print "Done sentence splitting..."

    # fifth build the JSON file
    if step_index <= 4:
        pre_sbd_dir = options.path + "/pre_sbd/"+options.name
        json_path = options.path + "/json/"+options.name+".json"
        print "Building JSON..."
        print "using working dir: "+pre_sbd_dir
        # issue command
        print "./build_mn_json.py -d %s -o %s -t %s" % (pre_sbd_dir, json_path, options.name)
        os.system("./build_mn_json.py -d %s -o %s -t %s" % (pre_sbd_dir, json_path, options.name))
        print "Done building JSON..."

        # then split the JSON
        print "Splitting JSON..."
        print "mkdir "+json_path[:-5]
        os.system("mkdir "+json_path[:-5])
        print "./split_apart_json.py "+json_path
        os.system("./split_apart_json.py "+json_path)
        print "mv "+json_path[:-5]+"_* "+json_path[:-5]
        os.system("mv "+json_path[:-5]+"_* "+json_path[:-5])
