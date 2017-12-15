#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for retrieving pages from a MediaWiki instance

This script uses a MediaWiki client api to retrieve filtered lists of
page names.  This is because we don't want every page to be copied.

jhong@icsi
"""

from __future__ import print_function
import os, sys, mwclient, argparse, logging, pprint, codecs, itertools
from subprocess import call

DEFAULT_SITE='metaphor.icsi.berkeley.edu'

def get_parameters():
    wikietcpath=os.path.dirname(os.path.realpath(__file__))
    default_exclude_file=wikietcpath+'/pages-to-exclude.txt'
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Script for retrieving pages from MediaWiki for the purpose "\
        "of duplication or external release.  Creates files containing page names "\
        "and XML dumps in the current directory.  Must be run locally on the "\
        "server that hosts the MediaWiki.")
    parser.add_argument('dumpprefix',help='Prefix to use for all page name dumps')
    parser.add_argument('-u','--username',help='Wiki username')
    parser.add_argument('-p','--password', help='Wiki password')
    parser.add_argument('-c','--config',help='Read login information from file',
                        default=os.path.expanduser('~')+'/.conf.metanet')
    parser.add_argument('-s','--site',help='Wiki site',default=DEFAULT_SITE)
    parser.add_argument('-l','--lang',help="Language",required=True)
    parser.add_argument('-e','--external',action='store_true',
                        help='Flag as page export for external release. This includes'\
                            ' all pages that do not have status "problematic."')
    parser.add_argument('-r','--release-only',dest='releaseonly',action='store_true',
                        help='Include only "approved for release" metaphors and frames'\
                        ' (for external only)')
    parser.add_argument('-w','--wikiroot',help='Root directory of wiki instance')
    parser.add_argument('-x','--excludefile',default=default_exclude_file,
                        help='File containing names of pages to exclude from'\
                        'export/import')
    cmdline = parser.parse_args()
    return cmdline

def main ():
    # for logging / error messages
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    logging.basicConfig(format=msgformat, datefmt=dateformat,
                        level=logging.INFO)

    params = get_parameters()

        
    # read wiki login information from config file.
    config = {}
    if os.path.exists(params.config):
        with open(params.config, 'r') as f:
            for line in f:
                if line.isspace():
                    continue
                line = line.strip()
                if line.startswith('#'):
                    continue
                if '=' in line:
                    variable, value = line.split('=',1)
                    config[variable] = value
    if (not params.username) and ('MNWIKI_USER' in config):
        params.username = config['MNWIKI_USER']
    if (not params.password) and ('MNWIKI_PW' in config):
        params.password = config['MNWIKI_PW']

    logging.info('Connecting to %s/%s/ as %s', params.site, params.lang,
                 params.username)
    site = mwclient.Site(('https',params.site),path='/'+params.lang+'/')
    site.login(params.username,params.password)

    get_by_category = ['Metaphor',
                       'Metaphor_family',
                       'Schema',
                       'Schema_family',
                       'Construct_analysis',
                       'CxnMP',
                       'MetaRC',
                       'IARPASourceConcept',
                       'IARPATargetConcept'
                       ]

    get_by_namespace = {'Template':10,
                        'Category':14,
                        'Property':102,
                        'Form':106,
                        'Cit':800,
                        'Glossary':502,
                        'MediaWiki':8,
                        'default':0
                        }

    status_categories = set(['Metaphor','Schema'])

    internal_only = set(['Construct_analysis',
                         'CxnMP',
                         'MetaRC',
                         'IARPASourceConcept',
                         'IARPATargetConcept'
                         ])

    allpagenames=set()
    
    # read excluded pages file and store in a set
    with codecs.open(params.excludefile,encoding='utf-8') as excludef:
        for line in excludef:
            ptitle = line.strip()
            if ptitle and not ptitle.startswith('#'):
                allpagenames.add(ptitle)
    
    # read additional page names to exclude for an external release
    if params.external:
        wikietcpath=os.path.dirname(os.path.realpath(__file__))
        extfpath=wikietcpath+'/exclude-pages-for-external.txt'
        with codecs.open(extfpath,encoding='utf-8') as excludef:
            for line in excludef:
                ptitle = line.strip()
                if ptitle and not ptitle.startswith('#'):
                    allpagenames.add(ptitle)

    # retrieve pages by category first
    for category in get_by_category:
        logging.info("processing category %s", category)
        os.mkdir(category)
        if params.external:
            if category in internal_only:
                logging.info("...skipping because internal only")
                continue
        if params.external and (category in status_categories):
            statusstring='!problematic'
            if params.releaseonly:
                statusstring='approved for release'
            askquery=u'[[Category:%s]] [[Status::%s]]'%(category,statusstring)
        else:
            askquery=u'[[Category:%s]]' % (category)
        result = site.api('ask',query=askquery)
        for pagename in result['query']['results']:
            if pagename not in allpagenames:
                page = site.Pages[pagename]
                text = page.text()
                with codecs.open('%s/%s'%(category,pagename.replace('/','__SLASH__')),'w',encoding='utf-8') as f:
                    print(text,file=f)
                allpagenames.add(pagename)
 
    # retrieve page names by namespace next
    for nsname, ns in get_by_namespace.iteritems():
        logging.info("processing namespace %s", nsname)
        os.mkdir(nsname)
        if params.external:
            if nsname in internal_only:
                logging.info("...skipping because internal only")
                continue
        result = site.api('query',list='allpages',apnamespace=ns,aplimit=5000)
        for r in result['query']['allpages']:
            pagename = r['title']
            if pagename not in allpagenames:
                page = site.Pages[pagename]
                text = page.text()
                with codecs.open('%s/%s'%(nsname,pagename.replace('/','__SLASH__')),'w',encoding='utf-8') as f:
                    print(text,file=f) 
                allpagenames.add(r['title'])        
        
    
if __name__ == "__main__":
    status = main()
    sys.exit(status)
