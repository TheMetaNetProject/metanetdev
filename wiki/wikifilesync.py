#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for synchronizing the MetaNet wiki pages to files on local storage.

jhong@icsi
"""

from __future__ import print_function
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

import os, sys, mwclient, argparse, logging, pprint, codecs, itertools, re, ujson
import time, calendar
from datetime import datetime
import requests
from subprocess import call

DEFAULT_SERVER='ambrosia.icsi.berkeley.edu:2080'
DEFAULT_SCRIPT_PATH='/dev/en'

def get_parameters():
    """ Parse command-line parameters an return as a dictionary.
    """
    wikietcpath=os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Script for synchronizing a MetaNet metaphor wiki with "\
                    "file on local storage.  It should be run from the root "\
                    "directory of the wiki page dump tree.")
    parser.add_argument('-v','--verbose',help='Display status messages',
                        action='store_true')
    parser.add_argument('-u','--username',help='Wiki username')
    parser.add_argument('-p','--password', help='Wiki password')
    parser.add_argument('-c','--config',help='Read login information from file',
                        default=os.path.expanduser('~')+'/.conf.metanet')
    parser.add_argument('-s','--server',help='Server (and port) hosting the Wiki site',
                        default=DEFAULT_SERVER)
    parser.add_argument('--protocol',help='Protocol to connect to the server with',
                        default='https')
    parser.add_argument('--certificate',help='Path to self-signed certificate',
                        default=wikietcpath + '/metanet.cert.pem')
    parser.add_argument('scriptpath',help="ScriptPath of the wiki on the server",
                        default=DEFAULT_SCRIPT_PATH)
    cmdline = parser.parse_args()
    
    # read wiki login information from config file.
    config = {}
    if os.path.exists(cmdline.config):
        with open(cmdline.config, 'r') as f:
            for line in f:
                if line.isspace():
                    continue
                line = line.strip()
                if line.startswith('#'):
                    continue
                if '=' in line:
                    variable, value = line.split('=',1)
                    config[variable] = value
    if (not cmdline.username) and ('MNWIKI_USER' in config):
        cmdline.username = config['MNWIKI_USER']
    if (not cmdline.password) and ('MNWIKI_PW' in config):
        cmdline.password = config['MNWIKI_PW']

    return cmdline

def setup_logging(verbose):
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if verbose:
        loglevel=logging.INFO
    else:
        loglevel=logging.WARN
    logging.basicConfig(format=msgformat, datefmt=dateformat,
                        level=loglevel)

def updatelocalfile(pfpath,mpfpath,text,mdata):
    with codecs.open(pfpath,'w',encoding='utf-8') as ofile:
        print(text, file=ofile)
        os.utime(pfpath,(mdata['atime'],mdata['mtime']))
        with codecs.open(mpfpath,"w",encoding='utf-8') as metaf:
            ujson.dump(mdata,metaf,ensure_ascii=True)

def main ():
    params = get_parameters()
    setup_logging(params.verbose)
        
    if (not params.username or not params.password):
        logging.error(u'Error: incomplete login credentials')
        sys.exit()

    logging.info('Connecting to %s://%s%s/ as %s via API',
                 params.protocol, params.server,
                 params.scriptpath, params.username)
    
    wikietcpath=os.path.dirname(os.path.realpath(__file__))
    session = requests.Session()
    session.verify = params.certificate
    session.auth = None
    session.headers['User-Agent'] = 'MwClient/' + mwclient.client.__ver__ + ' (https://github.com/mwclient/mwclient)'
            
    site = mwclient.Site((params.protocol,params.server),path=params.scriptpath+'/',pool=session)
    site.login(params.username,params.password)

    get_by_namespace = {'Glossary':502,
                        'Metaphor':550,
                        'Frame':552,
                        'Metaphor_family':554,
                        'Frame_family':556,
                        'Construct_analysis':560,
                        'CxnMP':562,
                        'MetaRC':564,
                        'IConcept':570,
                        'Template':10,
                        'Category':14,
                        'Property':102,
                        'Form':106,
                        'Cit':800,
                        'MediaWiki':8,
                        'default':0
                        }
 
    # retrieve page names by namespace
    lastupdatedfname='.lastupdated'
    pagestosync=[]

    # record updated time at the start of the process    
    newupdatedtime = datetime.utcnow()
    newupdatedtstamp = newupdatedtime.strftime('%Y%m%d%H%M%S')

    if not os.path.exists(lastupdatedfname):
        for nsname, ns in get_by_namespace.iteritems():
            logging.info("retrieving page names from namespace %s", nsname)
            if not os.path.exists(nsname):
                os.mkdir(nsname)
            result = site.api('query',list='allpages',apnamespace=ns,aplimit=5000)
            for r in result['query']['allpages']:
                pagestosync.append({'title':r['title']})
    else:
        with open(lastupdatedfname,'r') as ltimef:
            lastupdatedtstamp=ltimef.read().strip()
            lastupdatedtime = datetime.strptime(lastupdatedtstamp,'%Y%m%d%H%M%S')
            localtimestruct=time.localtime(calendar.timegm(lastupdatedtime.utctimetuple()))
            logging.info('retrieving changed pages since %s',
                         time.strftime('%Y-%m-%d %H:%M:%S %Z',localtimestruct))
            result = site.api('query',list='recentchanges',
                              rcprop='user|title|comment|timestamp',
                              rctoponly='1',rcstart=lastupdatedtstamp,rcdir='newer')
            try:
                for r in result['query']['recentchanges']:
                    pagestosync.append(r)
            except:
                logging.error(u'Unexpected result: %s',pprint.pformat(result))
                raise
                
    for pageinfo in pagestosync:
        fullpagename = pageinfo['title']
        
        # retrieve latest revision from wiki
        page = site.Pages[fullpagename]
        pagename = page.page_title
        if u':' in fullpagename:
            nsname = fullpagename[:fullpagename.find(u':')]
        else:
            nsname = 'default'
        if not os.path.exists(nsname):
            os.mkdir(nsname)
        pagefilename = pagename.replace(u' ',u'_').replace(u'/',u'___')
        pagemetafilename = '.meta-'+pagefilename
        text = page.text()
        rev = page.revision
        rtime = page.last_rev_time # a UTC struct_time
        rtimestamp = calendar.timegm(rtime)
        modtime = datetime.fromtimestamp(rtimestamp) # localtime datetime
        atimestamp = time.time()
        wiki_mdata = {'wiki':params.protocol+'://'+params.server+params.scriptpath+'/',
                      'title':fullpagename,
                      'rev':int(rev),
                      'mtime':rtimestamp,
                      'atime':atimestamp}

        pagefilepath = nsname+'/'+pagefilename
        pagemetafilepath = nsname+'/'+pagemetafilename
        
        # possibilities
        if os.path.exists(pagemetafilepath):
            # update only if the wiki version is newer
            file_mdata = {}
            with codecs.open(pagemetafilepath,'r',encoding='utf-8') as pmf:
                file_mdata = ujson.load(pmf)
                if wiki_mdata['mtime'] > file_mdata['mtime']:
                    updatelocalfile(pagefilepath, pagemetafilepath, text, wiki_mdata)
        else:
            # then this is a new retrieval
            updatelocalfile(pagefilepath, pagemetafilepath, text, wiki_mdata)
                    
    # if we got here, update the record for last updated time    
    with codecs.open(lastupdatedfname,'w',encoding='utf-8') as ltimef:
        print (newupdatedtstamp, file=ltimef)
    
if __name__ == "__main__":
    status = main()
    sys.exit(status)
