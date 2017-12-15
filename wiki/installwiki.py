#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Script for installing and configuring a MetaNet wiki site.
#
#
from __future__ import print_function
from subprocess import call, Popen, PIPE, STDOUT
import argparse
import codecs
import getpass
import itertools
import logging
import MySQLdb
import os
import re
import setproctitle
import shutil
import sys
import traceback
import urllib2
from distutils.dir_util import copy_tree

# defaults
MWVERSION       = u'1.24.2'
MWTARBASE_TPL   = u'mediawiki-%s'
MWTARURL_TPL    = u'http://releases.wikimedia.org/mediawiki/%s/%s.tar.gz'
LANGUAGES       = [u'en', u'es', u'ru', u'fa']
GITCMD          = u'/usr/bin/git'
GERRITURLBASE   = u'https://gerrit.wikimedia.org/r/p/mediawiki/extensions'
SVNURLBASE      = u'http://svn.wikimedia.org/svnroot/mediawiki/trunk/extensions'
MNGITURLBASE    = u'ssh://ambrosia.icsi.berkeley.edu/u/metanet/git'

#
# LISTS OF EXTENSIONS BY INSTALLATION TYPE (COMPOSER, GIT, SVN, METANET, DEFAULT)
# 

# composer is the new dependency manager
COMPOSER_EXTENSIONS = {
    'mediawiki/semantic-media-wiki':     '*',
    'mediawiki/semantic-result-formats': '*',
    'mediawiki/semantic-forms':          '*'
}

# some extensions require additional setup commands
EXTRA_COMPOSER_COMMANDS = {
    'mediawiki/semantic-media-wiki': [
        ['php', 'maintenance/update.php']
    ]
}

# extensions retrieved via git
GIT_EXTENSIONS = ['AdminLinks',
                  'Arrays',
                  'CSS',
                  'CodeEditor',
                  'ConfirmAccount',
                  'ConfirmEdit',
                  'DataTransfer',
                  'DiscussionThreading',
                  'DismissableSiteNotice',
                  'DynamicSidebar',
                  'ExternalData',
                  'HeaderTabs',
                  'Lockdown',
                  'Loops',
                  'PageSchemas',
                  'ReplaceSet',
                  'ReplaceText',
                  'SemanticCompoundQueries',
                  'SemanticExtraSpecialProperties',
                  'SemanticFormsInputs',
                  'Variables',
                  'Widgets']

# This list used to contain Push, but it does't work so we
# removed it
DEV_GIT_EXTENSIONS = []

# some extensions require additional configuration steps
EXTRA_GIT_COMMANDS = {
    'Widgets': [[GITCMD, 'submodule', 'init'],
                [GITCMD, 'submodule', 'update']]
}

# some old extensions are still stored in svn
SVN_EXTENSIONS = []

# metanet custom extensions are retrieved from metanet's git
# repository
METANET_EXTENSIONS = ['PipeEscape',
                      'MetaNetGraph',
                      'JavaScript',
                      'FrameNetQuery']

# includes scriptsrelated to IARPA concept mapping
DEV_METANET_EXTENSIONS = ['MetaNetWikiTools']

# default extensions are bundled with MediaWiki but still need
# to be enabled
DEFAULT_EXTENSIONS = ['Cite',
                      'ConfirmEdit',
                      'Gadgets',
                      'ImageMap',
                      'InputBox',
                      'Interwiki',
                      'LocalisationUpdate',
                      'Nuke',
                      'ParserFunctions',
                      'Poem',
                      'Renameuser',
                      'SpamBlacklist',
                      'SyntaxHighlight_GeSHi',
                      'TitleBlacklist',
                      'WikiEditor']

# main page has to be localised
MAIN_PAGE = {
    'en': u'Main_Page',
    'es': u'Página_principal',
    'ru': u'Заглавная_страница',
    'fa': u'صفحهٔ_اصلی'
}


