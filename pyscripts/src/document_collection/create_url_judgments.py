#!/usr/bin/python

"""
.. module: create_url_judgments

run the case study sourcing pipeline from fetching documents -> creating final json

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-i --input_file       file with judgments from Google Docs\n
-o --output_file      file with url judgment pairs to input into system\n

"""

#from optparse import OptionParser
import os
import re

# command line options
#parser = OptionParser()

#parser.add_option("-i", "--input_file", dest="input_file",
        #help="file with judgments from Google Docs")

#parser.add_option("-o", "--output_file", dest="output_file",
        #help="file with url judgment pairs to input into system")

#(options,args) = parser.parse_args()

# helpful regexes
url_to_id_regex = re.compile("^RESULT_NUM to URL:")
judgment_regex = re.compile("^judgment for")

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    parser.add_option("-i", "--input_file", dest="input_file",
            help="file with judgments from Google Docs")

    parser.add_option("-o", "--output_file", dest="output_file",
            help="file with url judgment pairs to input into system")

    (options,args) = parser.parse_args()
    google_docs_input = file(options.input_file).read().split("\n")
    id_to_url = {}
    id_to_judgment = {}
    for line in google_docs_input:
        if judgment_regex.match(line):
            judgment = line.split(":")[1].rstrip(" \r").lstrip(" \r")
            doc_id = line.split(":")[0].split(" ")[-1]
            #print (doc_id,judgment)
            id_to_judgment[doc_id] = judgment
        if url_to_id_regex.match(line):
            (doc_id,url) =  ":".join(line.split(":")[1:]).rstrip(" \r").lstrip(" \r").split(" ")
            #print (doc_id,url)
            id_to_url[doc_id] = url

    # write to output file
    output_file = file(options.output_file,"w")
    for doc_id in id_to_url:
        if id_to_judgment[doc_id] != "?":
            #print id_to_url[doc_id] + " " + id_to_judgment[doc_id]
            output_file.write(id_to_url[doc_id] + " " + id_to_judgment[doc_id]+"\n")

    output_file.close()
