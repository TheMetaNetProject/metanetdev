#!/usr/bin/python

"""
.. module: extract_natural_text

given a folder of html, extract natural text

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-d --directory        directory where html is stored\n
-o --output_file      path to dump documents to\n
-j --output_json      path to dump json output to\n

"""

import commands
import os
import re
import time
import urllib
import urllib2
import urlparse

#from random import random
#from optparse import OptionParser
from time import sleep

# command line options
#parser = OptionParser()

# TO DO: need to tidy this up, right now it's assumed there are subdirectories in this directory
# probably change this back to just a directory with all HTML files in it, was arranging them by query

#parser.add_option("-d", "--directory", dest="documents_directory",
        #help="directory with the html documents, e.g. html/sourcing_test_01_13")

#parser.add_option("-o", "--output_file", dest="output_file",
        #help="file to output documents to")

#parser.add_option("-j","--output_json", dest="output_json",
        #help="path to dump json output to")

#(options,args) = parser.parse_args()

counter = 0

# TO DO: read this from ENV, for now just gonna put my local in script
BOILER_JAVA_CP = "build/demo:dist/boilerpipe-1.2.0.jar:lib/nekohtml-1.9.13.jar:lib/xerces-2.9.1.jar:lib/gson-2.2.4.jar"

# this assumes you are in document_collection directory
PATH_TO_BOILER = commands.getoutput("cd ../../.. ; pwd") + "/components/boilerpipe-read-only/boilerpipe-core"

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    # TO DO: need to tidy this up, right now it's assumed there are subdirectories in this directory
    # probably change this back to just a directory with all HTML files in it, was arranging them by query

    parser.add_option("-d", "--directory", dest="documents_directory",
            help="directory with the html documents, e.g. html/sourcing_test_01_13")

    parser.add_option("-o", "--output_file", dest="output_file",
            help="file to output documents to")

    parser.add_option("-j","--output_json", dest="output_json",
            help="path to dump json output to")

    (options,args) = parser.parse_args()
    master_html_dir = options.documents_directory
    output_file = options.output_file
    output_json = options.output_json
    # cd to boiler directory, call java with class path needed for boiler, print boiler's output to output file
    #print "cd "+PATH_TO_BOILER+" ; java -cp "+BOILER_JAVA_CP+" "+master_html_dir+" > "+output_file
    print "Running boiler pipe..."
    os.system("cd "+PATH_TO_BOILER+" ; java -cp "+BOILER_JAVA_CP+" de.l3s.boilerpipe.demo.DocumentProcessor "+master_html_dir+" "+output_json+" > "+output_file)
