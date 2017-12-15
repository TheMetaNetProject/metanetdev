#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for retrieving pages from a MediaWiki instance

This script uses a MediaWiki client api to retrieve filtered lists of
page names.  This is because we don't want every page to be copied.
It then uses a maintenance script to retrieve the content of those pages
in XML format.  Because of this latter step, it must run on the server
that hosts the MediaWiki from which the pages are being retrieved.

Example:

% getwikipages.py -u USER -p PASS -s metaphor.icsi.berkeley.edu -w /da/metaphor/wiki dev

Page name lists are created in .txt format and page concent in .xml, and
are created in the current directory.

jhong@icsi
"""

from __future__ import print_function

# workaround for urllib3/python<2.7.9 InsecurePlatformWarning issue
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

import requests
import os, sys, mwclient, argparse, logging, pprint, codecs, itertools, re
from subprocess import call

DEFAULT_SITE='ambrosia.icsi.berkeley.edu:2080'

DBNAME_MAP={'en':'enmetanetwiki',
            'es':'esmetanetwiki',
            'ru':'rumetanetwiki',
            'fa':'fametanetwiki',
            'metaphor':'enmetanetadminwiki'}

EXPORT_CATEGORIES = ['Metaphor',
                     'Metaphor_family',
                     'Frame',
                     'Frame_family',
                     'Construct_analysis',
                     'CxnMP',
                     'MetaRC',
                     'IARPASourceConcept',
                     'IARPATargetConcept',
                     'Definition'
                    ]

INTERNAL_ONLY_CATEGORIES = ['Construct_analysis',
                            'CxnMP',
                            'MetaRC',
                            'IARPASourceConcept',
                            'IARPATargetConcept',
                            'Metaphor_family',
                            'Frame_family'
                            ]

STATUS_CATEGORIES = ['Metaphor','Frame','Metaphor_family','Frame_family']

EXPORT_NAMESPACES = {'Template':10,
                     'Category':14,
                     'Property':102,
                     'Form':106,
                     'Cit':800,
                     'Glossary':502,
                     'MediaWiki':8,
                     'default':0
                     }

EXPORT_TALK_NAMESPACES = {"Glossary_talk": 503,
                          "Metaphor_talk": 551,
                          "Frame_talk": 553,
                          "Metaphor_family_talk": 555,
                          "Frame_family_talk": 557
                          }

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
    parser.add_argument('--scriptpath',help='Wiki script path')
    parser.add_argument('--protocol',help='Protocol to connect to wiki api',
                        default='https')
    parser.add_argument('-l','--lang',help="Language",required=True,
                        choices=DBNAME_MAP.keys())
    parser.add_argument('-e','--external',action='store_true',
                        help='Flag as page export for external release.  This will '\
                        'cause internal-only namespaces to be skipped in the page '\
                        'retrieval. It also requires Metaphor and Frame pages to '\
                        'have a status that is not "problematic" for inclusion.')
    parser.add_argument('-r','--release-only',dest='releaseonly',action='store_true',
                        help='Include only "approved for release" metaphors and frames'\
                        ' in the external release (i.e. do not include "release candidate")')
    parser.add_argument('--talk',action='store_true',
                        help='Causes only talk pages to be exported.  This is used in '\
                        'the process of updating the public wiki, where we want to '\
                        'import updated content from the development wiki while '\
                        'preserving talk-page content from the public wiki.')
    parser.add_argument('-w','--wikiroot',help='Root directory of wiki instance')
    parser.add_argument('-x','--excludefile',default=default_exclude_file,
                        help='File containing names of pages to exclude from'\
                        'export/import')
    parser.add_argument('-n','--nohist',help='No history.  Just current versions',
                        action='store_true')
    parser.add_argument('--users',help='Create a mysqldump of the wiki\'s users',
                        action='store_true')
    parser.add_argument('--certificate',help='Path to self-signed certificate',
                        default=wikietcpath + '/metanet.cert.pem')
    parser.add_argument('--no-certificate',action='store_true',dest='nocertificate',
                        help='Do not use stored certificate to connect to API')

    cmdline = parser.parse_args()
    return cmdline


def main ():
    global EXPORT_CATEGORIES, EXPORT_NAMESPACES, EXPORT_TALK_NAMESPACES
    global INTERNAL_ONLY_CATEGORIES, STATUS_CATEGORIES
    
    # for logging / error messages
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    logging.basicConfig(format=msgformat, datefmt=dateformat,
                        level=logging.INFO)

    params = get_parameters()
    if params.releaseonly:
        params.external = True
        
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

    # connect to the mediawiki via API to retrieve page names
    if not params.scriptpath:
        params.scriptpath = '/'+params.lang+'/'
    if not params.scriptpath.endswith('/'):
        params.scriptpath += '/'
    logging.info('Connecting to %s%s as %s', params.site, params.scriptpath,
                 params.username)
    
    wikietcpath=os.path.dirname(os.path.realpath(__file__))
    session = requests.Session()
    session.verify = params.certificate
    session.auth = None
    session.headers['User-Agent'] = 'MwClient/' + mwclient.client.__ver__ + ' (https://github.com/mwclient/mwclient)'
    if params.nocertificate:
        session=None
    site = mwclient.Site((params.protocol,params.site),path=params.scriptpath,pool=session)
    site.login(params.username,params.password) 

    get_by_category = []
    status_categories = set(STATUS_CATEGORIES)
    internal_only = set(INTERNAL_ONLY_CATEGORIES)
    
    if params.talk:
        get_by_namespace = EXPORT_TALK_NAMESPACES
    else:
        get_by_namespace = EXPORT_NAMESPACES
        get_by_category = EXPORT_CATEGORIES

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

    # retrieve page names by category first
    for category in get_by_category:
        logging.info("processing category %s", category)
        with codecs.open('%s-%s.txt'%(params.dumpprefix,category),
                         mode='w',encoding='utf8') as outf:
            if params.external:
                if category in internal_only:
                    continue
            if params.external and (category in status_categories):
                #statusstring='release candidate||approved for release'
                statusstring='!problematic'
                if params.releaseonly:
                    statusstring='approved for release'
                askquery=u'[[Category:%s]] [[Status::%s]]'%(category,statusstring)
            else:
                askquery=u'[[Category:%s]]' % (category)
            result = site.api('ask',query=askquery)
            for r in result['query']['results']:
                if r not in allpagenames:
                    print(r,file=outf)
                    allpagenames.add(r)
 
    testpat = re.compile(ur'(Alpha|ETest|Ec ineq wild|En2Pre|E[ns]Pre|Eng\dof\d|Esp1|Logic|RuPre|Rus1)',
                         flags=re.U)
 
    # retrieve page names by namespace next
    for nsname, ns in get_by_namespace.iteritems():
        logging.info("processing namespace %s", nsname)
        with codecs.open('%s-%s.txt'%(params.dumpprefix,nsname),
                         mode='w',encoding='utf8') as outf:
            # if external option is set, skip processing any namespaces
            # that are marked as internal only
            if params.external:
                if nsname in internal_only:
                    continue
            # retrieve all the page names in the namespace
            result = site.api('query',list='allpages',apnamespace=ns,aplimit=5000)
            for r in result['query']['allpages']:
                ptitle = r['title']
                # obsolete: used to skip particular garbage pages that used to be in the old admin wiki
                if ((params.lang=='metaphor') and (nsname=='default') and
                    testpat.match(ptitle)):
                    continue
                # do not export multiple times
                if ptitle not in allpagenames:
                    print(ptitle,file=outf) 
                    allpagenames.add(ptitle)        
    
    # change into maintenance directory and retrieve page content
    cwd = os.getcwd()
    os.chdir(params.wikiroot + '/maintenance')
    exportcmd = []
    if os.path.exists('./runonwiki'):
        exportcmd.extend(['./runonwiki',params.lang])
    else:
        exportcmd.append('php')
    exportcmd.append('dumpBackup.php')
    if params.nohist:
        exportcmd.append('--current')
    else:
        exportcmd.append('--full')
    for nscat in itertools.chain(get_by_namespace.keys(),get_by_category):
        fpath = '%s/%s-%s.txt' % (cwd, params.dumpprefix, nscat)
        ofpath = '%s/%s-%s.xml' % (cwd, params.dumpprefix, nscat)
        if (not os.path.exists(fpath)) or (os.stat(fpath).st_size == 0):
            logging.info('page retrieval: skipping %s: no file or zero size',
                         fpath)
            continue
        logging.info('retrieving page content for %s',fpath)
        call(exportcmd+['--pagelist='+fpath,
                        '--output=file:'+ofpath])
    
    # dump users
    if params.users:
        # read database info from settings file
        with codecs.open(params.wikiroot + '/LocalSettings.php',encoding='utf-8') as lf:
            varpat = re.compile(ur'\$(\w+)\s+=\s+"([^"]+)";',flags=re.U)
            dbUser = None
            dbPw = None
            dbName = None
            for line in lf:
                m = varpat.match(line)
                if not m:
                    continue
                if m.group(1)=='wgDBuser':
                    dbUser=m.group(2)
                if m.group(1)=='wgDBpassword':
                    dbPw=m.group(2)
                if m.group(1)=='wgDBname':
                    dbName=m.group(2)
                if dbUser and dbPw and dbName:
                    break
            if not dbName:
                dbName = DBNAME_MAP[params.lang]
            if dbUser and dbPw and dbName:
                ofname = '%s/%s-userdump.sql'%(cwd,params.dumpprefix)
                dumpcmd = ['/usr/bin/mysqldump','-c','-t',
                           '--extended-insert=FALSE',
                           '-u',dbUser,
                           '--password='+dbPw, 
                           dbName,'user','--where=user_id>1',
                           '--result-file='+ofname]
                call(dumpcmd)
            else:
                logging.error('Could not extract login info for database')
    
if __name__ == "__main__":
    status = main()
    sys.exit(status)
