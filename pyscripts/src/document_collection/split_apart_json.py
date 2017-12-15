#!/usr/bin/python

"""
.. module: split_apart_json

split an overall json file into smaller batches

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options] file_path_of_overall_json

"""

import codecs
import collections
import commands
import json
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

def batchify_the_id(the_id, batch_num):
    """ add batch number to overall doc id
    """
    split_up_words = the_id.split(" ")
    split_up_words[0] = split_up_words[0] + "_" + str(batch_num)
    new_id = " ".join(split_up_words)
    return new_id

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    (options,args) = parser.parse_args()
    
    # master file name
    json_file_name = args[0]

    # get master json
    master_json = json.loads(file(json_file_name).read())
    
    # start with a fresh mini json
    new_mini_json = { 
            'encoding': 'UTF-8',
            'lang': 'en',
            'jsonschema':'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json',
            'documents': [],
            'sentences': []
    }
    
    # set initial batch number, last sentence's doc
    batch_number = 0

    last_sentences_doc = None

    # add an "" at end of array to indicate we've processed last batch
    master_json['sentences'].append("")

    # exhaust sentences, adding them to a mini json, when the mini jsons get too big, dump them to file
    for sentence in master_json['sentences']:
        this_sentences_doc = sentence['id'].split(":")[0] if sentence else None
        # check that we've hit 500 sentences and are starting a new doc
        if (len(new_mini_json['sentences']) >= 500 and (last_sentences_doc != this_sentences_doc)) or sentence == "":
            print "---"
            print last_sentences_doc
            print this_sentences_doc
            # add all needed docs
            needed_docs = []
            for mini_json_sentence in new_mini_json['sentences']:
                needed_docs.append(mini_json_sentence['id'].split(":")[0])
            needed_docs = set(needed_docs)
            #print "---"
            #for doc in needed_docs:
                #print doc
            for doc in master_json['documents']:
                if doc['name'] in needed_docs:
                    new_mini_json['documents'].append(doc)
            
            # "batchify" the ids so you can see which file name corresponds to the sentence
            for batch_doc in new_mini_json['documents']:
                batch_doc['name'] = batchify_the_id(batch_doc['name'],batch_number)
            for batch_sentence in new_mini_json['sentences']:
                batch_sentence['id'] = batchify_the_id(batch_sentence['id'],batch_number)
            # write to file
            this_batch_filename = json_file_name[:-5]+"_"+str(batch_number)+".json"
            writefile(this_batch_filename,new_mini_json)
            #print this_batch_filename
            # start a fresh batch
            batch_number += 1
            new_mini_json = { 
                    'encoding': 'UTF-8',
                    'lang': 'en',
                    'jsonschema':'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json',
                    'documents': [],
                    'sentences': []
                    }
        
        # process next sentence
        if sentence:
            sentence['idx'] = len(new_mini_json['sentences']) 
            new_mini_json['sentences'].append(sentence)

        # update last sentence
        last_sentences_doc = this_sentences_doc
