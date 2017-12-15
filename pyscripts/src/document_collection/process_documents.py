#!/usr/bin/python

"""
.. module: process_documents

given an input of natural text, put into format for sentence splitting

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-f --file_path        input path of documents to prepare for sentence splitting\n
-d --directory        working directory for sentence splitting\n

"""


import collections
import commands
import json
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

# command line options
#parser = OptionParser()

#parser.add_option("-f", "--file_path", dest="file_path",
        #help="file with documents delimited by ---")

#parser.add_option("-d", "--directory", dest="working_dir",
        #help="working directory for sentence splitting")

#(options,args) = parser.parse_args()

# doc regexes

doc_delimiter = re.compile("^---\n")
doc_id = re.compile("^document id")
url_field = re.compile("^url: ")
query_field = re.compile("^query: ")
text_field = re.compile("^text: ")

# first sentence regex

first_sentence_regex = re.compile("[\b \n][A-Z][A-Za-z0-9 \-,\"]+\.")

class Document_Reader:
    """ read in yaml of docs from previous step of pipeline
    """
    def __init__(self,file_path):
        self.doc_file = file(file_path)
        self.last_record_delimiter = None
        self.file_done = False
    def next_record(self):
        if self.file_done == True:
            return None
        if not self.last_record_delimiter:
            self.last_record_delimiter = self.doc_file.readline()
        doc_id = self.doc_file.readline()
        url = self.doc_file.readline()
        query = self.doc_file.readline()
        current_line = self.doc_file.readline()
        text = ""
        while (not doc_delimiter.match(current_line) and current_line):
            text += current_line
            current_line = self.doc_file.readline()
            if current_line == None:
                self.file_done = True
                break
        if not current_line:
            self.file_done = True
        return {"url": url.rstrip("\n"),
                "query": query.rstrip("\n"),
                "text": text.rstrip("\n")[7:],
                "doc_id": doc_id.rstrip("\n")
                }
    def all_records(self):
        all_records = []
        current_record = self.next_record()
        while current_record:
            if self.validate_record(current_record):
                all_records.append(current_record)
            current_record = self.next_record()
        return all_records
    
    def validate_record(self,record):
        if not doc_id.match(record['doc_id']):
            return False
        if not url_field.match(record['url']):
            return False
        if not query_field.match(record['query']):
            return False
        return True

def check_for_bad_chars(text):
    """ check for bad chars in a string
    """
    bad_chars = False
    output_file = file('bad_chars','a')
    for x in text:
        if x not in string.printable:
            output_file.write(x+"\n")
            bad_chars = True
            break
    return bad_chars

def clean_text(text):
    """ remove bad characters from text by checking chars in string.printable
    """
    new_string = ""
    for x in text:
        if x in string.printable:
            new_string += x
    return new_string

legit_word_regex = re.compile("[A-Za-z]+")

def text_mostly_natural_language(text):
    """ check the text is mostly natural language not strange gibberish
    """
    words = text.split(" ")
    total_words = 0
    legit_words = 0
    for word in words:
        if legit_word_regex.match(word):
            legit_words+= 1
        total_words += 1
    if total_words == 0:
        return False
    if (float(legit_words)/float(total_words)) > .9:
        return True
    else:
        return False


if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    parser.add_option("-f", "--file_path", dest="file_path",
            help="file with documents delimited by ---")

    parser.add_option("-d", "--directory", dest="working_dir",
            help="working directory for sentence splitting")

    (options,args) = parser.parse_args()
    document_reader = Document_Reader(options.file_path)
    all_docs = document_reader.all_records()
    counter = 0
    # build input docs for sentence splitter
    os.mkdir(options.working_dir)
    bad_docs = 0
    total_docs = 0
    for doc in all_docs:
        total_docs += 1
        if not text_mostly_natural_language(doc['text']):
            print "---"
            print doc
            bad_docs += 1
            continue
        output_file = file(options.working_dir+"/"+str(counter)
                +"_output.txt","w")
        output_file.write("---\n"+doc['url']+"\n")
        output_file.write("---\n"+doc['query']+"\n")
        output_file.close()
        input_file = file(options.working_dir+"/"+str(counter)
                +"_input.txt","w")
        input_file.write(clean_text(doc['text']))
        input_file.close()
        counter += 1
    print "---"
    print "total bad docs: "+str(bad_docs)
    print "percentage: "+str(float(bad_docs)/float(total_docs))
