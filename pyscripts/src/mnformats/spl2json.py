#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Sentence per line to JSON format converter
Created on April 1, 2013
@jhong@ICSI.Berkeley.EDU
'''

import os
import sys
import argparse
import codecs
from mnformats import mnjson
reload(sys)
sys.setdefaultencoding("UTF-8")

if os.environ['MNDEVDIR']:
    DEFAULT_SCHEMA_PATH=os.environ['MNDEVDIR']+'/etc/ixjschema.json'
else:
    DEFAULT_SCHEMA_PATH='/u/metnet/dev/etc/ixjschema.json'
    
def main():
    cmdline = process_command_line()
    # read and process sentences in SPL file
    insplf = codecs.open(cmdline.infile.decode('utf-8').encode('utf-8'),"r",encoding="utf-8")

    if not cmdline.prov:
        cmdline.prov = cmdline.name
    if not cmdline.corpus:
        cmdline.corpus = cmdline.name

    # call converter to json object
    json_obj = mnjson.convert_spl_to_json(insplf,cmdline.lang,cmdline.name,
                                          cmdline.corpus,
                                          cmdline.desc,
                                          cmdline.prov,
                                          cmdline.type,
                                          cmdline.comments)

    # add message if set
    if cmdline.message:
        for sent in json_obj[u'sentences']:
            sent[u'comment'] = cmdline.message.decode('utf-8').encode('utf-8')

    # serialize the json object to file
    if cmdline.outputfile:
        fname = cmdline.outputfile.decode('utf-8').encode('utf-8')
    else:
        (filebase, filext) = os.path.splitext(cmdline.infile.decode('utf-8').encode('utf-8'))
        fname = filebase + u'.json'

    # write out the file
    mnjson.writefile(fname,json_obj)
    
    # validate and return status
    if mnjson.validate(json_obj,cmdline.schema) is None:
        return 0
    else:
        print >> sys.stderr, "Error:",fname,"failed validation."
        return 1


def process_command_line():
    global DEFAULT_SCHEMA_PATH
    """
    Return a command line parser object
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Converts SPL format text to JSON format",
        epilog="Note: everything is assumed to be UTF-8.")
    
    # required (positional) args
    parser.add_argument("infile", help="SPL text file")
    parser.add_argument("-l","--lang",
                        help="Language of the input file. This should be an"\
                        " ISO language code (e.g. en, es, ru).",
                        required=True)
    parser.add_argument("-n","--name", required=True,
                        help="Unique name of document (if part of one), "\
                        "which is also used in the id string of all the "\
                        "sentences.")
    
    # optional args
    parser.add_argument("-s","--schema",help="JSON Schema file or URL to " \
                        "use for validation. Note that this is saved into " \
                        "into the output files.",default=DEFAULT_SCHEMA_PATH )
    parser.add_argument("-o","--outputfile",
                        help="Path/name of output file. If not given, the "\
                        "script uses the basename of the input file")
    parser.add_argument("-c","--comment-column",dest="comments",
                        action="store_true",
                        help="Indicates that the first column of the"\
                        " input file contains comments that should be"\
                        " associated with the sentence.")
    parser.add_argument("-m","--comment-message",dest="message",
                        help="Adds the message to the comment field of "\
                        "each sentence")
    parser.add_argument("--desc", help="Description of document",
                        default="Converted from SPL")
    parser.add_argument("--prov", help="Provenance string. If not given, it "\
                        "defaults to the name of the document.  This is the "\
                        "recommended value.")
    parser.add_argument("--corpus",help="Unique name of corpus the document is part of "\
                        "also defaults to the document name if not given. But giving a "\
                        "corpus name is recommended.")
    parser.add_argument("--type", help="Document type (or genre)",default="Manual")
    
    cmdline = parser.parse_args()
    mnjson.METANET_IXSCHEMA = cmdline.schema
    return cmdline

if __name__ == "__main__":
    status = main()
    sys.exit(status)
