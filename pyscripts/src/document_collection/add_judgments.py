#!/usr/bin/python

"""
.. module: add_jugments

run the case study sourcing pipeline from fetching documents -> creating final json

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-s --start_point      what part of pipeline to start from\n
-n --name             name of document bundle e.g. immigration_01_15\n
-p --path             path of data dir to store results\n

-d --directory        directory with json batches\n
-j --judgments        file with judgments in format url<space>judgment\n
-c --conversion       conversion from shorthand to full judgment io:individual oversight, go:government oversight\n

"""

import json
#from optparse import OptionParser
import os

# command line options
#parser = OptionParser()

#parser.add_option("-d", "--directory", dest="directory",
        #help="directory with json batches")

#parser.add_option("-j", "--judgments", dest="judgment_file",
        #help="file with judgments")

#parser.add_option("-c", "--conversion", dest="conversion",
        #help="convert judgment shorthand to full judgment text, io:individual oversight, go:government oversight")

#(options,args) = parser.parse_args()

# build conversion dict
#conversion_dict = {}
#for kv in options.conversion.split(","):
    #kv = kv.rstrip().lstrip()
    #k = kv.split(":")[0]
    #v = kv.split(":")[1]
    #conversion_dict[k] = v

#print conversion_dict

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    parser.add_option("-d", "--directory", dest="directory",
            help="directory with json batches")

    parser.add_option("-j", "--judgments", dest="judgment_file",
            help="file with judgments")

    parser.add_option("-c", "--conversion", dest="conversion",
            help="convert judgment shorthand to full judgment text, io:individual oversight, go:government oversight")

    (options,args) = parser.parse_args()
    # build conversion dict
    conversion_dict = {}
    for kv in options.conversion.split(","):
        kv = kv.rstrip().lstrip()
        k = kv.split(":")[0]
        v = kv.split(":")[1]
        conversion_dict[k] = v

    print conversion_dict
    url_to_judgment = {}
    # read in urls and judgments
    for url_judgment in file(options.judgment_file).read().split("\n")[:-1]:
        url = url_judgment.split(" ")[0]
        judgment = url_judgment.split(" ")[1]
        url_to_judgment[url] = conversion_dict[judgment]
    # go through each batch in json, add judgments
    batch_files = os.listdir(options.directory)
    for batch_file in batch_files:
        full_file_path = options.directory+"/"+batch_file
        doc_json = json.loads(file(full_file_path).read())
        # go through every document see if we have a judgment
        for doc in doc_json['documents']:
            if doc['provenance'] in url_to_judgment:
                doc['perspective'] = url_to_judgment[doc['provenance']]
                print "---"
                print "added "+doc['perspective'] + ' to ' + doc['provenance']
                print "in this file: "+batch_file
        # write the updated json
        json_file = file(full_file_path,"w")
        json_file.write(json.dumps(doc_json))
        json_file.close()