def get_parameters():
    global MWVERSION
    def_settings_dir = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Script for installing MetaNet Semantic MediaWiki site')
    parser.add_argument('-l', '--lang', help='Install for language',
                        required=True)
    parser.add_argument('--dbauser', help='Database admin username')
    parser.add_argument('--dbapw', help='Database admin password')
    parser.add_argument('--wikiuser', default='mnwikiuser',
                        help='Wiki to database connection username.')
    parser.add_argument('--wikipw', help='Wiki to database connection password')
    parser.add_argument('--mwversion', help='MediaWiki version to install',
                        default=MWVERSION)
    parser.add_argument('--wikiadmin', help='Username of wiki administrator',
                        default='mnadmin')
    parser.add_argument('--wikiadminpw', help='Passoword of wiki administrator')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose status messages')
    parser.add_argument('-p', '--public', help='Set up a public (restricted) wiki',
                        action='store_true')
    parser.add_argument('--staging', help='Set up a staging public (restricted) wiki',
                        action='store_true')
    parser.add_argument('--extdev', help='Set up an external dev (restricted) wiki',
                        action='store_true')
    parser.add_argument('--sdir', dest='settingsdir', default=def_settings_dir,
                        help='Directory from which to copy preset settings.')
    parser.add_argument('-u', '--url', help='Wiki site url, without script path',
                        required=True)
    parser.add_argument('-r', '--resetdb', help='SQL dump to import into the database.  This '
                                                'is primarily used to reset a wiki to its clean post-installation ' 
                                                'state prior to loading page content. No other installation occurs.',
                        dest='sqldumpfile')
    parser.add_argument('--debug', help='Add debug settings to wiki configuration', action='store_true')
    parser.add_argument('--base', help='Base only', action='store_true')
    parser.add_argument('--socket', help='MySQL socket file', default='/tmp/mysql.sock')
    parser.add_argument('--dbhost', help='MySQL database host', default='127.0.0.1')
    parser.add_argument('--dbport', help='MySQL database port', default=3306)
    cmdline = parser.parse_args()

    # obscure passwords if entered in through cmdline
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(--dbauser|--dbapw|--wikiuser|--wikipw|--wikiadminpw)(=|\s+)(\S+)', ur'\1\2XXXX', pstr)
    setproctitle.setproctitle(pstr)

    # retrieve passwords and usernames via console if not passed
    if not cmdline.dbauser:
        cmdline.dbauser = raw_input('Enter database admin username: ')
    if not cmdline.dbapw:
        cmdline.dbapw = getpass.getpass('Enter database admin password: ')
    if not cmdline.wikiuser:
        cmdline.wikiuser = raw_input('Enter wiki to database connection username: ')
    if not cmdline.wikipw:
        cmdline.wikipw = getpass.getpass('Enter wiki to database connection password: ')
    if not cmdline.wikiadminpw:
        cmdline.wikiadminpw = getpass.getpass(u'Password for wiki admin account %s: ' % cmdline.wikiadmin)

    # Check that we're either using sockets or IPs
    if cmdline.socket and (cmdline.dbhost or cmdline.dbport):
        print('Please either specify socket or host/port')
        raise ValueError(cmdline.socket)

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


def copyWithReplacement(infpath, outfpath, wordDic):
    with codecs.open(infpath, encoding='utf-8') as inf:
        instring = inf.read()
        outstring = multiwordReplace(instring, wordDic)
        with codecs.open(outfpath, 'w', encoding='utf-8') as outf:
            print(outstring, file=outf)


