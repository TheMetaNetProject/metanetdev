'''
Script for retrieving seeds from wiki or google docs

Created on May 6, 2013

@author: jhong@icsi
'''

import argparse
import sys
import urllib2
import subprocess
import codecs
import os
import re
import csv
import time
import filecmp
from HTMLParser import HTMLParser

"""
global variables
"""
WIKI_SEED_PAGES = {
    "ei": "Economic_inequality_seeds_for_the_LM_extractor",
    "gov": "Governance_seeds_for_the_LM_extractor",
    "test": "Small_test_set_of_seeds_for_LM_extractor"}

SUBDOMAINS = {
    "poverty":"ei",
    "taxation":"ei",
    "wealth":"ei",
    "education":"ei"
}

SUBDOMAIN_COLUMNS = {
    "poverty":3,
    "taxation":5,
    "wealth":4,
    "education":6
}

PYWIKI_GET_SCRIPT = "metaget.py"
PYWIKI_DIR = "/u/metanet/repository/pywikipedia"

GDOC_SEED_PAGES = {
    "en" : {
        "ei":"https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdDJQOUFfME9YMnlwTmhNX2J3VmkwVkE&single=true&gid=2&output=csv"
    },
    "es":{
        "ei":"https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGxFcUNYMmZTTUhwNGhWMXc2STFfdVE&single=true&gid=2&output=csv"
    },
    "ru": {
        "ei":"https://docs.google.com/spreadsheet/pub?key=0Ap6NYC3tEN6GdGJhbXpRQUxocm1yVlRKMzlVVVdwV2c&single=true&gid=2&output=csv"
    }
}

SEEDS_DIR = "/u/metanet/extraction/seeds"

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

class WikiSeedPageHTMLParser(HTMLParser):
    """
    HTML Class to parse seed lists out of <pre> tags on wiki pages
    """
    currentTag = None
    currentLang = None
    subdomain = None
    filterLang = None
    seeds = {}
    
    def __init__(self, subdomain, filterlang):
        self.subdomain = subdomain
        self.filterLang = filterlang
        HTMLParser.__init__(self)

    def get_seeds(self):
        return self.seeds
        
    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.currentTag=tag
            for attr, val in attrs:
                if attr=="class":
                    if val=="enseeds":
                        self.currentLang="en"
                    elif val=="esseeds":
                        self.currentLang="es"
                    elif val=="ruseeds":
                        self.currentLang="ru"
    def handle_endtag(self, tag):
        if tag == "pre":
            self.currentTag=None
            self.currentLang=None

    def handle_data(self, data):
        if self.currentTag=="pre":
            # if filterLang is set, then only handle data if
            # filterlang matches currentLang
            if self.filterLang:
                if self.currentLang != self.filterLang:
                    return
            # filter out comments, or is subdomains given,
            # only include that part
            flines = set()
            currentSD = ""
            for line in data.splitlines(True):
                if line.startswith('#'):
                    if self.subdomain:
                        tgm = re.search('^# Subdomain:(.*)\s*$',line,
                                        re.UNICODE|re.IGNORECASE)
                        if tgm:
                            currentSD = tgm.group(1).lower().strip()
                    continue
                else:
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    # remove any trailing _part_prep's
                    parts[1] = parts[1].split('_')[0]
                    line = ' '.join(parts[0:3])
                if self.subdomain:
                    if currentSD == self.subdomain:
                        flines.add(line)
                else:
                    flines.add(line)
            self.seeds[self.currentLang] = sorted(flines)


def getseeds_wiki(domain, lang=None):
    """
    Get seeds from wiki pages
    """
    global PYWIKI_DIR, PYWIKI_GET_SCRIPT, WIKI_SEED_PAGES, SUBDOMAINS

    if domain in SUBDOMAINS:
        subdomain = domain
        domain = SUBDOMAINS[subdomain]
    else:
        subdomain = None

    tempfile = "seedpagedump."+domain+".txt"
    # retrieve seeds from a page on the wiki
    # assume that the seed page is on the admin wiki
    subprocess.call(['python',
                     PYWIKI_DIR+'/'+PYWIKI_GET_SCRIPT,
                     '-lang:metaphor',
                     '-o',
                     tempfile,
                     WIKI_SEED_PAGES[domain]])

    with codecs.open(tempfile,"r",encoding="utf-8") as f:
        seedpage = u''.join(f.readlines())
        
    parser = WikiSeedPageHTMLParser(subdomain, lang)
    parser.feed(seedpage)
    os.remove(tempfile)    
    return parser.get_seeds()


