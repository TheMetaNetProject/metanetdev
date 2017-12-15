#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: m4mapping
   :platform: Unix
   :synopsis: Maps Linguistic Metaphors (LMs) provided in IARPA XML or MetaNet JSON formats to IARPA concepts.

Maps Linguistic Metaphors (LMs) in the input files to IARPA concepts.  This mapping is accomplished via
two approaches, one which leverages the MetaNet conceptual network via :py:mod:`mnrepository.metanetrdf`
and one which uses distributional statistics (:py:mod:`mapping`).  The latter approach is presently employed only for
English.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>, Luca Gilardi <lucag@icsi.berkeley.edu>

"""

import sys, os, codecs, subprocess, re
import iarpaxml as ix
import logging

from mnrepository.cnmapping import ConceptualNetworkMapper
from mnformats import mnjson
from mapping.assign import Assigner
from depparsing.dep2json import parse
from depparsing.util import flattened#, log
from pprint import pprint, pformat
from cmsextractor.cms import ConstructionMatchingSystem as cms
from depparsing.parser.util import parserdesc

REMAP_CONCEPT = {u'MONEY':u'WEALTH',
                 u'THE_RICH':u'WEALTH',
                 u'IMPOVERISHED':u'POVERTY',
                 u'TAXES':u'TAXATION'}

def find_lm(target, source, relations):
    """Looks up the pair (t, s) without worrying about their positons (for now).
    relations is in the format returned by RaspBuilder.
    """
    #print('looking for', target, source)
    return [(dep_l, head_l, rtype)
            for (dep_l, dep_w, _, dep_n), (head_l, head_w, _, head_n), rtype in relations
            if target == dep_w and source == head_w]

def find_lm2(target, source, words):
    """ Assumes words is ordered by idx. """
    def head(word):
        i = word['dep']['head']
        return words[i - 1] if 0 < i <= len(words) else None

    return [(w['lem'], head(w)['lem'], w['dep']['type']) for w in words
            if head(w) and target.lower() == w['form'].lower() and source.lower() == head(w)['form'].lower()]

def lemma(form, words):
    for w in words:
        if w['form'].lower() == form.lower():
            return w['lem']
    return None

def lemma2(form, words):
    def d(w1, w2):
        return abs(w1['start'] - w2['start'])

    l = sorted([(d(form, w), w['lem']) for w in words if form['form'].lower() == w['form'].lower()],
               key=lambda (d, _): d)
#     pprint(l)
    return l[0][1] if len(l) > 0 else None

def find_lm3(target_f, source_f, words):
    p = map(lambda f: lemma(f, words), (target_f, source_f))
    return [p + ['-']] if all(p) else None

def find_lm4(target, source, words):
    p = map(lambda f: lemma2(f, words), (target, source))
    return [p + ['-']] if all(p) else None

def find_lm5(target_f, source_f, relations):
# (dep.wordn, dep.head.wordn, dep.rel, dep.word, dep.lemma, dep.head.word, dep.head.lemma)
    for _, _, rel, f, l, hf, hl in relations:
        if target_f == f and source_f == hf:
            return [[l[0], hl[0], rel]]
        if target_f == hf and source_f == f:
            return [[l[0], hl[0], rel]]
    return None


def deprels(words):
    def head(word):
        i = word['dep']['head']
        return words[i - 1] if 0 < i <= len(words) else None

    return [(w['form'], w['dep']['type'], head(w)['form'])
             for w in words if head(w)]


logger = logging.getLogger(__name__)


def main():
    """
    Runs LM to concept mapping.
    """
    global REMAP_CONCEPT
    # ------------------------------------------------------------------- #
    # INITIALIZATION
    m4test = ix.IARPATestCommand('metam', 'Map LMs to target and source concepts.')

    # add some custom cmdline parameters
    aparser = m4test.getArgParser()
    cmdline, config = m4test.parseCmdLineConfig('m4mapping')
    in_jdata = m4test.getJSON()

    # ------------------------------------------------------------------- #
    # MAIN APPLICATION LOGIC
    
    lang = in_jdata['lang']    
    mappingsystems = config.getList('mappingsystems',lang=lang)
    if not mappingsystems:
        mappingsystems = ['CNMS','DSMS','DLS']
    secondaryMappingThreshold = config.getFloat('secondarymappingthreshold', lang=lang,default=0.1)
    secondaryMinScore = config.getFloatFromComp('cnms','secondaryminscore', lang=lang,default=0.1)
    mappingLimit=config.getIntFromComp('cnms','sourcelimit',lang=lang,default=2)
    if secondaryMappingThreshold:
        m4test.setSecondaryMappingThreshold(secondaryMappingThreshold)
    conceptrank = config.getListFromComp('cnms', 'targetconceptranking', lang=lang)
    expansionTypes = config.getListFromComp('cnms','expansiontypes',lang=lang)
    expansionScoreScale = config.getFloatFromComp('cnms','expansionscorescale',lang=lang,
                                                  default=1.0)
    dsmsdefaultrank = config.getIntFromComp('dsms','defaultrank',lang=lang,default=2)
    dsmsdefaultscore = config.getFloatFromComp('dsms','defaultscore',lang=lang,default=0.10)
    dsmsScoreStr = ':%s:%s' % (dsmsdefaultrank,dsmsdefaultscore)
    
    # initialize CNMS system
    # this is always used at least for target concept lookups
    cnmap = ConceptualNetworkMapper(in_jdata['lang'], cmdline.cachedir,
                                    useSE=cmdline.useSE, govOnly=True,
                                    disableFN=True,
                                    targetConceptRank=conceptrank,
                                    expansionTypes=expansionTypes,
                                    expansionScoreScale=expansionScoreScale)
    
    # ------------------------------------------------------------------- #
    # Invoke here the parser and add tags to the sentences element of the JSON input
    in_sentences = in_jdata['sentences']
    
    # run POS/Lemmatizer for all languages except Persian (CNMS)
    if (lang != 'fa'):
        tt = mnjson.MNTreeTagger(lang)
        tt.cleanText(in_sentences)
        tt.run(in_sentences)
        tt.processLMs(in_sentences)

    # run dependency parser for Englishjunk
    if (lang in ('en', 'ru', 'es')) and ('DSMS' in mappingsystems):
        ss = [s['ctext'] for s in in_sentences]
        logger.info('begin parsing sentence block, lang: %s, len: %d' % (lang, len(ss)))
        out_jdata = parse(in_jdata['lang'], ss)
        logger.info('end parsing sentence block')
        mapping = Assigner(lang)
    else:
        out_jdata = in_jdata

    currentTestItem = ''
    parser_name = parserdesc(lang).name
    # XXX makes no sense!
#     for in_sent, parsed_sent, in_sent in zip(in_sentences, out_jdata['sentences'], in_jdata['sentences']):
    for in_sent, parsed_sent in zip(in_sentences, out_jdata['sentences']):
        testItemId = in_sent['id'].split(u':')[1]
        if testItemId != currentTestItem:
            currentTestItem = testItemId
            logger.warn('mapping sentences in %s', currentTestItem)

        if 'lms' not in in_sent:
            continue

        for lm in in_sent['lms']:
            source, target = lm['source'], lm['target']
            # ===============================================================
            # TARGET CONCEPT MAPPING: ALWAYS USE CNMS
            # ===============================================================
            cnmap.runTargetMapping(lm)
            lm['extractor'] = 'CNMS'
            
            # remap targetconcepts if needed.  this is a hack to deal with
            # IARPA's inconsistency about concept coverage
            if target.get('concept') in REMAP_CONCEPT:
                target['concept'] = REMAP_CONCEPT[target['concept']]
            
            # ================================================================
            # CNMS
            # ================================================================
            if 'CNMS' in mappingsystems:
                cnmap.runSourceMapping(lm, sourceMappingLimit=mappingLimit,
                                       minSecondaryScore=secondaryMinScore)
            
            # ================================================================
            # DSMS MAPPING SYSTEM (formerly KMS)
            # ================================================================

            if ((source.get('concept') in (None,'NULL','NONE','')) and ('DSMS' in mappingsystems) and 
                    (lang in ('en', 'ru', 'es'))):
                target_f = target['form'] if 'form' in target else target['lemma']
                source_f = source['form'] if 'form' in target else source['lemma']
                found_lms = False
                
                words = sorted(parsed_sent['word'], key=lambda w: w['idx'])
                twords = sorted(in_sent['word'], key=lambda w: w['idx'])
                
#                 logger.info(pformat(in_sent['word']))
                            
                # Try looking for a relation first
                relations = parsed_sent[parser_name]['relations']
                found_lms = find_lm5(target_f, source_f, relations)
                
                if not found_lms:
                    found_lms = find_lm3(target_f, source_f, twords)
                    
#                 if not found_lms:
#                     found_lms = find_lm4(target, source, words)
                    
                logger.debug('DSMS: found_lms: %s' % found_lms)
                
                if found_lms:
                    target_l, source_l, _r = found_lms[0]
                    target['rlemma'] = target_l
                    source['rlemma'] = source_l
                    if _r != '-':
                        r = _r.split('.')[0] if '.' in _r else _r
                        dimensions = mapping.assign2(source_l, r)
                    else:
                        dimensions = mapping.gassign(source_l, target_l)
                        
                    scon = dimensions[0].upper() if dimensions else None
                else:
                    scon = None
                    target_l = target['lemma'] if 'lemma' in target else target['form']
                    source_l = source['lemma'] if 'lemma' in source else source['form']
#                     dd = ', '.join(' '.join(d) for d in deprels(words))
#                     log('could not find %s - %s in %s' % (target_f, source_f, dd))
                source['concept'] = scon+dsmsScoreStr if scon else 'NONE'
                if scon:
                    if source.get('extractor'):
                        source['extractor'] += ':DSMS'
                    else:
                        source['extractor'] = 'DSMS'

    # ------------------------------------------------------------------- #
    # OUTPUT FILE GENERATION
    m4test.writeOutput(in_jdata)


if __name__ == "__main__":
    status = main()
    sys.exit(status)


