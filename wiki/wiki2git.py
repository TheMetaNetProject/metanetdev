#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for populating and updating a local git repository with page
revisions from a local MediaWiki installation.  This script requires
direct database access to MediaWiki's MySQL backend.

jhong@icsi
"""

from __future__ import print_function
import urllib3.contrib.pyopenssl
from _sqlite3 import Row
urllib3.contrib.pyopenssl.inject_into_urllib3()
import argparse, calendar, codecs, getpass, logging, os, re, setproctitle, sys, time
import mwclient, requests, MySQLdb, pprint
from subprocess import call
from sh import git
from datetime import datetime, timedelta
from bisect import bisect
from subprocess import check_output

DEFAULT_SCRIPT_PATH='/dev/en'
DEFAULT_SERVER='ambrosia.icsi.berkeley.edu:2080'

def get_parameters():
    """ Parse command-line parameters an return as a dictionary.
    """
    wikietcpath=os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Script for populating a local git repository with "\
                    "page revision from a local MediaWiki.")
    parser.add_argument('-v','--verbose',help='Display status messages',
                        action='store_true')
    parser.add_argument('--wikiuser',help='Wiki username')
    parser.add_argument('--wikipw', help='Wiki password')
    parser.add_argument('--wikiconf',help='Read login information from file',
                        default=os.path.expanduser('~')+'/.conf.metanet')
    parser.add_argument('--wikiserver',help='Server (and port) hosting the Wiki site',
                        default=DEFAULT_SERVER)
    parser.add_argument('--protocol',help='Protocol to connect to the server with',
                        default='https')
    parser.add_argument('--certificate',help='Path to self-signed certificate',
                        default=wikietcpath + '/metanet.cert.pem')
    parser.add_argument('scriptpath',help="ScriptPath of the wiki on the server",
                        default=DEFAULT_SCRIPT_PATH)
    parser.add_argument('-u','--dbuser',help='Db username',
                        default='readonly_user')
    parser.add_argument('-p','--dbpw',help='Db password',
                        default='readme')
    parser.add_argument('-d','--dbname',help='Db name',required=True)
    parser.add_argument('-s','--socket',help='Db socket',default='/tmp/mysql.sock')
    parser.add_argument('-r','--repository',help='Git repository root directory',
                        default='.')
    parser.add_argument('-n','--new',action='store_true',
                        help='Builds a new git repository rather than updating.')
    cmdline = parser.parse_args()
    # obscure passwords if entered in through cmdline
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(--wikiuser|--wikipw|--dbuser|--dbpw|-u|-p)(=|\s+)(\S+)',ur'\1\2XXXX',pstr)
    setproctitle.setproctitle(pstr)
    if not cmdline.dbpw:
        cmdline.dbpw = getpass.getpass('Enter database admin password: ')
    
    # read wiki login information from config file.
    config = {}
    if os.path.exists(cmdline.wikiconf):
        with open(cmdline.wikiconf, 'r') as f:
            for line in f:
                if line.isspace():
                    continue
                line = line.strip()
                if line.startswith('#'):
                    continue
                if '=' in line:
                    variable, value = line.split('=',1)
                    config[variable] = value
    if (not cmdline.wikiuser) and ('MNWIKI_USER' in config):
        cmdline.wikiuser = config['MNWIKI_USER']
    if (not cmdline.wikipw) and ('MNWIKI_PW' in config):
        cmdline.wikipw = config['MNWIKI_PW']
    
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

def splitns(title):
    nsmarker_idx = title.find(u':')
    if nsmarker_idx > 0:
        return (title[:nsmarker_idx],title[nsmarker_idx+1:])
    else:
        return (u'default', title[nsmarker_idx+1:])

def processrevision(rev):
    """ Receives a row tuple representing revision information, and 
    adds and commits it to a local git repositiory.
    """
    rev['author'] = rev['username']+u' <'+rev['email']+u'>'
    revdatetime = datetime.strptime(rev['tstamp'],'%Y%m%d%H%M%S')
    rev['datetime'] = revdatetime
    rev['authordate'] = revdatetime.isoformat() + 'Z'
    try:
        logging.info(u'processing rev %d (%s) of %s (%s) by %s',
                     rev['id'],rev['authordate'],
                     rev['ns']+':'+rev['title'].decode('utf-8'),rev['comment'].decode('utf-8'),rev['author'])
    except:
        logging.warn(u'Warning: trouble processing rev: %s',pprint.pformat(rev))
        raise
    rev['pfname'] = rev['title'].decode('utf-8').replace(u'/',u'___')
    rev['pfpath'] = rev['ns'] + u'/' + rev['pfname']
    rev['gitcomment'] = rev['comment'].decode('utf-8') + u'\nwiki_'+rev['type']+u'_id=' + str(rev['id'])
    return rev

def addgitcommit(rev):    
    mtime = calendar.timegm(time.strptime(rev['authordate'], '%Y-%m-%dT%H:%M:%SZ'))
    if not os.path.exists(rev['ns']):
        os.mkdir(rev['ns'])
    with codecs.open(rev['pfpath'],'w',encoding='utf-8') as pf:
        print(rev['text'].decode('utf-8'),file=pf)
    os.utime(rev['pfpath'],(time.time(),mtime))
    git.add(rev['pfpath'])
    # use --allow-empty so that commit works even if the page content didn't change
    # this is to preserve the messages
    git.commit(rev['pfpath'],author=rev['author'],date=rev['authordate'],m=rev['gitcomment'],allow_empty=True)

def main ():
    params = get_parameters()
    setup_logging(params.verbose)
        
    if (not params.dbuser or not params.dbpw):
        logging.error(u'Error: incomplete database login credentials')
        sys.exit(-1)

    # connect via API to retrieve namespaces
    logging.info('Connecting to wiki %s://%s%s/ as %s via API',
                 params.protocol, params.wikiserver,
                 params.scriptpath, params.wikiuser)
    
    session = requests.Session()
    session.verify = params.certificate
    session.auth = None
    session.headers['User-Agent'] = 'MwClient/' + mwclient.client.__ver__ + ' (https://github.com/mwclient/mwclient)'
            
    site = mwclient.Site((params.protocol,params.wikiserver),path=params.scriptpath+'/',pool=session)
    site.login(params.wikiuser,params.wikipw)

    result = site.api('query',meta='siteinfo',siprop='namespaces')
    namespaces = {}
    try:
        for nsid, nsdict in result['query']['namespaces'].iteritems():
            if nsid==u'0':
                namespaces[nsid] = 'default'
            else:
                namespaces[nsid] = nsdict['canonical']
    except:
        logging.error(u'Error in api result: %s',pprint.pformat(result))
        
    # connect via database to retrieve page/revision content
    con = MySQLdb.connect(unix_socket=params.socket,
                          user=params.dbuser,
                          passwd=params.dbpw,
                          db=params.dbname,
                          charset='utf8',
                          use_unicode=True)
    cursor = con.cursor()

    returncode = 0
    
    # pages in these namespaces are used to generate the RDF
    rdfnamespaces = set(['Metaphor',
                         'Frame',
                         'Metaphor_family',
                         'Frame_family',
                         'MetaRC',
                         'CxnMP'])

    if params.new:
        # populate a new git repository; returncode = 1 signals that RDF should be regenerated
        returncode = 1
        
        # query written so as not to return revisions in which the wiki text has not
        # changed at all    
        revq = """\
            (SELECT r.rev_id as 'rev_id', p.page_namespace, p.page_title, t.old_text, r.rev_comment,
                    r.rev_timestamp, u.user_name, u.user_email, 'revision'
            FROM revision AS r INNER JOIN page AS p ON r.rev_page = p.page_id
                INNER JOIN text AS t ON r.rev_text_id = t.old_id
                INNER JOIN user AS u ON r.rev_user=u.user_id
                LEFT JOIN revision AS oldr ON r.rev_parent_id = oldr.rev_id
            WHERE r.rev_parent_id=0 OR 
                (t.old_text <> (SELECT t2.old_text
                                FROM revision AS r2
                                    INNER JOIN text AS t2 ON r2.rev_text_id=t2.old_id
                                WHERE r2.rev_id=r.rev_parent_id)))
            UNION ALL
            (SELECT a.ar_rev_id as 'rev_id', a.ar_namespace, a.ar_title, t.old_text, a.ar_comment,
                    a.ar_timestamp, u.user_name, u.user_email, 'archive'
            FROM archive AS a INNER JOIN text AS t ON a.ar_text_id = t.old_id
                INNER JOIN user AS u ON a.ar_user=u.user_id
                LEFT JOIN archive AS olda ON a.ar_parent_id = olda.ar_rev_id
            WHERE a.ar_parent_id=0 OR
                (t.old_text <> (SELECT t2.old_text
                                FROM archive AS a2
                                    INNER JOIN text AS t2 ON a2.ar_text_id=t2.old_id
                                WHERE a2.ar_rev_id=a.ar_parent_id)))
            ORDER BY rev_id ASC"""
        
        # retrieve deletion log events
        deltimequery = """\
            SELECT l.log_timestamp, u.user_name, u.user_email, l.log_comment, l.log_action
            FROM logging AS l, user AS u
            WHERE log_type = "delete" AND log_namespace=%s AND log_title=%s
                AND l.log_user=u.user_id
            ORDER BY log_timestamp DESC"""
        
        deletionfiles = set()
        deletionqueue = []
        deletiontimes = []
        cursor.execute(revq)
        for row in cursor:
            rev = dict(zip(('id','nsid','title','text','comment',
                            'tstamp','username','email','type'), row))
            rev['ns'] = namespaces[str(rev['nsid'])].replace(u' ',u'_')
            rev = processrevision(rev)
            
            # check if a deletion should be executed
            while deletiontimes and (rev['datetime'] > deletiontimes[0]):
                delitem = deletionqueue.pop(0)
                deldatetime = deletiontimes.pop(0)
                logging.info(u'running deletion on %s',delitem['pfpath'])
                git.rm(delitem['pfpath'])
                git.commit(delitem['pfpath'],
                           author=delitem['author'],
                           date=delitem['authordate'],
                           m=delitem['comment'])
            
            addgitcommit(rev)
            if (rev['type']=='archive'):
                if rev['pfpath'] not in deletionfiles:
                    # look up a deletion log event
                    cursor.execute(deltimequery, (int(rev['nsid']),rev['title']))
                    (deltstamp, username, email, comment, action) = cursor.fetchone()
                    if action=='delete':
                        deldatetime = datetime.strptime(deltstamp,'%Y%m%d%H%M%S')
                        author = username+u' <'+email+u'>'
                        authordate = deldatetime.isoformat() + 'Z'
                        delcomment = comment.decode('utf-8')
                        del_idx = bisect(deletiontimes,deldatetime)
                        deletiontimes.insert(del_idx, deldatetime)
                        deletionqueue.insert(del_idx, {'datetime':deldatetime,
                                                       'author':author,
                                                       'authordate':authordate,
                                                       'comment':delcomment,
                                                       'pfpath':rev['pfpath']})
                        deletionfiles.add(rev['pfpath'])
        
        # process outstanding deletions
        while deletiontimes:
            delitem = deletionqueue.pop(0)
            deldatetime = deletiontimes.pop(0)
            git.rm(delitem['pfpath'])
            git.commit(delitem['pfpath'],
                       author=delitem['author'],
                       date=delitem['authordate'],
                       m=delitem['comment'])
    else:
        tstampstr = check_output(['git','log','-n','1','--format=%at']).strip()
        logging.info('Time stamp is %s', tstampstr)
        dtime = datetime.utcfromtimestamp(int(tstampstr))
        logging.info('Repository last log entry time: %s', dtime.isoformat()+'Z')
        dtime += timedelta(seconds=1)
        logging.info('Searching for log entries from time: %s',dtime.strftime('%Y%m%d%H%M%S'))
        # update the existing repository using the recentchanges API
        result = site.api('query',list='recentchanges',rcdir='newer',
                          rcstart=dtime.strftime('%Y%m%d%H%M%S'),
                          rcprop='loginfo|ids|userid|comment|title|timestamp')
        recentchanges = result['query']['recentchanges']
        while 'query-continue' in result:
            continueval = result['query-continue']['recentchanges']['rccontinue']
            result = site.api('query',list='recentchanges',rcdir='newer',
                              rcstart=dtime.strftime('%Y%m%d%H%M%S'),
                              rcprop='loginfo|ids|userid|comment|title|timestamp',
                              rccontinue=continueval)
            recentchanges.extend(result['query']['recentchanges'])
            
        revq = """\
            SELECT r.rev_id, p.page_namespace, p.page_title, t.old_text, r.rev_comment,
                    r.rev_timestamp, u.user_name, u.user_email, 'revision'
            FROM revision AS r INNER JOIN page AS p ON r.rev_page = p.page_id
                INNER JOIN text AS t ON r.rev_text_id = t.old_id
                INNER JOIN user AS u ON r.rev_user=u.user_id
            WHERE r.rev_id=%s"""
        
        userq = """\
            SELECT u.user_name, u.user_email FROM user as u WHERE u.user_id=%s
            """
        
        pageq = """\
            SELECT r.rev_id, p.page_namespace, p.page_title, t.old_text, r.rev_comment,
                    r.rev_timestamp, u.user_name, u.user_email, 'revision'
            FROM revision AS r INNER JOIN page AS p ON r.rev_id = p.page_latest
                INNER JOIN text AS t ON r.rev_text_id = t.old_id
                INNER JOIN user AS u ON r.rev_user=u.user_id
            WHERE p.page_id=%s"""
        
        for rc in recentchanges:
            logging.info(u'processing change: %s', pprint.pformat(rc))
            if rc['type'] in ('new','edit'):
                cursor.execute(revq,(int(rc['revid']),))
                row = cursor.fetchone()
                rev = dict(zip(('id','nsid','title','text','comment',
                                'tstamp','username','email','type'), row))
                rev['ns'] = namespaces[str(rev['nsid'])].replace(u' ',u'_')
                if rev['ns'] in rdfnamespaces:
                    returncode = 1
                rev = processrevision(rev)
                addgitcommit(rev)
            elif rc['type'] == 'log':
                ns = namespaces[str(rc['ns'])].replace(u' ',u'_')
                pfname = rc['title'].replace(u'/',u'___')
                pfpath = ns + u'/' + pfname
                revdatetime = datetime.strptime(rc['timestamp'],'%Y-%m-%dT%H:%M:%SZ')
                authordate = revdatetime.isoformat() + 'Z'
                cursor.execute(userq,(int(rc['userid']),))
                (user_name, user_email) = cursor.fetchone()
                author = user_name + u' <' + user_email +u'>'
                gitcomment = rc['comment'].decode('utf-8')
                # these events can be delete, restore, or move
                if rc['logaction'] in ['move','delete','restore']:
                    if ns in rdfnamespaces:
                        returncode = 1
                if rc['logaction'] == 'move':
                    if os.path.exists(pfpath):
                        newns = namespaces[str(rc['move']['new_ns'])].replace(u' ',u'_')
                        if newns in rdfnamespaces:
                            returncode = 1
                        newpfname = rc['move']['new_title'].replace(u'/',u'___')
                        newpfpath = newns + u'/' + newpfname 
                        git.mv(pfpath, newpfpath)
                        mtime = calendar.timegm(time.strptime(authordate, '%Y-%m-%dT%H:%M:%SZ'))
                        os.utime(newpfpath,(time.time(),mtime))
                        if not gitcomment:
                            gitcomment = u'%s renamed to %s' % (pfname, newpfname)
                        git.commit(newpfpath,author=author,date=authordate,m=gitcomment)
                elif rc['logaction'] == 'delete':
                    if os.path.exists(pfpath):
                        git.rm(pfpath)
                        if not gitcomment:
                            gitcomment = u'%s deleted' % (pfname)
                        git.commit(newpfpath,author=author,date=authordate,m=gitcomment)
                elif rc['logaction'] == 'restore':
                    cursor.execute(pageq,(int(rc['pageid']),))
                    row = cursor.fetchone()
                    rev = dict(zip(('id','nsid','title','text','comment',
                                    'tstamp','username','email','type'), row))
                    rev['ns'] = namespaces[str(rev['nsid'])].replace(u' ',u'_')
                    if rev['ns'] in rdfnamespaces:
                        returncode = 1
                    rev = processrevision(rev)
                    rev['gitcomment'] = gitcomment
                    rev['author'] = author
                    rev['authordate'] = authordate
                    addgitcommit(rev)
    return returncode

if __name__ == "__main__":
    status = main()
    sys.exit(status)
