#!/usr/bin/env python
"""
.. module:: jsonvalidate
   :platform: Unix
   :synopsis: Utility for running json validation for MetaNet Internal Exchange Format

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""

import argparse
import json
import sys
import urllib2
import jsonschema

METANET_IXSCHEMA = u'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json'

def validate(insource,schemapath=None):
    """ validated JSON object or file by default against the schema
    on the metanet wiki site
    :param insource: input to evaluation (either filename or dict)
    :type insource:str
    :returns: validation state
    """
    global METANET_IXSCHEMA
    # determine type of data to validate and load it up
    if type(insource)==file:
        data = json.load(file(insource),encoding="UTF-8")
    elif type(insource)==dict:
        data = insource
    else:
        raise Exception("Unsupported source type for validation:"+type(insource))
    # load up the schema
    # if one is passed as parameter, use that.  If not, then look in the data.
    # If not there, then use the default.
    if not schemapath:
        # first look at data itself
        if u'jsonschema' in data:
            schemapath = data[u'jsonschema']
        else:
            schemapath = METANET_IXSCHEMA
    if schemapath.startswith("http"):
        schema = json.load(urllib2.urlopen(schemapath), encoding="UTF-8")
    else:
        schema = json.load(file(schemapath),encoding="UTF-8")
    # run validation and return
    return(jsonschema.validate(data, schema))
        

def main():
    """
    Main method for command line usage
    """
    cmdline = process_command_line()
    if validate(cmdline.datafile, cmdline.schema) is None:
        print cmdline.datafile, "passes validation."
        return 0
    else:
        print cmdline.datafile, "fails validation."
        return 1

def process_command_line():
    """
    Return a command line parser object
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Run JSON validation against a JSON schema specified " \
        "either in the JSON file itself as a top-level 'schema' property " \
        "or via a file or URL passed in to the script using the -s or " \
        "--schema parameter",
        epilog="")
    
    # required (positional) args
    parser.add_argument("-s","--schema", help="Path or URL to JSON Schema. " \
                        "Use of this parameter overrides the schema " \
                        "specified in the data file.")
    parser.add_argument("datafile", help="JSON Data file to validate")
    
    cmdline = parser.parse_args()
    return cmdline

if __name__ == "__main__":
    status = main()
    sys.exit(status)
