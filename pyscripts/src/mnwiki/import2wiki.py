#!/usr/bin/env python
'''
Import files into wiki.  Format assume pywikipedia format.
Created on April 16, 2013
@jhong@ICSI.Berkeley.EDU
'''

import os
import sys
import argparse
import subprocess
import codecs

LANGS = ['en','es','fa','ru']

def main():
    """
    Main processing 
    """
    cmdline = process_command_line()
    lang = cmdline.lang
    
    if cmdline.delete:
        for f in cmdline.files:
            if f.startswith('/')==False:
                f = os.getcwd() + '/' + f
            if os.path.exists(f):
                subprocess.call(["python",
                                 "delete.py",
                                 "-lang:"+lang,
                                 "-file:"+f,
                                 "-putthrottle:1"])
        return 0

    if cmdline.file:
        pagefile = codecs.open(cmdline.pagenames,"w",encoding='utf-8')
        for f in cmdline.file:
            if f.startswith('/')==False:
                f = os.getcwd() + '/' + f
            wf = codecs.open(f, "r", encoding='utf-8')
            numpages = 0
            for line in wf:
                l = line.strip()
                if l.startswith("'''"):
                    pagefile.write(l[3:-3])
                    pagefile.write("\n")
                    numpages += 1
            if numpages==0:
                continue
            if os.path.exists(f):
                subprocess.call(["python",
                                 "metapagefromfile.py",
                                 "-lang:"+lang,
                                 "-mergetemplates",
                                 "-notitle",
                                 "-putthrottle:1",
                                 "-start:xxxx",
                                 "-end:yyyy",
                                 "-file:"+f],cwd=cmdline.pywiki)
    return 0

def process_command_line():
    """
    Return a command line parser object
    """
    global LANGS
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Given a list of wiki format files, imports them"\
        " into the wiki, leaving a record of pagenames.  Also can "\
        " delete the pages whos titles are listed in a file.",
        epilog="Note: if the -d option is given, the input files"\
        " are assumed to contain lists of page titles of pages to"\
        " delete from the wiki.")
    
    # required (positional) args
    parser.add_argument("-l","--lang",dest="lang",
                        required=True,help="Language of the wiki"\
                        " to import to.",choices=LANGS)
    parser.add_argument("-d","--delete", dest="delete",
                        help="Instead of importing, delete the "\
                        "pages listed in input file(s).",action="store_true")
    parser.add_argument("-w","--pywiki", dest="pywiki",
                        help="Path to pywiki installation",
                        default="/u/metanet/repository/pywikipedia")
    parser.add_argument("-p","--page-name-file",dest="pagenames",
                        help="Specify the name of the file in "\
                        "which to save to titles of pages that were"\
                        "imported.",default=".importedpages.txt")
    parser.add_argument("file",
                        help="File containing page content to import"\
                        " OR if -d is specified, lists of page titles"\
                        " of pages to delete from the wiki.",
                        nargs='+')
    cmdline = parser.parse_args()
    return cmdline


if __name__ == "__main__":
    status = main()
    sys.exit(status)
