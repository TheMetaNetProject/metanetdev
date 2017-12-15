#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Script that imports XML dumps of wiki pages into a wiki instance.

In addition it does replacements to the XML content to convert references
to schema to frame, and to get rid of references to VettedSchema and
VettedMetaphor.

jhong@icsi
"""

from __future__ import print_function

# workaround for urllib3/python<2.7.9 InsecurePlatformWarning issue
import urllib3.contrib.pyopenssl

urllib3.contrib.pyopenssl.inject_into_urllib3()

import requests
import os, sys, argparse, logging, pprint, codecs, itertools, re, setproctitle, mwclient
from subprocess import call, check_output
from glob import glob
from xml.etree import ElementTree
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

DEFAULT_SITE = 'metaphor.icsi.berkeley.edu'
DEFAULT_SERVER = 'http://ambrosia2.icsi.berkeley.edu'


def get_parameters():
    wikietcpath = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Script for importing XML-format wiki page dumps into " \
                    "a MediaWiki instance.  Must be run locally on the server hosting " \
                    "the wiki. Must be run from the directory that contains the wiki " \
                    "dump files.")
    parser.add_argument('dumpprefix',
                        help='Prefix to use for all page name dumps')
    parser.add_argument('-s', '--server',
                        help='Server protocol and address',
                        default=DEFAULT_SERVER)
    parser.add_argument('-w', '--wikiroot', required=True,
                        help='Root directory of wiki instance')
    parser.add_argument('-d', '--dumpdir', help='Directory containing wikidumps',
                        default=os.getcwd())
    parser.add_argument('-n', '--noimport', action='store_true',
                        help='Do substitutions but do not import')
    parser.add_argument('--skip-import', dest='skipimport', action='store_true',
                        help='Skip import and go to post-processing')
    parser.add_argument('--skip-users', dest='skipusers', action='store_true',
                        help='Skip import of user login info')
    parser.add_argument('--skip-rebuild', dest='skiprebuild', action='store_true',
                        help='Skip rebuilding (as when no templates changed)')
    parser.add_argument('--sdir', dest='settingsdir', default=wikietcpath,
                        help='Directory from which to copy preset settings.')
    parser.add_argument('--users-only', dest='usersonly', help='Import users only, then exit.',
                        action='store_true')
    parser.add_argument('--subs', help='Do schema to frame substitutions',
                        action='store_true')
    parser.add_argument('--pub', help='Do public website filtering of internal-only data',
                        action='store_true')
    parser.add_argument('--procs', help='Number of processes to run in parallel'
                                        ' for jobs processing', type=int, default=2)
    parser.add_argument('--socket', help='MySQL database socket')
    parser.add_argument('--host', help='MySQL database host', default='127.0.0.1')
    parser.add_argument('--port', help='MySQL database port', default='3306')
    parser.add_argument('--wikiuser', help='Wiki username (admin or bot)', default='Mnadmin')
    parser.add_argument('--wikipw', help='Wiki password')
    parser.add_argument('-p', '--page-overrides-dir', dest='pageoverridesdir',
                        help='Directory containing pages to override')
    parser.add_argument('--certificate', help='Path to self-signed certificate',
                        default=wikietcpath + '/metanet.cert.pem')
    parser.add_argument('--no-certificate', action='store_true', dest='nocertificate',
                        help='Do not use stored certificate to connect to API')
    parser.add_argument('--remapuids',
                        help=("Remap user ids on import to not conflict"
                              " with those in the given file"))
    parser.add_argument('--nosession', action='store_true',
                        help='Initialize mwclient without custom session')
    cmdline = parser.parse_args()

    # obscure passwords if entered in through cmdline
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(--wikiuser|--wikipw)(=|\s+)(\S+)', ur'\1\2XXXX', pstr)
    setproctitle.setproctitle(pstr)

    cmdline.wikiroot = os.path.abspath(cmdline.wikiroot)
    cmdline.dumpdir = os.path.abspath(cmdline.dumpdir)

    return cmdline


def multiwordReplace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile(u'|'.join(wordDic), flags=re.U)

    def translate(match):
        return wordDic[match.group(0)]

    return rc.sub(translate, text)


def main():
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    logging.basicConfig(format=msgformat, datefmt=dateformat,
                        level=logging.INFO)

    params = get_parameters()

    # title replacement (schema -> frame)
    titleDict = {
        u'Schema': u'Frame',
        u'schema': u'frame',
        u'SCHEMA': u'FRAME'
    }
    nsprefDict = {}

    # translate localized namespaces
    nsDict = {
        u'Plantilla':  u'Template',
        u'Atributo':   u'Property',
        u'Categoría':  u'Category',
        u'Formulario': u'Form',
        u'Шаблон':     u'Template',
        u'Свойство':   u'Property',
        u'Категория':  u'Category',
        u'Форма':      u'Form',
        u'الگو':       u'Template',
        u'رده':        u'Category',
        u'فرم':        u'Form',
        u'مدیاویکی':   u'MediaWiki'
    }
    for key, item in nsDict.iteritems():
        nsprefDict[key + u':'] = item + u':'

    # to fix image-schemas
    ximageDict = {
        u'x-frame':     u'x-schema',
        u'X-frame':     u'X-schema',
        u'image frame': u'image schema',
        u'Image frame': u'Image schema'
    }

    # getting rid of Vetted prefix
    vettedDict = {
        u'Category:Vetted': u'Category:',
        u'mo:Vetted':       u'mo:'
    }

    # file types to import (some are namespaces, some are categories)
    ftypes = [u'MediaWiki',
              u'Category',
              u'Property',
              u'Template',
              u'Form',
              u'Definition',
              u'Glossary',
              u'Glossary_talk',
              u'Cit',
              u'Construct_analysis',
              u'CxnMP',
              u'MetaRC',
              u'IARPASourceConcept',
              u'IARPATargetConcept',
              u'Schema',
              u'Frame',
              u'Metaphor',
              u'Schema_family',
              u'Frame_family',
              u'Metaphor_family',
              u'Frame_talk',
              u'Metaphor_talk',
              u'Frame_family_talk',
              u'Metaphor_family_talk',
              u'default']

    # import user accounts and groups
    # determine database login/pw
    dbUser = None
    dbPw = None
    dbName = None
    scriptPath = None
    with codecs.open(params.wikiroot + '/LocalSettings.php', encoding='utf-8') as lf:
        varpat = re.compile(ur'\$(\w+)\s+=\s+"([^"]+)";', flags=re.U)
        for line in lf:
            m = varpat.match(line)
            if not m:
                continue
            if m.group(1) == 'wgDBuser':
                dbUser = m.group(2)
            elif m.group(1) == 'wgDBpassword':
                dbPw = m.group(2)
            elif m.group(1) == 'wgDBname':
                dbName = m.group(2)
            elif m.group(1) == 'wgScriptPath':
                scriptPath = m.group(2)
            if dbUser and dbPw and dbName and scriptPath:
                break
    # this map lists uname => uid maps that should be used to fix those
    # in the talk xml dump files
    talk_xml_remap = {}
    if dbUser and dbPw and dbName:
        if (not params.skipimport) and (not params.skipusers):
            userdumpf = '%s/%s-userdump.sql' % (params.dumpdir, params.dumpprefix)
            if params.remapuids:
                maxid = 0
                uidmap = {}
                uidrevmap = {}
                with codecs.open(params.remapuids, 'r', encoding='utf8') as f:
                    for line in f:
                        m = re.match("INSERT .* VALUES \((\d+),'([^']+)',",
                                     line)
                        if m:
                            uid = int(m.group(1))
                            uname = m.group(2)
                            if uid > maxid:
                                maxid = uid
                            uidmap[uname] = uid
                            uidrevmap[uid] = uname
                # uname => uid mappings to fix in the talk xml dumps and in the
                #          talk user sql dump
                talk_user_inserts = ['LOCK TABLES `user` WRITE;']
                with codecs.open(userdumpdf, 'r', encoding='utf8') as f:
                    for line in f:
                        m = re.search("^(INSERT .* VALUES \()(\d+),'([^']+)',(.*)$", line)
                        if m:
                            uid = int(m.group(2))
                            uname = m.group(3)
                            if uname in uidmap:
                                # this username is already in the internal wiki
                                if uid != uidmap[uname]:
                                    # if the uid doesn't match we need substitute the
                                    # ids in the talk xml files to the ones from the internal
                                    talk_xml_remap[uname] = uidmap[uname]
                                    # we do not need to include user however in the talk users
                                    # sql dump, since it's already there from internal
                                    # if the id matches, then we really don't need to do anything
                            else:
                                # this username is not already in the internal wiki
                                if uid in uidrevmap:
                                    # if the uid is already being used in the internal wiki
                                    # we need to re-assign it, and we need to subst all the
                                    # talk pages accordingly
                                    maxid += 1
                                    talkuidmap[uname] = maxid
                                    q = u'%s%d,\'%s\',%s' % (m.group(1), maxid, uname, m.group(4))
                                    talk_user_inserts.append(q)
                                else:
                                    # if the uid is not being used we can leave the references
                                    # as is in the xml files, and import users as is
                                    talk_user_inserts.append(line.rstrip())
                # make a new user dumpf file
                userdumpf = '%s/proc-%s-userdump.sql' % (params.dumpdir, params.dumpprefix)
                talk_user_inserts.append('UNLOCK TABLES;')
                with codecs.open(userdumpf, 'w', encoding='utf8') as f:
                    print(talk_user_inserts, sep='\n', file=f)
            importcmd = ['mysql', '-u', dbUser, '--password=' + dbPw, dbName]
            with codecs.open(os.path.abspath(userdumpf), encoding='utf-8') as stdinf:
                call(importcmd, stdin=stdinf)

            connection_params = {
                'unix_socket': params.socket,
                'user': dbUser,
                'passwd': dbPw,
                'db': dbName
            } if params.socket else {
                'host': params.dbhost,
                'port': params.dbport,
                'user': dbUser,
                'passwd': dbPw,
                'db': dbName
            }

            # now need to process groups
            con = MySQLdb.connect(**connection_params)
            cursor = con.cursor()
            with codecs.open(params.settingsdir + '/user-groups.txt', encoding='utf-8') as ugf:
                for line in ugf:
                    cline = line.strip()
                    if (not cline) or cline.startswith(u'#'):
                        continue
                    uname, groupstr = cline.split(u':')
                    groups = groupstr.split(u',')
                    for group in groups:
                        q = 'INSERT INTO user_groups (ug_user, ug_group) ' \
                            'SELECT user_id, %s FROM user ' \
                            'WHERE user_name=%s'
                        cursor.execute(q, (group.strip(), uname.strip()))
            # inserts are not saved until they are committed
            con.commit()
    else:
        logging.error('Could not import user login info into the database')

    if params.usersonly:
        logging.info('Exiting after user data import')
        sys.exit()

    os.chdir(params.wikiroot + '/maintenance')
    mwns = 'http://www.mediawiki.org/xml/export-0.9/'
    ElementTree.register_namespace('', mwns)
    if params.skipimport:
        ftypes = []
    for ftype in ftypes:
        xmlfpath = u'%s/%s-%s.xml' % (params.dumpdir, params.dumpprefix, ftype)
        if (ftype == 'Definition') and ((not os.path.exists(xmlfpath)) or
                                            (os.stat(xmlfpath).st_size == 0)):
            xmlfpath = u'%s/../metaphor/%s-%s.xml' % (params.dumpdir, params.dumpprefix,
                                                      ftype)
        if (not os.path.exists(xmlfpath)) or (os.stat(xmlfpath).st_size == 0):
            logging.info('page import: skipping %s: no file or zero size',
                         xmlfpath)
            continue
        if params.subs or params.pub:
            tree = ElementTree.parse(xmlfpath)
            root = tree.getroot()

            if params.subs:
                for node in root.iter(u'{%s}namespace' % (mwns)):
                    if node.text:
                        if ((u'Schema' in node.text) or
                                (u'schema' in node.text) or (u'SCHEMA' in node.text)):
                            node.text = multiwordReplace(node.text, titleDict)
                        node.text = multiwordReplace(node.text, nsDict)

                for node in root.iter(u'{%s}title' % (mwns)):
                    if node.text and ((u'Schema' in node.text) or
                                          (u'schema' in node.text)):
                        node.text = multiwordReplace(node.text, titleDict)
                        node.text = multiwordReplace(node.text, ximageDict)
                        node.text = multiwordReplace(node.text, vettedDict)
                        # print(node.text)
                    if u'Metaphor_family' in xmlfpath:
                        if not node.text.startswith('Metaphor family:'):
                            node.text = u'Metaphor family:' + node.text
                    elif u'Schema_family' in xmlfpath:
                        if not node.text.startswith('Frame family:'):
                            node.text = u'Frame family:' + node.text
                    elif u'Definition' in xmlfpath:
                        if not node.text.startswith('Glossary:'):
                            node.text = u'Glossary:' + node.text
                    elif u'Category' in xmlfpath:
                        if node.text == u'Category:Definition':
                            node.text = u'Category:Glossary'
                    elif u'Template' in xmlfpath:
                        if node.text.startswith(u'Template:Definition'):
                            node.text = node.text.replace(u'Definition',
                                                          u'Glossary')
                    elif u'Form' in xmlfpath:
                        if node.text == u'Form:Definition':
                            node.text = u'Form:Glossary'
                    elif u'Property' in xmlfpath:
                        if node.text.startswith(u'Property:Definition'):
                            node.text = node.text.replace(u'Definition',
                                                          u'Glossary')
                    node.text = multiwordReplace(node.text, nsprefDict)

                # set namespace for Metaphor/Frame families
                if u'Metaphor_family' in xmlfpath:
                    for node in root.iter(u'{%s}ns' % (mwns)):
                        node.text = u'554'
                elif u'Schema_family' in xmlfpath:
                    for node in root.iter(u'{%s}ns' % (mwns)):
                        node.text = u'556'
                elif u'Definition' in xmlfpath:
                    for node in root.iter(u'{%s}ns' % (mwns)):
                        node.text = u'501'

                for node in root.iter(u'{%s}text' % (mwns)):
                    if not node.text:
                        continue
                    if (u'Schema' in node.text) or (u'schema' in node.text):
                        node.text = multiwordReplace(node.text, titleDict)
                        node.text = multiwordReplace(node.text, ximageDict)
                        node.text = multiwordReplace(node.text, vettedDict)
                        # print(node.text)
                    if u'#set_internal:' in node.text:
                        node.text = node.text.replace(u'#set_internal:', '#subobject:')
                    if u'Template' in xmlfpath:
                        if (u'{{Metaphor' in node.text):
                            node.text = node.text.replace(u'[[Metaphor.Family::x]]',
                                                          u'[[Metaphor.Family::Metaphor family:x|x]]')
                        elif (u'{{Frame' in node.text):
                            node.text = node.text.replace(u'[[Frame.Family::x]]',
                                                          u'[[Frame.Family::Frame family:x|x]]')
                        elif (u'{{Metaphor family' in node.text):
                            node.text = node.text.replace(u'[[Metaphor subfamily of::x]]',
                                                          u'[[Metaphor subfamily of::Metaphor family:x|x]]')
                            node.text = node.text.replace(u'{{PAGENAME}}',
                                                          u'{{FULLPAGENAME}}')
                            node.text = node.text.replace(u'Printgloss|{{FULLPAGENAME}}',
                                                          u'Printgloss|{{PAGENAME}}')
                        elif (u'{{Frame family' in node.text):
                            node.text = node.text.replace(u'[[Frame subfamily of::x]]',
                                                          u'[[Frame subfamily of::Frame family:x|x]]')
                            node.text = node.text.replace(u'{{PAGENAME}}',
                                                          u'{{FULLPAGENAME}}')
                            node.text = node.text.replace(u'Printgloss|{{FULLPAGENAME}}',
                                                          u'Printgloss|{{PAGENAME}}')
                        elif (u'{{Metaphor family tree' in node.text):
                            node.text = node.text.replace(u'[[{{{1|}}}]]',
                                                          u'[[{{{1|}}}|{{#replace:{{{1|}}}|Metaphor_family:|}}]]')
                        elif (u'{{Frame family tree' in node.text):
                            node.text = node.text.replace(u'[[{{{1|}}}]]',
                                                          u'[[{{{1|}}}|{{#replace:{{{1|}}}|Frame_family:|}}]]')
                        elif (u'[[Definition.Entry::' in node.text):
                            node.text = node.text.replace(u'Definition',
                                                          u'Glossary')
                        elif (u'DefinitionLink' in node.text):
                            node.text = node.text.replace(u'DefinitionLink',
                                                          u'GlossaryLink')
                        elif (u'DefinitionListing' in node.text):
                            node.text = node.text.replace(u'DefinitionListing',
                                                          u'GlossaryListing')

                    if ('default' in xmlfpath):
                        if (u'{{Metaphor family tree' in node.text):
                            node.text = node.text.replace(u'{{Unsetpropnns|topfams',
                                                          u'{{Unsetprop|topfams')
                        if (u'{{Frame family tree' in node.text):
                            node.text = node.text.replace(u'{{Unsetpropnns|topfams',
                                                          u'{{Unsetprop|topfams')
                    if ('Category' in xmlfpath):
                        if (u'The glossary provides' in node.text):
                            node.text = node.text.replace(u'Definition',
                                                          u'Glossary')
                    if ('Form' in xmlfpath):
                        if (u'{{{for template|Definition}}}' in node.text):
                            node.text = node.text.replace(u'Definition',
                                                          u'Glossary')
                    if ('Definition' in xmlfpath):
                        node.text = node.text.replace(u'Definition',
                                                      u'Glossary')

                for node in root.iter(u'{%s}comment' % (mwns)):
                    if node.text and ((u'Schema' in node.text) or
                                          (u'schema' in node.text)):
                        node.text = multiwordReplace(node.text, titleDict)
                        node.text = multiwordReplace(node.text, ximageDict)
                        node.text = multiwordReplace(node.text, vettedDict)
                        # print(node.text)
            if params.pub:
                if ('Frame' in xmlfpath) or ('Metaphor' in xmlfpath):
                    for node in root.iter(u'{%s}text' % (mwns)):
                        if not node.text:
                            continue
                        ntextlines = []
                        # delete Comments, Entered by, and Last reviewed by
                        skip_variable = False
                        for line in node.text.split('\n'):
                            if skip_variable:
                                if line.startswith('|') or line.startswith('}}'):
                                    skip_variable = False
                                else:
                                    continue
                            if (line.startswith(u'|Comments=') or
                                    line.startswith(u'|Entered by=') or
                                    line.startswith(u'|Last reviewed by=')):
                                skip_variable = True
                                continue
                            ntextlines.append(line)
                        # delete lines past the last }} (free text)
                        for i in range(len(ntextlines)):
                            if ntextlines[-1].startswith(u'}}'):
                                break
                            ntextlines.pop()
                        node.text = u'\n'.join(ntextlines)
                        # replace uid's in the (talk) xml files as per the map
            if params.remapuids and talk_xml_remap:
                for node in root.iter(u'{%s}contributor' % (mwns)):
                    unamenode = node.find(u'{%s}username' % (mwns))
                    if unamenode.text in talk_xml_remap:
                        node.find(u'{%s}id' % (mwns)).text = talk_xml_remap[unamenode.text]

            basedir, fname = os.path.split(xmlfpath)
            oxmlfpath = '%s/proc-%s' % (basedir, fname)
            tree.write(oxmlfpath, encoding='utf-8', xml_declaration=True)
        else:
            oxmlfpath = xmlfpath

        if params.noimport:
            continue

        importcmd = ['php', 'importDump.php',
                     '--server=' + params.server, oxmlfpath]
        logging.info('importing page dump %s', oxmlfpath)
        call(importcmd)

    if params.noimport:
        return

    if params.pageoverridesdir:
        if os.path.exists(params.pageoverridesdir):
            # connect to api
            urlmatch = re.search('^(http|https)://(.*)$', params.server)
            protocol = urlmatch.group(1)
            server = urlmatch.group(2)
            logging.info('Connecting to %s://%s%s/ as %s',
                         protocol, server,
                         scriptPath,
                         params.wikiuser)

            session = requests.Session()
            session.verify = params.certificate
            session.auth = None
            session.headers['User-Agent'] = 'MwClient/' + mwclient.client.__ver__ + ' (https://github.com/mwclient/mwclient)'

            # override the self-signed certificate
            if params.nocertificate:
                session = None

            # trying with default session settings (otherwise, pool=session would be an argument)
            if params.nosession:
                site = mwclient.Site((protocol, server), path=scriptPath + '/')
            else:
                site = mwclient.Site((protocol, server), path=scriptPath + '/', pool=session)
            site.login(params.wikiuser, params.wikipw)
            for pfname in os.listdir(params.pageoverridesdir):
                pfpath = os.path.join(params.pageoverridesdir, pfname)
                if not os.path.isfile(pfpath):
                    continue
                pname = pfname.replace('___', ':')
                ptext = ''
                with codecs.open(pfpath, encoding='utf-8') as pf:
                    ptext = pf.read()
                page = site.Pages[pname]
                try:
                    page.save(ptext,
                              summary='overridden at import')
                except:
                    logging.error('Error saving page %s, with content from %s; conn to %s %s %s as (%s, %s)',
                                  pname, pfpath, protocol, server, scriptPath, params.wikiuser, params.wikipw)
                    raise
        else:
            logging.error('Overrides directory %s does not exist', params.pageoverridesdir)

    # rebuild all
    if not params.skiprebuild:
        rebuildcmd = ['php', 'rebuildall.php', '--server=' + params.server]
        call(rebuildcmd)

    # rebuild semantics
    # os.chdir(params.wikiroot + '/extensions/SemanticMediaWiki/maintenance')
    # rebuildcmd = ['php', 'rebuildData.php', '--runtime']
    # call(rebuildcmd)

    # run all outstanding jobs: run 20 iterations of 1000 jobs, using 10 cpus
    for _ in range(20):
        jobscmd = ['php', 'runJobs.php', '--maxjobs=500', '--proc=%d' % (params.procs),
                   '--server=' + params.server]
        call(jobscmd)


if __name__ == "__main__":
    status = main()
    sys.exit(status)
