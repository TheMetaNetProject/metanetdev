#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: wiktionary
    :platform: Unix
    :synopsis: library for looking up wiktionary definitions from a defn TSV file dump

Creates and caches lookup tables to search for word meanings in wiktionary.
Presently only possible for English.  This is used to expand coverage by 
retrieving linked words in the definitions.

.. moduleauthor:: Jisup <jhong@icsi.berkeley.edu>
"""
import sys, os, logging, re, pprint, sqlite3, codecs, argparse
import cPickle as pickle

DEFAULTTSVFILE='TEMP-E20141004.tsv'

class Wiktionary:
    dbdir = '/u/metanet/repository/wiktionary'
    langabbr = {'English': 'en',
                'Spanish': 'es',
                'Russian': 'ru',
                'Persian': 'fa'}
    
    def __init__(self, lang='en', tsvfile=DEFAULTTSVFILE, dbdir=None, cachedir=None, force=False):
        """
        :param lang: language
        :type lang: str
        :param tsvfile: name of file containing wiktionary dump (TSV format)
        :type tsvfile: str
        :param dbdir: directory containing the file dump
        :type dbdir: str
        :param cachedir: directory to create cache files
        :type cachedir: str
        :param force: flag to force cache regeneration
        :type force: bool 
        """
        self.logger = logging.getLogger(__name__)
        if dbdir:
            self.dbdir = dbdir
        if not cachedir:
            cachedir = self.dbdir
        self.lang = lang
        self.cachef = '%s/%s.wikdata' % (cachedir, self.lang)
        tsvfpath = '%s/%s' % (self.dbdir, tsvfile)
        infmodtime = os.path.getmtime(tsvfpath)
        if (os.path.exists(self.cachef) and (not force) and 
                (os.path.getmtime(self.cachef) > infmodtime)):
            self.logger.info('loading wiktionary data')
            self.loadcache()
            return
        self.logger.info('generating wiktionary cache')
        self.importDefs(tsvfpath)
        self.cacheme()

    def cacheme(self):
        f = open(self.cachef,'wb')
        pickle.dump((self.lookup,
                     self.lposlookup),f,2)
        f.close()

    def loadcache(self):
        f = open(self.cachef,'rb')
        (self.lookup,
         self.lposlookup) = pickle.load(f)
        f.close()
       
    def importDefs(self, tsvfile):
        self.lookup = {}
        self.lposlookup = {}
        self.logger.info('importing wiktionary definitions')
        with codecs.open(tsvfile, encoding='utf-8') as ifile:
            numwords = 0
            for line in ifile:
                numwords += 1
                lang, word, pos, defn = line.strip().split(u'\t')
                startprop = defn.find('{{')
                if startprop >= 0:
                    endprop = defn.find('}}')
                    property = defn[startprop+2:endprop]
                    definition = defn[endprop+2:].strip()
                else:
                    property = ""
                    definition = defn[1:].strip()
                if (word,pos) in self.lookup:
                    self.lookup[(word,pos)].append((property,definition))
                else:
                    self.lookup[(word,pos)]= [(property,definition)]
                if word in self.lposlookup:
                    self.lposlookup[word].add((word,pos))
                else:
                    self.lposlookup[word] = set([word,pos])
                     
                if numwords % 1000 == 0:
                    self.logger.info('imported %d words... current word: %s', numwords,word)
        
    def getDef(self,word,pos=None):
        """ Given a word and an optional POS extension, return the definition.
        :param word: word to look up
        :type word: str
        :param pos: part of speech
        :type pos: str
        :return: definition of the word
        :rtype: str
        """
        try:
            if pos:
                for row in self.lookup[(word,pos)]:
                    print row[0], row[1]
            else:
                for lpos in self.lposlookup[word]:
                    for row in self.lookup[lpos]:
                        print lpos[0], lpos[1], row[0], row[1]
        except KeyError:
            self.logger.error(u'%s.%s not found',word,pos)
                
    def getDefWords(self, word, pos):
        """ Given a word with a pos, return the bracketed words from that word's
        definition.
        :param word: word to look up
        :type word: str
        :param pos: part of speech
        :type pos: str
        :return: list of linked words from definition
        :rtype: list        
        """
        q = '''SELECT properties, definition FROM dictionary WHERE word=? AND pos=?'''
        wordList = set()
        try:
            for row in self.lookup[(word,pos)]:
                props, defn = row
                wcontext = ''
                if props:
                    if 'context|' in props:
                        proplist = props.split('|')
                        # extra sanity
                        if proplist[0]=='context':
                            wcontext = proplist[1]                
                brackstart = defn.find('[[')
                while brackstart >= 0:
                    brackend = defn.find(']]', brackstart+2)
                    if brackend >= 0:
                        wordstr = defn[brackstart+2:brackend]
                        # sometimes multiple words appear with | separating them
                        if '|' in wordstr:
                            words = wordstr.split('|')
                        else:
                            words = [wordstr]
                        for w in words:
                            # sometimes #POS is appended to the lemma to override the pos
                            # of the looked-up word
                            if '#' in w:
                                wordpart, ppos = w.split('#')
                                wordList.add((wordpart,ppos,wcontext))
                            else:
                                wordList.add((w,pos,wcontext))
                    brackstart = defn.find('[[', brackend+2)
        except KeyError:
            pass
        return wordList
            
            
    
def main():
    """ For processing the TSV file into a sqlite3 database """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Wiktionary lookup library utility",
        epilog="Note: Importing a new dump will delete the old one.")
    parser.add_argument("-l", "--lang",
                        default='en',
                        help="Language of the dictionary.")
    parser.add_argument("-w","--word-lookup",dest='wlookup',
                        help="Look up word in the dictionary.")
    parser.add_argument("-v","--verbose",action="store_true",
                        help="Verbose messages.")
    parser.add_argument("-m","--mlookup",
                        help='Embedded words in definition')
    parser.add_argument("-d","--dbdir",help="Directory to search for TSV file in",
                        default=".")
    parser.add_argument("-c","--cachedir",help="Directory to create cache files in. "\
                        "Default: same as dbdir")
    parser.add_argument("-t","--tsvfilename",help="Name of TSV file in the dbdir",
                        default=DEFAULTTSVFILE)
    parser.add_argument("-f","--force",help="Force cache regeneration",
                        action="store_true")
    
    cmdline = parser.parse_args()

    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if cmdline.verbose:
        deflevel = logging.INFO
    else:
        deflevel = logging.WARN
    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)

    wik = Wiktionary(cmdline.lang,tsvfile=cmdline.tsvfilename,
                     dbdir=cmdline.dbdir,cachedir=cmdline.cachedir,
                     force=cmdline.force)

    if cmdline.wlookup:
        if u'.' in cmdline.wlookup:
            word,pos = cmdline.wlookup.split(u'.')
            wik.getDef(word, pos)
        else:
            wik.getDef(cmdline.wlookup)
            
    if cmdline.mlookup:
        word,pos = cmdline.mlookup.split(u'.')
        print pprint.pformat(wik.getDefWords(word,pos))

if __name__ == "__main__":
    status = main()
    sys.exit(status)
