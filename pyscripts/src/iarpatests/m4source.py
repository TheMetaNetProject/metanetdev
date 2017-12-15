#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: m4source
   :platform: Unix
   :synopsis: Determines the source dimension of Linguistic Metaphors (LMs) which have already been mapped to target and source concepts.

DEPRECATED.

Identifies a source dimension for LMs and LM mappings to IARPA concepts in the input XML or JSON files.  This
system combines two approaches: one which leverages the MetaNet conceptual network via :py:mod:`mnrepository.metanetrdf`,
and one which uses distributional statistics (:py:mod:`source`).  The latter approach is used in addition to the
former for all languages except Persian.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>, Luca Gilardi <lucag@icsi.berkeley.edu>, Dario Gutierrez <edg@icsi.berkeley.edu>

"""

import sys, os, codecs, subprocess
import iarpaxml as ix

from mnrepository.cnmapping import ConceptualNetworkMapper
from mnformats import mnjson
from depparsing.dep2json import parse
from string import capwords 
from m4mapping import find_lm3

# XXXX This is the switch, for now
# USE_DARIOS = False
USE_DARIOS = True

if USE_DARIOS:
    _lang = {'en': 'english', 'ru': 'russian', 'es': 'spanish'}
    from source.subdims_matcher import subdim_match

    def capitalize(s):
        if s.lower() == 'all':
            return 'ALL'
        else:
            s = s.replace('_', ' ')
            s.capitalize()
            s = s.replace(' ', '_')
            return s

        
def main():
    """
    Runs source dimension identification.
    """
    # ------------------------------------------------------------------- #
    # INITIALIZATION
    m4test = ix.IARPATestCommand('metas', 'Map LMs with concepts to source dimensions.')
    cmdline = m4test.parseCmdLine()
    jdata = m4test.getJSON()

    # Run the parser
#     parsed_jdata = parse(jdata['lang'],  [s['text'] for s in jdata['sentences']])

    def lemma(source):
        pass
    
    # ------------------------------------------------------------------- #
    # MAIN APPLICATION LOGIC
    
    lang = jdata['lang']
    in_sentences = jdata['sentences']
    if lang != 'fa':
        tt = mnjson.MNTreeTagger(lang)
        tt.cleanText(in_sentences)
        tt.run(in_sentences)
        tt.processLMs(in_sentences)
                
    cnmap = ConceptualNetworkMapper(lang, cmdline.cachedir)
    for sent in jdata['sentences']:
        if 'lms' not in sent:
            continue
        for lm in sent['lms']:
            # Note that dimension here is in the form
            # CONCEPT.Dimension, e.g. DISEASE.Type.  An UNRESOLVED problem here
            # for the GMR system is what happens when the CONCEPT part we
            # calculated doesn't match with what IARPA provides in the XML.
            
            # INTEGRATE NEW SYSTEM HERE!

            source, target = lm['source'], lm['target']
            source_f = source['form']
            target_f = target['form']
            source_l = source['lemma'] if 'lemma' in source else source['form']   
            target_l = target['lemma'] if 'lemma' in target else target['form']
            source_pos = source['pos'] if 'pos' in source else ''
            target_pos = target['pos'] if 'pos' in target else ''
            
            sschemas, sourceconceptdim = cnmap.getSourceSchemasAndDimensionFromLemma(source_l,source_pos)
            if not sourceconceptdim:
                sschemas, sourceconceptdim = cnmap.getSourceSchemasAndDimensionFromLemma(source_f)
            
            if not USE_DARIOS or lang == 'fa':
                source['dimension'] = sourceconceptdim
                lm['extractor'] = 'WMS'
            else:
                source_c = source['concept'].lower()
                ((_, dim, sdim), confident) = subdim_match(_lang[lang], source_l, target_l, source_c) 
                sd_pair = u'%s.%s' % (dim.upper(), capwords(sdim, '_'))
                source['dimension'] = sd_pair if confident else sourceconceptdim
                lm['extractor'] = 'DMS' if confident else 'WMS'
                
            source['schemas'] = sschemas

    # ------------------------------------------------------------------- #
    # OUTPUT FILE GENERATION
    m4test.writeOutput(jdata)
        
if __name__ == "__main__":
    status = main()
    sys.exit(status)
