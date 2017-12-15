#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Created on April 1, 2013
@jhong@ICSI.Berkeley.EDU'''

import os
import sys
import argparse
import mnjson

def main():
    """
    Main processing for testset2json
    """
    returnval = 0
    
    cmdline = process_command_line()
    verbose = cmdline.verbose
    filebase = os.path.splitext(cmdline.infile)[0]

    jsondict = mnjson.convert_iarpa_testset_to_jsonlist(cmdline.infile, cmdline.pertext)

    for filespec in jsondict:
        documentnode = jsondict[filespec]
        if cmdline.pertext:
            fname = filespec + ".json"
        else:
            fname = filebase + mnjson.SEPARATOR + filespec + ".json"
        mnjson.writefile(fname, documentnode)
        print fname
        # validate file
        if mnjson.validate(documentnode, cmdline.schema) is None:
            if verbose:
                print >> sys.stderr, "Output", fname, "passes validation."
        else:
            returnval = 1
            if verbose:
                print >> sys.stderr, "Output", fname, "fails validation."
    return returnval

def process_command_line():
    """
    Return a command line parser object
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Convert IARPA TestSet input XML format to MetaNet " \
        "internal JSON format.  Generates one output file per language " \
        "references in the input file.  Output files are generated in " \
        "the same directory as the input file, with names of the format " \
        " basename(infile)____lang.json by default, or with" \
        " ____textid____lang.json if -p is given.  Note that the ____ "\
        " delimiter can also be changed with an option.",
        epilog="")
    
    # required (positional) args
    parser.add_argument("infile", help="TestSet.xml")
    
    # optional args
    parser.add_argument("-s","--schema",help="JSON Schema file or URL to " \
                        "use for validation. Note that this is saved into " \
                        "into the output files.",default=mnjson.METANET_IXSCHEMA )
    parser.add_argument("-p","--per-text",help="Generate one file per text "\
                        "node in the XML file.",dest="pertext",
                        action='store_true')
    parser.add_argument("-v","--verbose",help="Display messages that "\
                        "indicate progress or status.", action='store_true')
    parser.add_argument("-d","--delimiter",help="String to use to separate"\
                        "elements in the outfile filename.",default=mnjson.SEPARATOR)
    cmdline = parser.parse_args()
    mnjson.SEPARATOR = cmdline.delimiter
    mnjson.METANET_IXSCHEMA = cmdline.schema
    return cmdline

if __name__ == "__main__":
    status = main()
    sys.exit(status)
