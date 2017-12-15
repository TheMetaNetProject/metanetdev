#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Script that runs findmetaphors.py for all the languages on
# seed files in SEED_DIR/LANG/seeds.  This can optionally be limited to
# just one language.  The script can also be pointed to alternate seeds
# via the specification of a suffix.  The output is processed to conform
# the format expected by the wiki import.
#
# jhong@icsi
#

import codecs
import sys
import re
import subprocess
import argparse

DEFAULT_SEED_DIR = './seeds/'

def main():
    global DEFAULT_SEED_DIR
    
    # Assume it is in path
    META_FINDER = 'findmetaphors'
    PERSIANDIR = '../persian2/'
    PERSIAN_META_FINDER = PERSIANDIR + 'extrMetaphBiGrNPs.py'

    langs = ['en', 'es', 'ru', 'fa']
    langname = {'en':'english', 'es':'spanish', 'ru':'russian', 'fa':'persian'}
    seedsuffix = ''

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Find metaphors in the corpora')
    parser.add_argument('-l', '--language', required=False, choices=['en', 'es', 'ru', 'fa'],
                        dest='language',
                        help='Use to limit metaphor search to just the one language given.'+
                        'Default is to run for all languages.')
    parser.add_argument('-s', '--seed-suffix', required=False, dest='seedsuff',
                        help='Use to specify suffix to the seed file names, e.g. short.'\
                        'It should not include the "."')
    parser.add_argument('-d', '--seed-dir', dest='seeddir',
                        help='Directory in which to look for seeds.  Note that this '\
                        'directory should contain lang-based subdirectories.',
                        default=DEFAULT_SEED_DIR)
    parser.add_argument('-x','--exclude-persian',dest='excludepersian',
                        help="Do not do metaphor search for Persian",
                        action='store_true')
    cmdline = parser.parse_args()

    language = cmdline.language
    seedsuff = cmdline.seedsuff
    seeddir = cmdline.seeddir
    
    # possible to specify
    if (language):
        sys.stderr.write("Running only for language "+language+"...\n")
        langs = [language]
    elif cmdline.excludepersian:
        langs = ['en','es','ru']
        print >> sys.stderr, "Running for ",langs
    else:
        sys.stderr.write("Running for en, es, ru, and fa ...\n")
        
    if seedsuff:
        #sys.stderr.write("Running for using seeds with suffix "+seedsuff+"\n")
        seedsuffix = seedsuff.strip()

    # iterate for all the languages
    for lang in langs:
        if lang == 'fa':
            continue
        lname = langname[lang]
        sys.stderr.write("Finding metaphors for "+lname+"...\n")
        seedsfile = codecs.open(seeddir+'/'+lang+'/seeds.'+seedsuffix, encoding='utf-8')
        toFile = codecs.open('output.'+lang+'.'+seedsuffix+'.txt',encoding='utf-8', mode='w+')
        for line in seedsfile:
            # trim whitespace
            line = line.strip()
            if (not line):
                continue
            relation = ''
            if line[0]=='-':
                relation = 'verb-object'
            else:
                relation = 'verb-subject'
            words = line.split()
            verb = ''
            noun = ''
            if (relation=='verb-object'):
                verb = words[1]
                noun = words[2]
            else:
                noun = words[0]
                verb = words[1]
            toFile.write('----------------------------\n');
            toFile.write("%s %s %s:\n" % (words[0], words[1], words[2]))
            # run finder
            mets = ''
            try:
                # run Find_Metaphors_Corpora
                sys.stderr.write("Searching on %s %s %s\n" % (relation,verb,noun))
                mets = unicode(subprocess.check_output([META_FINDER,
                                                        '-l',lang,
                                                        '-r',relation,
                                                        '-v',verb,
                                                        '-n',noun]),'utf-8')
            except subprocess.CalledProcessError:
                sys.stderr.write('Error running %s -l %s -r %s -v %s -n %s\n' %
                             (META_FINDER,lname,relation,verb,noun))
            # extract out just the "Discovered metaphor:" lines
            metlines = mets.splitlines()
            for mline in metlines:
                if mline.startswith('Discovered metaphor:'):
                    mlwords = mline.strip().split()
                    metv = mlwords[2]
                    metn = mlwords[4]
                    if (len(mlwords) > 5):
                        freq = mlwords[5]
                        toFile.write("%s %s %s\n" % (metv, metn, freq))
                    else:
                        toFile.write("%s %s\n" % (metv, metn))
                    print "    "+mline
        toFile.close();
        seedsfile.close()

    if 'fa' in langs:
        lname = langname[lang]
        sys.stderr.write("Finding metaphors for "+lname+"...\n")
        toFile = codecs.open('output.'+lang+'.'+seedsuffix+'.txt',encoding='utf-8', mode='w+')
        mets = unicode(subprocess.check_output(['python', PERSIAN_META_FINDER,
                                                'persian.parsed.conll', 'wn-fa.tab',
                                                'EnglishWord4Top500Sents.txt', 'cot.txt',
                                                'lmCorp.ct', 'new.sensePairs.similarity.txt','MetaphorLexByAria.txt'],
                                               cwd=PERSIANDIR),'utf-8')
        #write the whole thing to file then display on screen
        toFile.write(mets)
        toFile.close()
        ngramline = True
        metlines = mets.splitlines()
        for line in metlines:
            line = line.strip()
            if (ngramline):
                if (line == ""):
                    ngramline = False
                    continue
                print '    Discovered metaphor: '+line
            if (line[:4] == "===="):
                ngramline = True
                continue
    sys.exit(0)

if __name__ == '__main__':
    main()
