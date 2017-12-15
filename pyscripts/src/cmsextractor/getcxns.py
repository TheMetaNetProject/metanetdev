"""
OBSOLETE: script for retrieving cxn lists from google docs

Created on May 31, 2013

@author: jhong@icsi
"""

import argparse
import sys
import urllib2
import codecs
import os
import filecmp
import csv
import time
import re

"""
global variables
"""

GDOC_CXN_PAGES = {
    "en" : {
        "ei": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdDJQOUFfME9YMnlwTmhNX2J3VmkwVkE&single=true&gid=6&output=csv"
    },
    "es" : {
        "ei": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGxFcUNYMmZTTUhwNGhWMXc2STFfdVE&single=true&gid=6&output=csv"
    },
    "fa" : {
        "ei": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGExNE05VlhXRWwyQUpqMmwwdmVDV2c&single=true&gid=6&output=csv"
    },
    "ru" : {
        "ei": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGJhbXpRQUxocm1yVlRKMzlVVVdwV2c&single=true&gid=6&output=csv"
    }
}

CXNS_DIR = "/u/metanet/extraction/cxns"

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def get_cxnlists_gdoc(domain, lang=None):
    """
    Get cxn lists from the google spreadsheet
    """
    global GDOC_CXN_PAGES, CXNS_DIR
    if lang:
        langs = [lang]
    else:
        langs = GDOC_CXN_PAGES.keys()
    cxnlists = {}
    for l in langs:
        cxnlists[l] = get_cxn_list(GDOC_CXN_PAGES[l][domain], l)
    return cxnlists

def get_cxn_list(pageurl, lang):
    """
    Takes a google doc CSV page url and returns a cxn list where each row
    has the cxn followed by a description, separated by a tab.
    """
    cxns = []
    page = urllib2.urlopen(pageurl)
    reader = csv.reader(page)
    rownum = -1
    for row in reader:
        rownum += 1
        if rownum==0:
            # this is the header: skip it
            continue
        else:
            cxn = row[0].strip()
            if cxn:
                comment = u''
                weight = u''
                if len(row) > 1:
                    # read comment
                    comment = row[1].strip()
                if len(row) > 2:
                    # read weight
                    weight = row[2].strip()
                cxns.append(u'{0}\t{1}\t{2}'.format(cxn,weight,comment))
    return cxns

def process_command_line():
    """
    Return a command line parser object
    """
    global GDOC_CXN_PAGES, CXNS_DIR
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Retrieves lists of cxns from the Clusters, Seeds,"\
        "Wordlists, and Cxns google docs spreadsheets.",
        epilog="")

    # required (positional) args
    parser.add_argument("-l","--lang",dest="lang",
                        help="Retrieve cxns only for this language",
                        default=None,
                        choices=GDOC_CXN_PAGES.keys())
    parser.add_argument("-d","--cxnlists-dir",dest="cxndir",
                        help="Override cxns directory.  Note that "\
                        " cxn lists are differentiated by language under"\
                        " this directory.",
                        default=CXNS_DIR)
    parser.add_argument("domain", help="Target domain"\
                        " identifier.",
                        choices=GDOC_CXN_PAGES["en"].keys())
    
    cmdline = parser.parse_args()
    
    # update some globals
    CXNS_DIR = cmdline.cxndir
    return cmdline

def main():
    """
    Main processing for command line invocation
    """
    global GDOC_CXN_PAGES, CXNS_DIR
    cmdline = process_command_line()
    cxnlists = get_cxnlists_gdoc(cmdline.domain,cmdline.lang)
    for lang in cxnlists:
        cxndir = CXNS_DIR+'/'+lang
        if not os.path.exists(cxndir):
            os.makedirs(CXNS_DIR+'/'+lang, 0775)
        cxnfname = u'cxns.' + cmdline.domain
        cxnfpath = cxndir + '/' + cxnfname
        backfpath = None
        if os.path.isfile(cxnfpath):
            timenow = time.strftime('%Y.%m.%d-%H:%M')
            backfpath = cxnfpath+ '.bak-' +timenow
            os.rename(cxnfpath, backfpath)
        outf = codecs.open(cxnfpath,'w',encoding='utf-8')
        cxns = cxnlists[lang]
        for cxn in cxns:
            print >> outf, cxn
        outf.close()
        # if the new file and the backup are the same, delete the backup
        if (backfpath) and (filecmp.cmp(cxnfpath,backfpath,False)):
            os.remove(backfpath)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
