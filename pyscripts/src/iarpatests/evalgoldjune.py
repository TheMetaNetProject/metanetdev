#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: comparegold
    :platform: Unix
    :synopsis: Gold standard testing comparison script
    
Tool for comparing JSON with gold used in 2013 June Evals.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>
"""

import os, sys, re, codecs, argparse
from mnformats import mnjson

reload(sys)
sys.setdefaultencoding('utf-8')

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

CLEANSRE = re.compile(ur'https://metaphor\.icsi\.berkeley\.edu/(?:en|es|fa|ru)/MetaphorRepository\.owl#VettedSchema_', flags=re.U)
CLEANMRE = re.compile(ur'https://metaphor\.icsi\.berkeley\.edu/(?:en|es|fa|ru)/MetaphorRepository\.owl#VettedMetaphor_', flags=re.U)
LOPSRE = re.compile(ur'\'s$',flags=re.U)

def checkform(lmschema, text):
    if 'form' not in lmschema:
        if ('start' in lmschema) and (lmschema['start'] >= 0):
            lmschema['form'] = text[lmschema['start']:lmschema['end']]
    
def get_lm_sets(sentences, tcmpfield='lemma', scmpfield='form', scoret=-9999.0):
    global LOPSRE
    sentsbyid = {}
    sentswlms = set()
    sentsnolms = set()
    for sent in sentences:
        if ('lms' in sent) and sent['lms']:
            for lm in sent['lms']:
                if 'score' in lm:
                    if float(lm['score']) < scoret:
                        continue
                checkform(lm['target'],sent['text'])
                checkform(lm['source'],sent['text'])
                lmstring = u'%s:%s____%s' % (sent['id'],
                                         LOPSRE.sub(u'',lm['target'][tcmpfield]).lower(),
                                         lm['source'][scmpfield].lower())
                sentswlms.add(lmstring)
        else:
            # currently, this part has no effect
            lmstring = u'%s:isnull____isnull' % (sent['id'])
            sentsnolms.add(lmstring)
        sentsbyid[sent['id']] = sent
    return (sentsbyid, sentswlms, sentsnolms)

def get_concept_sets(sentences, tcmpfield='lemma', scmpfield='form'):
    global LOPSRE
    sentsbyid = {}
    sentswtcons = set()
    sentswscons = set()
    sentswboth = set()
    for sent in sentences:
        if ('lms' in sent) and sent['lms']:
            for lm in sent['lms']:
                checkform(lm['target'],sent['text'])
                checkform(lm['source'],sent['text'])
                if ('concept' in lm['target']) and lm['target']['concept']:
                    tcon = lm['target']['concept']
                else:
                    tcon = None
                if ('concept' in lm['source']) and lm['source']['concept']:
                    scon = lm['source']['concept']
                else:
                    scon = None
                if tcon:
                    tconstring = u'%s:%s____%s:%s' % (sent['id'],
                                                            LOPSRE.sub(u'',lm['target'][tcmpfield]).lower(),
                                                            lm['source'][scmpfield].lower(),
                                                            tcon.upper())
                    sentswtcons.add(tconstring)
                if scon:
                    if u',' in scon:
                        for eachscon in scon.split(u','):
                            if u':' in eachscon:
                                eachscon, _rank, _score = eachscon.split(u':',2)
                            sconstring = u'%s:%s____%s:%s' % (sent['id'],
                                                              LOPSRE.sub(u'',lm['target'][tcmpfield]).lower(),
                                                              lm['source'][scmpfield].lower(),
                                                              eachscon.strip().upper())
                            sentswscons.add(sconstring)
                    else:
                        if u':' in scon:
                            scon, _rank, _score = scon.split(u':',2)
                        sconstring = u'%s:%s____%s:%s' % (sent['id'],
                                                          LOPSRE.sub(u'',lm['target'][tcmpfield]).lower(),
                                                          lm['source'][scmpfield].lower(),
                                                          scon.upper())
                        sentswscons.add(sconstring)
                if tcon and scon:
                    bothstring = u'%s:%s____%s:%s____%s' % (sent['id'],
                                                            LOPSRE.sub(u'',lm['target'][tcmpfield]).lower(),
                                                            lm['source'][scmpfield].lower(),
                                                            tcon.upper(),
                                                            scon.upper())
                    sentswboth.add(bothstring)
        sentsbyid[sent['id']] = sent
    return (sentsbyid, sentswboth, sentswtcons, sentswscons)

def cleanmet(mname):
    global CLEANMRE
    return CLEANMRE.sub('',mname)

def print_lm(sent, target=None, source=None, tcmpfield='lemma', scmpfield='form', printaff=False, printcon=False, printdim=False, isGold=False):
    global LOPSRE
    print "============================================================"
    if isGold:
        print u'GOLD SENTENCE %s:\ntext: %s' % (sent['id'],sent['text'])
    else:
        print u'RESULT SENTENCE %s:\ntext: %s' % (sent['id'],sent['text'])
    if ('lms' in sent) and sent['lms']:
        for lm in sent['lms']:
            tg = lm['target']
            sc = lm['source']
            if target and source:
                if (LOPSRE.sub(u'',tg[tcmpfield]).lower() != target) or (sc[scmpfield].lower() != source):
                    continue
            if 'schemaname' in tg:
                print u'target=%s\ntarget schema=%s' % (tg[tcmpfield],tg['schemaname'])
            elif ('schemanames' in tg) and tg['schemanames']:
                print u'target=%s\ntarget schemas=%s' % (tg[tcmpfield],u','.join(tg['schemanames']))
            else:
                if isGold:
                    print u'target=%s' % (tg[tcmpfield])
                else:
                    print u'target=%s (No matching schemas found)' % (tg[tcmpfield])
            if 'schemanames' in sc:
                print u'source=%s\nsource schema=%s' % (sc[scmpfield],u','.join(sc['schemanames']))
            elif ('schemanames' in sc) and sc['schemanames']:
                print u'source=%s\nsource schemas=%s' % (sc[scmpfield],u','.join(sc['schemanames']))
            else:
                if isGold:
                    print u'source=%s' % (sc[scmpfield])
                else:
                    print u'source=%s (No matching schemas found)' % (sc[scmpfield])
            if 'smapmethod' in sc:
                print u'source schema via %s' % (sc['smapmethod'])
            if ('cms' in lm) and lm['cms']:
                print "cms= %s" % (cleanmet(u','.join(lm['cms'])))
            if 'score' in lm:
                print u'score= %f' % (lm['score'])
            if ('cxn' in lm) and lm['cxn']:
                print u'cxn= %s' % (lm['cxn'])
            if (not printaff) and (not printdim) and (not printcon):
                if 'extractor' in lm:
                    print u'extractor: %s' % (lm['extractor'])
            elif printcon:
                if ('concept' in tg) and tg['concept']:
                    tcon = tg['concept']
                else:
                    tcon = 'NULL'
                if ('concept' in sc) and sc['concept']:
                    scon = sc['concept']
                else:
                    scon = 'NULL'
                print u'target concept: %s, source concept: %s' % (tcon, scon)
                if 'extractor' in lm:
                    print u'mapper: %s' % (lm['extractor'])
    else:
        print "0 LMs"
    if (not printaff) and (not printcon) and (not printdim) and (not isGold):
        if 'mtext' in sent:
            print u'mtext: %s' % (sent['mtext'])
        if 'word' in sent:
            print "deps:"
            for w in sent['word']:
                if 'dep' in w:
                    if int(w['dep']['head'])==0:
                        hword = 'ROOT'
                    else:
                        try:
                            hword = sent['word'][int(w['dep']['head'])-1]['form']
                        except:
                            hword = 'ERR'
                    if 'otype' in w['dep']:
                        print u'\t"%s"-%d is %s(%s) of "%s"-%d' % (w['form'],
                                                                   w['idx'],
                                                                   w['dep']['type'],
                                                                   w['dep']['otype'],
                                                                   hword,
                                                                   int(w['dep']['head'])-1)
                    else:
                        print u'\t"%s"-%d is %s of "%s"-%d' % (w['form'],
                                                               w['idx'],
                                                               w['dep']['type'],
                                                               hword,
                                                               int(w['dep']['head'])-1)

def print_lm_set(typestr, lmset, goldbyid, resultsbyid):
    lmlist = []
    for lmstring in lmset:
        (sid, lm_name) = lmstring.rsplit(':',1)
        idnum = int(sid.rsplit(':',1)[1])
        (target,source) = lm_name.split('____',1)
        lmlist.append((idnum, sid, target, source))
    num = 0
    total = len(lmset)
    for (idnum, sid, target, source) in sorted(lmlist, key=lambda x:x[0]):
        num += 1
        if target=='isnull':
            target=None
        if source=='isnull':
            source=None
        print '========================================================================'
        print '========================================================================'
        print u' %s # %d of %d' % (typestr, num, total)
        print_lm(resultsbyid[sid], target, source)
        print_lm(goldbyid[sid],isGold=True)

def print_concept_set(typestr, conset, goldbyid, resultsbyid, contype=None):
    conlist = []
    for lmstring in conset:
        (sid, lm_name, concepts) = lmstring.rsplit(':',2)
        idnum = int(sid.rsplit(':',1)[1])
        (target,source) = lm_name.split('____',1)
        if contype=='target':
            tcon = concepts
            scon = None
            dim = None
        elif contype=='source':
            tcon = None
            scon = concepts
            dim = None
        else:
            (tcon, scon) = concepts.split('____',1)
            dim = None
        conlist.append((idnum, sid, target, source, tcon, scon, dim))
    num = 0
    total = len(conset)
    for (idnum, sid, target, source, tcon, scon, dim) in sorted(conlist, key=lambda x:x[0]):
        num += 1
        if target=='isnull':
            target=None
        if source=='isnull':
            source=None
        print '========================================================================'
        print '========================================================================'
        print u' %s # %d of %d' % (typestr, num, total)
        print_lm(resultsbyid[sid], target, source, printcon=True)
        print_lm(goldbyid[sid],target, source, isGold=True, printcon=True)

def m4detect_cmp(gold, result, tcmpfield='lemma', scmpfield='form', scoret=-9999.0, quiet=False):
    (goldbyid, goldlms, goldnolms) = get_lm_sets(gold['sentences'],tcmpfield,scmpfield,scoret)
    (resultsbyid,resultslms, resultsnolms) = get_lm_sets(result['sentences'],tcmpfield,scmpfield,scoret)
    
    true_pos = goldlms.intersection(resultslms)
    false_pos = resultslms.difference(goldlms) # items in results lms but not in goldlms
    false_neg = goldlms.difference(resultslms) # items in gold but not in results
    
    true_neg = goldnolms.intersection(resultsnolms) # but this is at the sentence level (not lm level)

    # note: false_neg_2 is fully contained in false_neg
    false_neg_2 = resultsnolms.difference(goldnolms) # we had none, but some lm are supposed to be reported
    
    n_true_pos = float(len(true_pos))
    n_false_pos = float(len(false_pos))
    n_true_neg = float(len(true_neg))
    n_gold = float(len(goldlms))
    n_results = float(len(resultslms))
    recall = n_true_pos / n_gold
    
    if not quiet:
        print 'FALSE NEGATIVES:'
        print_lm_set('FALSE NEGATIVE', false_neg, goldbyid, resultsbyid)
    
        # false positives
        print 'FALSE POSITIVES:'
        print_lm_set('FALSE POSITIVE', false_pos, goldbyid, resultsbyid)
        
        print 'TRUE POSITIVES:'
        print_lm_set('TRUE POSITIVE', true_pos, goldbyid, resultsbyid)

    # precision: of the result lms, how many were in gold
    try:
        precision = n_true_pos / n_results
    except ZeroDivisionError:
        precision = -1.0
    print u'%s Recall=%.3f (%.0f/%.0f)   Precision=%.3f (%.0f/%.0f)' % (gold['lang'].upper(),
                                                                       recall, n_true_pos,n_gold,
                                                                       precision, n_true_pos, n_results)

def m4mapping_cmp(gold, result, tcmpfield='lemma', scmpfield='form', quiet=False):
    (goldbyid, _goldboth, _goldtcons, goldscons) = get_concept_sets(gold['sentences'], tcmpfield, scmpfield)
    (resultsbyid, _resultsboth, _resultstcons, resultsscons) = get_concept_sets(result['sentences'], tcmpfield, scmpfield)

    lang = gold['lang']

    # target
    sc_true_pos = goldscons.intersection(resultsscons)
    sc_false_pos = resultsscons.difference(goldscons)
    sc_false_neg = goldscons.difference(resultsscons)
    n_sc_true_pos = float(len(sc_true_pos))
    n_sc_gold = float(len(goldscons))
    n_sc_results = float(len(resultsscons))
    sc_recall = n_sc_true_pos / n_sc_gold
    try:
        sc_precision = n_sc_true_pos / n_sc_results
    except ZeroDivisionError:
        sc_precision = -1.0
        
    if not quiet:
    
        print 'FALSE NEGATIVES: (SOURCE)'
        print_concept_set('FALSE NEGATIVE (SOURCE)', sc_false_neg, goldbyid, resultsbyid, 'source')
        
        print 'FALSE POSITIVES (SOURCE):'
        print_concept_set('FALSE POSITIVE (SOURCE)', sc_false_pos, goldbyid, resultsbyid, 'source')
    
        print 'TRUE POSITIVES: (SOURCE)'
        print_concept_set('TRUE POSITIVE (SOURCE)', sc_true_pos, goldbyid, resultsbyid, 'source')
    

    print u'%s [SOURCE] Recall=%.3f (%.0f/%.0f)   Precision=%.3f (%.0f/%.0f)' % (lang.upper(),
                                                                                sc_recall,
                                                                                n_sc_true_pos,
                                                                                n_sc_gold,
                                                                                sc_precision,
                                                                                n_sc_true_pos,
                                                                                n_sc_results)
    
        
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Diff JSON to determine performance against gold",
        epilog="Note:")
    
    # required (positional) args
    parser.add_argument("goldfile", help="gold JSON file")
    parser.add_argument("resfile", help="results JSON file")
    parser.add_argument('-t', '--testname', help='m4 test name',
                        default='m4detect')
    parser.add_argument('-s', '--score', dest='scoret',
                        type=float,
                        default=-9999.0,
                        help="Score threshhold for m4detect. If negative,"\
                        " it must be quoted with a space inserted before the - sign.")
    parser.add_argument('-q','--quiet',
                        help="Only print the stats",
                        action='store_true')
    
    cmdline = parser.parse_args()

    goldjdata = mnjson.loadfile(cmdline.goldfile)
    resjdata = mnjson.loadfile(cmdline.resfile)
    if resjdata['lang']=='fa':
        for sent in resjdata['sentences']:
            if 'lms' in sent:
                for lm in sent['lms']:
                    if ('seed' in lm) and (lm['seed']=='NA'):
                        lm['target']['form'] = lm['target']['lemma']
                        lm['source']['form'] = lm['source']['lemma']
    if cmdline.testname=='m4detect':
        m4detect_cmp(goldjdata, resjdata, scoret=cmdline.scoret,quiet=cmdline.quiet)
    elif cmdline.testname=='m4mapping':
        m4mapping_cmp(goldjdata,resjdata,quiet=cmdline.quiet)

if __name__ == "__main__":
    status = main()
    sys.exit(status)