def main():
    global GIT_EXTENSIONS, METANET_EXTENSIONS, DEV_GIT_EXTENSIONS, DEV_METANET_EXTENSIONS
    global MWTARBASE_TPL, COMPOSER_EXTENSIONS, EXTRA_COMPOSER_COMMANDS, GERRITURLBASE
    global GITCMD, DEFAULT_EXTENSIONS, SVN_EXTENSIONS, SVNURLBASE, MNGITURLBASE
    global EXTRA_GIT_COMMANDS, MWTARURL_TPL, MWVERSION

    params = get_parameters()

    # add Push extension to English wiki
    if (not params.public) and (not params.staging):
        GIT_EXTENSIONS += DEV_GIT_EXTENSIONS
        METANET_EXTENSIONS += DEV_METANET_EXTENSIONS

    urlmatch = re.search('^(http|https)://([^:]+)(|:\d+)$', params.url)
    if not urlmatch:
        logging.error('URL %s does not have valid hostname', params.url)
        sys.exit(1)
    protocol = urlmatch.group(1)
    baseservername = urlmatch.group(2)
    servername = urlmatch.group(2) + urlmatch.group(3)

    # set up logging for error messages
    msgformat = u'%(asctime)-15s - %(message)s'
    dateformat = u'%Y-%m-%dT%H:%M:%SZ'
    if params.verbose:
        deflevel = logging.INFO
    else:
        deflevel = logging.WARN

    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)

    connection_params = {
        'unix_socket': params.socket,
        'user': params.dbauser,
        'passwd': params.dbapw
    } if params.socket else {
        'host': params.dbhost,
        'port': int(params.dbport),
        'user': params.dbauser,
        'passwd': params.dbapw
    }

    con = MySQLdb.connect(**connection_params)

    cursor = con.cursor()
    tstitle = params.lang.upper() + u' MetaNet Wiki '
    if params.public or params.staging:
        scriptpre = '/pub/'
        dbname = params.lang + 'mnwiki_pub'
        tstitle = tstitle + 'Pub'
        settingsfname = 'PubMetaNetSettings.php'
    else:
        scriptpre = '/dev/'
        dbname = params.lang + 'mnwiki_dev'
        tstitle = tstitle + 'Dev'
        if params.extdev:
            settingsfname = 'ExtDevMetaNetSettings.php'
        else:
            settingsfname = 'DevMetaNetSettings.php'
    scriptpath = scriptpre + params.lang

    #
    # Via the --resetdb option, an sql dump can be passed in to load into the
    # database.
    #
    if params.sqldumpfile:
        try:
            with codecs.open(os.path.abspath(params.sqldumpfile), encoding='utf-8') as dumpfile:
                cursor.execute('drop database if exists ' + dbname)
                importcmd = ['mysql', '-u', params.dbauser, '--password=' + params.dbapw]
                call(importcmd, stdin=dumpfile)
            return
        except:
            logging.error(u'SQL dump import of %s has failed.', params.sqldumpfile)
            logging.error(traceback.format_exc())
            raise

    # compute version numbers and file/dir paths
    mwmajor, mwminor = params.mwversion.rsplit('.', 1)
    if '.' not in mwmajor:
        mwmajor = params.mwversion
        mwminor = 0
        params.mwversion = mwmajor + '.' + mwminor
    mwbase = MWTARBASE_TPL % (params.mwversion)
    mwtarfurl = MWTARURL_TPL % (mwmajor, mwbase)
    mwdirname = mwbase + '-' + params.lang

    # retrieve tar file and decompress
    mwtarfile = mwbase + '.tar.gz'
    if not os.path.exists(mwtarfile):
        logging.info(u'Retrieving mediawiki tarball from %s', mwtarfurl)
        call(['wget', mwtarfurl])

    if not os.path.exists(mwdirname):
        call(['tar', 'xzvf', mwtarfile])
        call(['mv', mwbase, mwdirname])

    cwd = os.getcwd()
    os.chdir(mwdirname)

    # create cache directories (localisation and page)
    os.mkdir("cache/local")
    os.mkdir("cache/html")
    call(['chmod', '-R', 'g+w', '.'])
    if params.public or params.extdev:
        call(['sudo', 'chown', '-R', 'apache', 'cache'])

    # create databases
    privs = 'index, create, select, insert, update, delete, drop, alter, ' \
            'create temporary tables, lock tables'

    # clear mysql database (if exists)    
    cursor.execute('drop database if exists ' + dbname)

    # clear triplestore if exists, or create if doesn't
    if (not params.public) and (not params.staging) and (not params.extdev):
        from subprocess import Popen, PIPE, STDOUT
        sesamecmd = ['/xa/metanet/tools/openrdf-sesame-2.7.8/bin/console.sh',
                     '-q', '-s', 'http://localhost:8080/openrdf-sesame']
        try:
            p = Popen(sesamecmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            pout, perr = p.communicate(input='open %s.\n' % (dbname))
            unkerr = "Unknown repository: '%s'" % (dbname)
            if unkerr in perr:
                # then the repository needs to be created
                p = Popen(sesamecmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                pout, perr = p.communicate(input='create native.\n%s\n%s\n\n' % (dbname, tstitle))
            elif perr:
                logging.error('Unknown error from triplestore: %s', perr)
                raise RuntimeError(perr)
            else:
                # clear existing repository
                p = Popen(sesamecmd + [dbname], stdout=PIPE, stdin=PIPE, stderr=PIPE)
                stdout_data, stderr_data = p.communicate(input='clear.\n')
        except:
            traceback.print_exc()
            raise

    # create mysql database and set permissions
    cursor.execute("CREATE DATABASE %s" % dbname)
    cursor.execute("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (params.wikiuser, params.wikipw))
    cursor.execute("CREATE USER '%s'@'%%'        IDENTIFIED BY '%s';" % (params.wikiuser, params.wikipw))
    cursor.execute("grant %s on %s.* to '%s'@'localhost' identified by '%s';" % (
        privs, dbname, params.wikiuser, params.wikipw))
    cursor.execute("grant %s on %s.* to '%s'@'%%'        identified by '%s';" % (
        privs, dbname, params.wikiuser, params.wikipw))
    cursor.execute(u"grant select on %s.* to 'readonly_user'@'localhost' identified by 'readme';" % dbname)

    def dbserver():
        if params.socket:
            return 'localhost:%s' % params.socket
        else:
            return '%s:%s' % (params.dbhost, params.dbport)

    # Install always with English as default: '--lang='+params.lang,
    wikiinstallcmd = ['php', 'maintenance/install.php',
                      '--dbname=%s'     % dbname,
                      '--dbserver=%s'   % dbserver(),
                      '--dbuser=%s'     % params.wikiuser,
                      '--dbpass=%s'     % params.wikipw,
                      '--pass=%s'       % params.wikiadminpw,
                      '--scriptpath=%s' % scriptpath,
                      dbname,
                      params.wikiadmin]

    call(wikiinstallcmd)

    # have to manually fix the wgLanguageCode line because of a bug in the CLI installer
    shutil.copy('LocalSettings.php', 'OrigLocalSettings.php')
    with codecs.open('OrigLocalSettings.php', encoding='utf-8') as olsfile:
        with codecs.open('LocalSettings.php', mode='w', encoding='utf-8') as lsfile:
            for line in olsfile:
                line = line.strip()
                # skip setting language (always English)
                # if (line.startswith('$wgLanguageCode =')):
                #    print(u'$wgLanguageCode = "%s";' % (params.lang), file=lsfile)
                # el
                if (line.startswith('$wgSitename =')):
                    print(u'$wgSitename = "%s MetaNet Wiki";' % (params.lang.upper()), file=lsfile)
                else:
                    print(line, file=lsfile);

    #
    # files_to_copy is a dict where the key is the file to copy from
    # the settings directory, and the value is the destination filename
    # which is None, if it's is the same as the source filename.
    #
    files_to_copy = {
        'icsi_logo_135b.jpg':      None,
        'EnableDebugSettings.php': None,
        'DocumentOntology.owl':    None
    }
    if params.public or params.staging:
        files_to_copy['PubMetaphorOntology.owl'] = 'MetaphorOntology.owl'
        files_to_copy['skins'] = None
    else:
        files_to_copy['DevMetaphorOntology.owl'] = 'MetaphorOntology.owl'

    for fname, dfname in files_to_copy.iteritems():
        fpath = u'%s/%s' % (params.settingsdir, fname)
        if not dfname:
            dfname = fname
        if os.path.isdir(fpath):
            copy_tree(fpath, u'./%s' % (dfname))
        else:
            shutil.copy(u'%s/%s' % (params.settingsdir, fname), './%s' % (dfname))

    if params.base:
        logging.info('Exiting after base MediaWiki installation')
        sys.exit()

    # use composer to install the extension, and then run the extra
    # commands as needed.  Note that composer needs to run in the
    # wiki's root, not in the extensions directory.
    call(['wget', 'https://getcomposer.org/composer.phar'])
    for ext, version in COMPOSER_EXTENSIONS.iteritems():
        call(['php', 'composer.phar', 'require', ext, version])
        if ext in EXTRA_COMPOSER_COMMANDS:
            for cmd in EXTRA_COMPOSER_COMMANDS[ext]:
                call(cmd)

    os.chdir('extensions')

    # use git to retrieve extensions stores in git.  Change to the release branch.
    relbranch = 'REL' + mwmajor.replace('.', '_')  # e,g, REL1_24
    for ext in GIT_EXTENSIONS:
        logging.info('Installing extension %s', ext)
        exturl = u'%s/%s.git' % (GERRITURLBASE, ext)
        logging.info(u'retrieving from url %s', exturl)
        call([GITCMD, 'clone', exturl])
        os.chdir(ext)
        logging.info(u'checking out branch %s', relbranch)
        call([GITCMD, 'checkout', '-b', relbranch, 'origin/' + relbranch])
        if ext in EXTRA_GIT_COMMANDS:
            for cmd in EXTRA_GIT_COMMANDS[ext]:
                call(cmd)
        os.chdir('..')

    for ext in SVN_EXTENSIONS:
        logging.info(u'Installing svn extension %s', ext)
        exturl = u'%s/%s/' % (SVNURLBASE, ext)
        logging.info(u'retrieving from url %s', exturl)
        call(['svn', 'checkout', exturl])

    for ext in METANET_EXTENSIONS:
        logging.info(u'Installing MetaNet extension %s', ext)
        exturl = u'%s/%s.git' % (MNGITURLBASE, ext)
        logging.info(u'retrieving from uri %s', exturl)
        call([GITCMD, 'clone', exturl])

    # settings files to copy over
    mn_str_replacements = {
        u'__WGSERVER_URL__':     params.url,
        u'__WG_COOKIE_DOMAIN__': baseservername
    }

    # copy over and add require line for the appropriate MetaNetSettings file
    with open('../LocalSettings.php', 'a') as localsettingsfh:
        print('\n##\n# MetaNet site-wide settings\n#\n', file=localsettingsfh)
        copyWithReplacement(u'%s/%s' % (params.settingsdir, settingsfname),
                            u'../' + settingsfname, mn_str_replacements)
        print(u'require_once "$IP/%s";\n' % (settingsfname), file=localsettingsfh)

    logging.info('Updating ExtensionSettings...')
    with open('../ExtensionSettings.php', 'a') as settingsfile:
        print('<?php\n/**\n * Extension inclusions\n */\n', file=settingsfile)
        for ext in itertools.chain(DEFAULT_EXTENSIONS, GIT_EXTENSIONS,
                                   SVN_EXTENSIONS, METANET_EXTENSIONS):
            print('\n##\n# Extension: %s\n#\n' % (ext), file=settingsfile)
            print(u'require_once "$IP/extensions/%s/%s.php";\n' % (ext, ext),
                  file=settingsfile)
            # if the extension has it's own specific settings, copy its
            # content into the extensions settings file
            extsettingsfname = u'%s/%sSettings.php' % (params.settingsdir, ext)
            if os.path.exists(extsettingsfname):
                with open(extsettingsfname) as extf:
                    for line in extf:
                        line = line.strip()
                        if line == '<?php':
                            continue
                        print(line, file=settingsfile)

    additionalsettings = []
    if params.public or params.staging:
        additionalsettings.append('PublicWikiSettings.php')
    elif params.extdev:
        additionalsettings.append('ExtDevWikiSettings.php')
    else:
        additionalsettings.append('PrivateWikiSettings.php')
    # set debug options by default
    if params.debug:
        additionalsettings.append('EnableDebugSettings.php')

    with open('../LocalSettings.php', 'a') as localsettingsfh:
        print('\n##\n# Include Extensions\n#\n', file=localsettingsfh)
        print('require_once "$IP/ExtensionSettings.php";\n', file=localsettingsfh)
        print('\n##\n# Include Additional Settings\n#\n', file=localsettingsfh)
        for settingfname in additionalsettings:
            shutil.copy(u'%s/%s' % (params.settingsdir, settingfname), '..')
            print(u'require_once "$IP/%s";\n' % (settingfname), file=localsettingsfh)

    # run the update script in case some extensions need it (besides SMW)
    os.chdir('..')
    call(['chmod', '-R', 'g+w', '.'])
    updatecmd = ['php', 'maintenance/update.php']
    call(updatecmd)

    # set up interwiki links
    if (not params.public) and (not params.staging):
        for lang in MAIN_PAGE.keys():
            inscmdbase = u"""
              INSERT INTO %s.interwiki 
                          (iw_prefix, iw_url, iw_local, iw_trans, iw_api, iw_wikiid)
              VALUES      ("%s", "%s%s/index.php/$1", 0, 0, "", "");"""
            cursor.execute(inscmdbase % (dbname, lang, scriptpre, lang))
        # commit db changes
        con.commit()

    # try loading the main page
    if params.url:
        siteurl = u'%s%s/index.php/' % (params.url, scriptpath)
        logging.info(u'Opening main page at %s%s', siteurl, 'Main_Page')
        pagename = u'Main_Page'
        response = urllib2.urlopen(siteurl + urllib2.quote(pagename))
        html = response.read()

    # create mysqldump of pristine database (prior to page imports)
    os.chdir(cwd)
    dumpcmd = ['mysqldump', '-u', params.dbauser, '--password=%s' % params.dbapw,
               '--add-drop-database', '--databases', dbname,
               '-r', dbname + '-dump-pristine.sql']

    if not params.socket:
        dumpcmd += ['--host=%s' % params.dbhost, '--port=%s' % params.dbport]
    call(dumpcmd)


if __name__ == '__main__':
    status = main()
    sys.exit(status)
