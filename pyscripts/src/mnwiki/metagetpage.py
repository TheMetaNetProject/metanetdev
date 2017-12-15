# -*- coding: utf-8 -*-
"""
Very simple script which gets a page and writes its contents to
standard output. This makes it possible to pipe the text to another
process.

Syntax: python get.py Title of the page

Example: python get.py Wikipedia | grep MediaWiki > results.txt
"""

# (C) Daniel Herding, 2005
#
# Distributed under the terms of the MIT license.

__version__='$Id: get.py 8525 2010-09-11 16:21:58Z xqt $'

import sys
sys.path.insert(0, '/u/metanet/repository/pywikipedia')

import wikipedia as pywikibot
import argparse
import codecs

def main():
    singlePageTitleParts = []
    args = pywikibot.handleArgs()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Script to retrieve a single wiki page. Modified so that"\
        " output can be written out to a file to circumvent unicode issues.",
        epilog="Note: to see pywikipedia's standard argument options, run"\
        " this script with '-help'")
    parser.add_argument("-o","--outputfile",dest="outfile",
                        help="File to write output to")
    parser.add_argument('titleparts', metavar='Title', nargs='+',
                        help='Page title')
    cmdline = parser.parse_args(args)

    singlePageTitleParts = cmdline.titleparts
    
    pageTitle = " ".join(singlePageTitleParts)
    page = pywikibot.Page(pywikibot.getSite(), pageTitle)

    # TODO: catch exceptions
    if cmdline.outfile:
        with codecs.open(cmdline.outfile,"w",encoding="utf-8") as f:
            f.write(page.get())
    else:
        pywikibot.output(page.get(), toStdout = True)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

