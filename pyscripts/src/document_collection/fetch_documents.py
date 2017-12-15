#!/usr/bin/python

"""
.. module: fetch_documents

given an input json of urls retrieved from Yahoo, fetch the html

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-l --links            file path of json to retrieve\n
-d --directory        directory to store html in\n

"""

import json
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

#parser.add_option("-l", "--links", dest="links_filename", 
        #help="file with json of urls to retrieve")

#parser.add_option("-s", "--start", dest="start_point",
        #help="where to start in input file",default=0)

#parser.add_option("-d", "--directory", dest="directory",
        #help="what directory to store files",default="fetched_documents")

#(options,args) = parser.parse_args()

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    parser.add_option("-l", "--links", dest="links_filename", 
            help="file with json of urls to retrieve")

    parser.add_option("-s", "--start", dest="start_point",
            help="where to start in input file",default=0)

    parser.add_option("-d", "--directory", dest="directory",
            help="what directory to store files",default="fetched_documents")

    (options,args) = parser.parse_args()
    # get links json
    sp = int(options.start_point)
    links_json = json.loads(file(options.links_filename).read())
    # check if dir is present
    if not os.path.isdir(options.directory):
        os.system('mkdir '+options.directory)
    # first assign id to each doc
    curr_id = 0
    for url_data in links_json["urls"]:
        url_data["doc_id"] = curr_id
        curr_id += 1
    # now fetch each document
    for url_data in links_json['urls']:
        url = url_data['url']
        query = url_data['query']
        #all_docs = os.listdir(options.directory)
        #all_docs = [int(d.split('.')[0]) for d in all_docs]
        #if not all_docs:
            #max_doc_number = 0
        #else:
            #max_doc_number = max(all_docs)
        #new_doc_number = max_doc_number + 1
        # fetch the document
        new_doc_number = url_data["doc_id"]
        try:
            print "fetching "+url
            html_location = options.directory+'/'+str(new_doc_number)+".html"
            new_file = file(html_location,"w")
            new_file.write(url+"\n")
            new_file.write(query+"\n")
            new_file.close()
            os.system("curl -m 10 "+url+" >> "+html_location)
            print "curl "+url+" > "+html_location
            print "done fetching...checking results"
            contents = file(html_location).read()
            if not contents:
                os.system('rm '+html_location)
                print "ERROR fetching this page: "+url
            # TO DO: resolve character set issue so HTML can be stored in JSON
            #url_data["html"] = contents
        except:
            print "document failed...oh well..."
            url_data["html"] = "Failed to retrieve html for this document."

    # until I change boilerpipe it needs a dir within a dir, so set that up here
    os.system('cd '+options.directory+' ; mkdir '+options.directory.split('/')[-1]+' ; mv *html '+options.directory.split('/')[-1])
    # dump updated json with html per url
    # TO DO: resolve character set issue
    json_dump_file = file(options.directory+"/"+options.directory.split('/')[-1]+".json","w")
    json_dump_file.write(json.dumps(links_json))
    json_dump_file.close()
