#!/usr/bin/python

"""
.. module: build_mn_json

given a directory with split sentences, create MetaNet json

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-d --directory        directory with split sentences\n
-o --output_file      file to store overall json\n

"""

import codecs
import collections
import commands
import datetime
import os
import re
import time
import ujson
import urllib
import urllib2
import urlparse

#from random import random
#from optparse import OptionParser
from time import sleep

# command line options
#parser = OptionParser()

#parser.add_option("-d", "--directory", dest="directory",
        #help="file with input docs directory")

#parser.add_option("-o", "--output_file", dest="output_file",
        #help="file to store json"
        #)

#parser.add_option("-s", action="store_true", dest="small_mode",
        #help="small mode, only pick 6 docs to make test json"
        #)

#parser.add_option("-t", "--document_tag", dest="document_tag",
        #help="title for docs")

#(options,args) = parser.parse_args()

# helper functions

def writefile(fname, jobj):
    """ write the json dict to file
    """
    if fname.endswith('.gz'):
        with gzip.open(fname,"wb") as f:
            ujson.dump(jobj, f, ensure_ascii=True)
    else:
        with codecs.open(fname,"w",encoding='utf-8') as f:
            ujson.dump(jobj, f, ensure_ascii=True)

def build_doc_json(doc_name, file_contents):
    """construct json doc
    """
    doc_components = file_contents.split("---\n")[1:]
    doc_dict = {}
    sentences = []
    doc_dict['name'] = doc_name
    doc_dict['corpus'] = 'yahoo gun control'
    doc_dict['description'] = doc_components[1].rstrip("\n")
    doc_dict['provenance'] = doc_components[0][5:].rstrip("\n")
    doc_dict['type'] = 'web document'
    doc_dict['size'] = 0
    doc_dict['pubdate'] = '2014-07-29'
    doc_dict['perspective'] = 'unknown'
    if doc_dict['description'].rstrip(" ").lstrip(" ") == "query: pro gun rights":
        doc_dict['perspective'] = "individual oversight"
    if doc_dict['description'].rstrip(" ").lstrip(" ") == "query: pro gun control":
        doc_dict['perspective'] = "government oversight"
    sentence_count = 1
    for sentence in doc_components[2:]:
        sentence_dict = {}
        sentence_dict['id'] = doc_name + ":" + str(sentence_count)
        sentence_count += 1
        sentence_dict['idx'] = None
        sentence_dict['text'] = sentence.rstrip("\n")
        sentences.append(sentence_dict)
    doc_dict['size'] = len(sentences)
    return {'doc_dict': doc_dict, 'sentences': sentences}


if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    parser.add_option("-d", "--directory", dest="directory",
            help="file with input docs directory")

    parser.add_option("-o", "--output_file", dest="output_file",
            help="file to store json"
            )

    parser.add_option("-s", action="store_true", dest="small_mode",
            help="small mode, only pick 6 docs to make test json"
            )

    parser.add_option("-t", "--document_tag", dest="document_tag",
            help="title for docs")

    (options,args) = parser.parse_args()

    top_level_json = { 
            'encoding': 'UTF-8',
            'lang': 'en',
            'jsonschema':'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json',
            'documents': [],
            'sentences': []
    }
    all_files = os.listdir(options.directory)
    doc_total = len(all_files)
    if options.small_mode:
        doc_total = 12
    for doc_file in all_files[:doc_total]:
        if doc_file[-10:] == "output.txt":
            # time stamp doc names to make unique
            time_stamp = time.time()
            time_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H-%M-%S')
            new_json =  build_doc_json(options.document_tag+" "+time_stamp+" "+doc_file.split("_")[0],
                    file(options.directory+"/"+doc_file).read())
            top_level_json['documents'].append(new_json['doc_dict'])
            for sentence in new_json['sentences']:
                sentence['idx'] = len(top_level_json['sentences'])
                top_level_json['sentences'].append(sentence)
    writefile(options.output_file,top_level_json)
