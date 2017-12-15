# -*- coding: utf-8 -*-

from __future__ import print_function

import codecs
import os
import sys
from finalTagger import hmm_tagger
from os.path import join, dirname, realpath
from textwrap import dedent

if len(sys.argv) < 2:
    msg  = """\
        =========================================
        Usage:
        python runTagger.py persian-raw-text-file
        "e.g.:" 
        python runTagger.py samplePersian.txt
        ========================================="""
    print(dedent(msg))
    sys.exit()

# loading the probability files for the pos tagger
# this step needs to be done only once for the whole tagging.
here = dirname(realpath(__file__))
fp1 = codecs.open(join(here, 'bigramProb.txt'),'r','utf-8').read()
fp2 = codecs.open(join(here, 'lexProb.txt'),'r','utf-8').read()        

perFile = codecs.open(sys.argv[1],'r','utf-8')

uerr = codecs.getwriter('utf-8')(sys.stderr)
uout = codecs.getwriter('utf-8')(sys.stdout)

# read sentences from the file and pos tag them
for perSent in (l.rstrip() for l in perFile):
    # for the tagger formating replace the "/"
    # (lucag) Replaced '/' with a '\t' in the tagger...
    #     perSent = perFile.readline().strip().replace("/","-")
    try:
        # POS tag the sentence, this is the main call to the pos tagger
        posList = hmm_tagger(unicode(perSent), fp1, fp2)        
        for posTup in posList:
#             posTup = posTup.encode("utf-8")
            print(posTup, file=uout)
        print(file=uout)
    except:
        print('problem tagging:', '|%s|' % perSent, file=uerr)

