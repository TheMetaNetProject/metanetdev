#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: m4affect
   :platform: Unix
   :synopsis: Computes affect for LMs in sentences in IARPA XML or MetaNet JSON formats.

DEPRECATED.

Computes affect for each Linguistic Metaphor in the input XML or JSON file in terms of
polarity and intensity.  For information on the algorithm, refer to :py:mod:`mnpipeline.affectlookup`.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>, Collin Baker <collinb@icsi.berkeley.edu>

"""
import sys, os, codecs, subprocess
import iarpaxml as ix
from mnpipeline.affectlookup import AffectLookup
from mnformats import mnjson

def main():
    """
    Runs affect computation.
    """
    # ------------------------------------------------------------------- #
    # INITIALIZATION

    m4test = ix.IARPATestCommand('metaa','Computes LM affect in terms of polarity and intensity.')
    cmdline = m4test.parseCmdLine()
    jdata = m4test.getJSON()
        
    # ------------------------------------------------------------------- #
    # MAIN APPLICATION LOGIC

    lang = jdata['lang']
    if lang != 'fa':
        tt = mnjson.MNTreeTagger(lang)
        tt.cleanText(jdata['sentences'])
        tt.run(jdata['sentences'])
        tt.processLMs(jdata['sentences'])
    
    esfilterwords = set(['a','desde','detrás','ante','en','segun','bajo',
            'entre','sin','con','hacia','sobre','contra','hasta','la','el',
            'los','tras','de','por','para'])
    
    aff_system = AffectLookup(jdata['lang'],cmdline.extdir)
    for sent in jdata['sentences']:
        for lm in sent['lms']:
            tg = lm['target']
            sc = lm['source']
            tlemma = tg['lemma'] if 'lemma' in tg else tg['form']
            slemma = sc['lemma'] if 'lemma' in sc else sc['form']
            affect = aff_system.getLMAffect(tlemma.lower(),slemma.lower())
            if affect==999:
                if lang=='es':
                    if ' ' in tlemma:
                        tlist = []
                        for w in tlemma.split():
                            if w in esfilterwords:
                                continue
                            tlist.append(w)
                        tlemma = u' '.join(tlist)
                    if ' ' in slemma:
                        slist = []
                        for w in slemma.split():
                            if w in esfilterwords:
                                continue
                            slist.append(w)
                        slemma = u' '.join(slist)
                    affect = aff_system.getLMAffect(tlemma.lower(),slemma.lower())
            lm['affect'] = affect

    # ------------------------------------------------------------------- #
    # OUTPUT FILE GENERATION
    m4test.writeOutput(jdata)
        
if __name__ == "__main__":
    status = main()
    sys.exit(status)