def getseeds_gdocs(domain, lang=None):
    """
    Get seeds from the google spreadsheet
    """
    global GDOC_SEED_PAGES, SEEDS_DIR, SUBDOMAINS, SUBDOMAIN_COLUMNS
    if lang:
        langs = [lang]
    else:
        langs = GDOC_SEED_PAGES.keys()
    subdomain = None
    if domain in SUBDOMAINS:
        subdomain = domain
        domain = SUBDOMAINS[subdomain]
    seeds = {}
    for l in langs:
        lseeds = set()
    
        isubj = 0
        iverb = 1
        idobj = 2
        igood = 7
        if subdomain:
            isubd = SUBDOMAIN_COLUMNS[subdomain]
        else:
            isubd = 0
    
        # for non-English there are gloss columns
        if l != 'en':
            iverb += 1
            idobj += 2
            igood += 3
            isubd += 3

        page = urllib2.urlopen(GDOC_SEED_PAGES[l][domain])
        reader = csv.reader(page)
        for row in reader:
            subj = row[isubj].decode('utf-8').strip()
            # remove and trailing _part_prep's
            verb = row[iverb].decode('utf-8').strip().split('_')[0]
            dobj = row[idobj].decode('utf-8').strip()
            good = row[igood].decode('utf-8').strip()
            subd = row[isubd].decode('utf-8').strip()
            if subj=='':
                subj = '-'
            if dobj=='':
                dobj = '-'
            if verb=='' or verb=='Verb':
                continue
            if good=='bad':
                continue
            if subdomain and not subd:
                continue
            lseeds.add(u'{0} {1} {2}'.format(subj,verb,dobj))
        seeds[l] = sorted(lseeds)
    return seeds

def process_command_line():
    """
    Return a command line parser object
    """
    global WIKI_SEED_PAGES,GDOC_SEED_PAGES, SEEDS_DIR, PYWIKI_DIR, PYWIKI_GET_SCRIPT
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Retrieves lists of seeds from the metanet admin wiki"\
        "or from google docs spreadsheets.",
        epilog="Note: not every language and domain combination are " \
        "possible. For example, subdomains are only valid for wiki "\
        "seeds")

    # required (positional) args
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g","--gdocs",dest="gdocs",
                        help="Retrieve seeds from google docs",
                        action="store_true")
    group.add_argument("-w","--wiki",dest="wiki",
                        help="Retrieve seeds from wiki",
                        action="store_true")
    parser.add_argument("-l","--lang",dest="lang",
                        help="Retrieve seeds only for this language",
                        default=None,
                        choices=GDOC_SEED_PAGES.keys())
    parser.add_argument("-d","--seed-dir",dest="seeddir",
                        help="Override seed directory.  Note that seeds"\
                        " are differentiated by language under this"\
                        " directory.",
                        default=SEEDS_DIR)
    parser.add_argument("-p","--pywiki-dir", dest="pywiki",
                        help="Pywikipedia installation directory in "\
                        "which to find the "+PYWIKI_GET_SCRIPT+" script.",
                        default=PYWIKI_DIR)
    parser.add_argument("-s","--seed-filename",dest="seedfname",
                        help="Name of seed file to create/update under"\
                        " the seed directory.  Default is seeds.[domain]")
    parser.add_argument("domain", help="Target domain or subdomain"\
                        " identifier.",
                        choices=WIKI_SEED_PAGES.keys()+SUBDOMAINS.keys())
    
    cmdline = parser.parse_args()
    
    # update some globals
    SEEDS_DIR = cmdline.seeddir
    PYWIKI_DIR = cmdline.pywiki
    return cmdline

def main():
    """
    Main processing for command line invocation
    """
    global GDOC_SEED_PAGES, SEEDS_DIR
    cmdline = process_command_line()
    if cmdline.gdocs:
        seeds = getseeds_gdocs(cmdline.domain,cmdline.lang)
    elif cmdline.wiki:
        seeds = getseeds_wiki(cmdline.domain,cmdline.lang)
    seedfname = "seeds."+cmdline.domain
    if cmdline.seedfname:
        seedfname = cmdline.seedfname
    for lang in seeds:
        seedcontent = seeds[lang]
        seeddir = SEEDS_DIR+'/'+lang
        if not os.path.exists(seeddir):
            os.makedirs(SEEDS_DIR+'/'+lang, 0775)
        seedfpath = seeddir+'/'+seedfname
        # if seed file already exists, make backup
        backfpath = None
        if os.path.isfile(seedfpath):
            timenow = time.strftime('%Y.%m.%d-%H:%M')
            backfpath = seedfpath + '.bak-' +timenow
            os.rename(seedfpath,backfpath)
        outf = codecs.open(seedfpath,'w',encoding='utf-8')
        for seed in seedcontent:
            print >> outf, seed
        outf.close()
        # remove backup if its the same
        if (backfpath) and (filecmp.cmp(seedfpath, backfpath, False)):
            os.remove(backfpath)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
