#!/usr/bin/python

"""
.. module: run_sentence_splitting

given a working directory of documents, split into sentences

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-d --directory        working directory for sentence splitting\n

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

#parser.add_option("-d", "--directory", dest="working_dir",
        #help="directory with the html documents")

#(options,args) = parser.parse_args()

counter = 0

# TO DO: get this from ENV
# this is hacky and needs to be fixed
# assumes you are running from ~/case_study_sourcing/pyscripts
SPLITTA_PATH = commands.getoutput("cd ../../.. ; pwd") + "/components/splitta.1.03"

# if there is an issue, set SPLITTA_PATH = path of splitta.1.03

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    # TO DO: need to tidy this up, right now it's assumed there are subdirectories in this directory
    # probably change this back to just a directory with all HTML files in it, was arranging them by query

    parser.add_option("-d", "--directory", dest="working_dir",
            help="directory with the html documents")

    (options,args) = parser.parse_args()
    os.system("cd "+SPLITTA_PATH+" ; python sbd.py -m model_nb "+options.working_dir)
