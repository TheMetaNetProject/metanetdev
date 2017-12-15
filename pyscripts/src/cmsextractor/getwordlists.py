'''
OBSOLETE: Script for retrieving wordlists from google docs for the SCMS extractor

Created on May 20, 2013

@author: jhong@icsi
'''

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

GDOC_WL_PAGES = {
    "en" : {
        "ei": {
            "target": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdDJQOUFfME9YMnlwTmhNX2J3VmkwVkE&single=true&gid=4&output=csv",
            "source": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdDJQOUFfME9YMnlwTmhNX2J3VmkwVkE&single=true&gid=5&output=csv"
        }
    },
    "es" : {
        "ei": {
            "target": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGxFcUNYMmZTTUhwNGhWMXc2STFfdVE&single=true&gid=4&output=csv",
            "source": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGxFcUNYMmZTTUhwNGhWMXc2STFfdVE&single=true&gid=5&output=csv"
        }
    },
    "fa" : {
        "ei": {
            "target": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGExNE05VlhXRWwyQUpqMmwwdmVDV2c&single=true&gid=4&output=csv",
            "source": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGExNE05VlhXRWwyQUpqMmwwdmVDV2c&single=true&gid=5&output=csv"
        }
    },
    "ru" : {
        "ei": {
            "target": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGJhbXpRQUxocm1yVlRKMzlVVVdwV2c&single=true&gid=4&output=csv",
            "source": "https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGJhbXpRQUxocm1yVlRKMzlVVVdwV2c&single=true&gid=5&output=csv"
        }
    }
}

WORDLISTS_DIR = "/u/metanet/extraction/wordlists"

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def get_wordlists_gdoc(domain, lang=None):
    """
    Get word lists from the google spreadsheet
    """
    global GDOC_WL_PAGES, WL_DIR
    if lang:
        langs = [lang]
    else:
        langs = GDOC_WL_PAGES.keys()
    wordlists = {}
    for l in langs:
        # get target wordlist, in wordTABsubdomain, allow duplicates
        targetwordlist = get_single_wordlist(GDOC_WL_PAGES[l][domain]["target"], l)
        sourcewordlist = get_single_wordlist(GDOC_WL_PAGES[l][domain]["source"], l)
        wordlists[l] = {"target": targetwordlist, "source": sourcewordlist}
    return wordlists

def get_single_wordlist(pageurl, lang):
    """
    Takes a google doc CSV page url and returns a wordlist where each row
    has the word(form/regular expression) followed by the subdomain name,
    separated by a tab.
    """
    wordlist = []
    page = urllib2.urlopen(pageurl)
    reader = csv.reader(page)
    rownum = 0
    headers = []
    for row in reader:
        if rownum==0:
            # this is the header: subdomains
            for col in row:
                header = col.decode('utf-8').strip()
                # strip anything in parentheses
                header = re.sub(r'\([\w\s]+\)',r'',header,0,re.I|re.U).strip()
                if not header:
                    header = 'GENERAL ECONOMIC INEQUALITY'
                headers.append(header)
        else:
            colnum = -1
            for col in row:
                colnum += 1
                w = col.decode('utf-8').strip()
                if (lang=='fa') and (re.search(r'[A-Za-z]+',w,re.U|re.I)):
                    continue
                if (w) and (not w.startswith(u'#')):
                    wlentry = w+"\t"+headers[colnum]
                    wordlist.append(wlentry)
        rownum += 1
    return wordlist

def process_command_line():
    """
    Return a command line parser object
    """
    global GDOC_WL_PAGES, WORDLISTS_DIR
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Retrieves lists of wordlists from the Clusters, Seeds,"\
        "and Wordlists google docs spreadsheets.",
        epilog="")

    # required (positional) args
    parser.add_argument("-l","--lang",dest="lang",
                        help="Retrieve wordlists only for this language",
                        default=None,
                        choices=GDOC_WL_PAGES.keys())
    parser.add_argument("-d","--wordlists-dir",dest="wldir",
                        help="Override wordlists directory.  Note that "\
                        " wordlists are differentiated by language under"\
                        " this directory.",
                        default=WORDLISTS_DIR)
    parser.add_argument("domain", help="Target domain"\
                        " identifier.",
                        choices=GDOC_WL_PAGES["en"].keys())
    
    cmdline = parser.parse_args()
    
    # update some globals
    WORDLISTS_DIR = cmdline.wldir
    return cmdline

def main():
    """
    Main processing for command line invocation
    """
    global GDOC_WL_PAGES, WORDLISTS_DIR
    cmdline = process_command_line()
    wordlists = get_wordlists_gdoc(cmdline.domain,cmdline.lang)
    for lang in wordlists:
        wldir = WORDLISTS_DIR+'/'+lang
        if not os.path.exists(wldir):
            os.makedirs(WORDLISTS_DIR+'/'+lang, 0775)
        for listtype in wordlists[lang].keys():
            wlfname = listtype + '.' + cmdline.domain
            wlfpath = wldir + '/' + wlfname
            backfpath = None
            if os.path.isfile(wlfpath):
                timenow = time.strftime('%Y.%m.%d-%H:%M')
                backfpath = wlfpath+ '.bak-' +timenow
                os.rename(wlfpath, backfpath)
            outf = codecs.open(wlfpath,'w',encoding='utf-8')
            wl = wordlists[lang][listtype]
            for w in wl:
                print >> outf, w
            outf.close()
            # if the new file and the backup are the same, delete the backup
            if (backfpath) and (filecmp.cmp(wlfpath,backfpath,False)):
                os.remove(backfpath)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
