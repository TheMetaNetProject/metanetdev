#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: goldxlsx2json
   :platform: Unix
   :synopsis: Convert gold annotation for june eval to json from excel

Convert gold standard sentences and annotation, collected in Excel format
to JSON.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""

import sys, os, codecs, subprocess, re
import iarpaxml as ix
from mnformats import mnjson
import logging
import argparse
from openpyxl.reader.excel import load_workbook
from openpyxl import Workbook
from openpyxl.style import Color, Fill
from mnpipeline.persiantagger import PersianPOSTagger

reload(sys)
sys.setdefaultencoding('utf-8')

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

logger = logging.getLogger(__name__)

def computePOS(lang, sentences):
    """ Compute POS tags and add them under a 'word' node in each sentence.
    The 'word' node is a list of dicts, where each describes a word in the
    sentence.  Uses TreeTagger for EN, ES, and RU, and a custom HMM tagger
    for FA.
    
    :param sentences: list of sentences:
    :type sentences: str
    """
    if lang == 'fa':
        pt = PersianPOSTagger()
        for sent in sentences:
            sent['ctext'] = pt.cleanText(sent['text'])
            tags = pt.run_hmm_tagger(sent['ctext'])
            #print 'sentence %d: %s\n%s' % (sidx, sent['text'],pprint.pformat(tags))
            sent['word'] = pt.getWordList(sent['text'], sent['ctext'], tags,
                                          'pos', 'lem')
    else:
        tt = mnjson.MNTreeTagger(lang)
        tt.cleanText(sentences)
        tt.run(sentences)

def main():
    """
    Runs LM to concept mapping.
    """
    # ------------------------------------------------------------------- #
    # INITIALIZATION
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Convert gold standard annotation to JSON format.")
    parser.add_argument('goldfile',
                        help="Excel file containing gold standard annotation")
    parser.add_argument('-l','--lang',required=True,
                        help="Language being processed")
    parser.add_argument('-v','--verbose',action='store_true',
                        help='print verbose messages')
    cmdline = parser.parse_args()
    
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if cmdline.verbose:
        deflevel = logging.INFO
    else:
        deflevel = logging.WARN
    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)
    
    # load the input excel file
    wb = load_workbook(cmdline.goldfile)
    
    sentences = []
    idx = 0;
    sentbycon = {}
    for tconcept in wb.get_sheet_names():
        logging.info('processing tab %s',tconcept)
        ws = wb.get_sheet_by_name(tconcept)
        sentbycon[tconcept] = {}
        for row in ws.rows[1:]:
            (id,text,tlemma,status,sform,sschema,sconcept) = (cell.value for cell in row[0:7])
            if (not text) or (not status) or status.lower()=='p':
                continue
            sent = mnjson.getJSONSentence(id,idx,text)
            if status.lower()=='n':
                sentences.append(sent)
                idx += 1
                continue
            if not sform:
                # then need to skip, because it's marked as Y but no answer was given
                continue
            if sconcept:
                sconcept = sconcept.replace(u' ',u'_').upper()
            #create lm
            sstart = text.lower().find(sform.lower())
            send = sstart + len(sform)
            source = {'form':sform,
                      'concept':sconcept,
                      'start':sstart,
                      'end':send}
            if sschema:
                source['schemanames'] = [sname.strip() for sname in sschema.split(u',')]
            target = {'lemma':tlemma,
                      'concept':tconcept}
            lm = {u'name':u'%s %s'%(target['lemma'],source['form']),
                  u'target':target,
                  u'source':source,
                  u'extractor':'Gold'}
            sent['lms'] = [lm]
            sentences.append(sent)
            idx += 1
            if sconcept:
                if sconcept in sentbycon[tconcept]:
                    sentbycon[tconcept][sconcept].append(sent)
                else:
                    sentbycon[tconcept][sconcept] = [sent]
    logging.info("Running POS tagger...")
    computePOS(cmdline.lang, sentences)
    # attempt to fill in missing form / lemma fields
    logging.info("Filling in missing fields in LMs...")
    for sent in sentences:
        if 'lms' in sent:
            if 'word' not in sent:
                continue
            for lm in sent['lms']:
                # do target
                target = lm['target']
                mwetarg = None
                if u' ' in target['lemma']:
                    # its a multiword
                    mwetarg = target['lemma'].split(u' ')
                for widx in range(len(sent['word'])):
                    w = sent['word'][widx]
                    if 'form' in target:
                        break
                    if mwetarg:
                        if mwetarg[0].lower()==w['lem'].lower():
                            tfparts = []
                            for midx in range(len(mwetarg)):
                                if mwetarg[midx].lower()==sent['word'][widx+midx]['lem'].lower():
                                    tfparts.append(sent['word'][widx+midx]['form'])
                                else:
                                    tfparts = []
                                    break
                            if tfparts:
                                target['form'] = u' '.join(tfparts)
                                target['start'] = w['start']
                                target['end'] = w['start'] + len(target['form'])
                                break
                                
                    else:
                        if target['lemma'].lower()==w['lem'].lower():
                            target['form'] = w['form']
                            target['start'] = w['start']
                            target['end'] = w['end']
                            break
                if 'form' not in target:
                    # backup, search for matching wforms
                    for widx in range(len(sent['word'])):
                        w = sent['word'][widx]
                        if 'form' in target:
                            break
                        if mwetarg:
                            if mwetarg[0].lower()==w['form'].lower():
                                tfparts = []
                                for midx in range(len(mwetarg)):
                                    if mwetarg[midx].lower()==sent['word'][widx+midx]['form'].lower():
                                        tfparts.append(sent['word'][widx+midx]['form'])
                                    else:
                                        tfparts = []
                                        break
                                if tfparts:
                                    target['form'] = u' '.join(tfparts)
                                    target['start'] = w['start']
                                    target['end'] = w['start'] + len(target['form'])
                                    break
                                    
                        else:
                            if target['lemma'].lower()==w['form'].lower():
                                target['form'] = w['form']
                                target['start'] = w['start']
                                target['end'] = w['end']
                                break
                source = lm['source']
                mwesource = None
                if u' ' in source['form']:
                    mwesource = source['form'].split(u' ')
                for widx in range(len(sent['word'])):
                    w = sent['word'][widx]
                    if 'lemma' in source:
                        break
                    if mwesource:
                        if mwesource[0].lower()==w['form'].lower():
                            slparts = []
                            for midx in range(len(mwesource)):
                                if mwesource[midx].lower()==sent['word'][widx+midx]['form'].lower():
                                    slparts.append(sent['word'][widx+midx]['lem'])
                                else:
                                    slparts = []
                                    break
                            if slparts:
                                source['lemma'] = u' '.join(slparts)
                                break                                
                    else:
                        if source['form'].lower()==w['form'].lower():
                            source['lemma'] = w['lem']
                            break
        if 'word' in sent:
            del sent['word']
        if 'ctext' in sent:
            del sent['ctext']
    fbase, _ = os.path.splitext(cmdline.goldfile)
    # create m4d gold file
    docheader = mnjson.getJSONDocumentHeader(fbase,
                                             "Gold Standard %s"%(cmdline.lang),
                                             "Gold Standard Document %s (%s)"%(fbase,cmdline.lang),
                                             "%s_MN_Analysis_Team"%(fbase),
                                             "mixed", len(sentences), cmdline.lang)
    jdata = mnjson.getJSONRoot(cmdline.lang, docs=[docheader], sents=sentences)
    mnjson.writefile(fbase+'_m4d_gold.json', jdata)
    # create m4m gold file
    
    docheaders = []
    msentences= []
    idx = 0
    for tconcept in sentbycon.iterkeys():
        for sconcept in sentbycon[tconcept].iterkeys():
            docnum = 1
            sentcount = 0
            docname = u'%s_%s_%d' % (tconcept,sconcept,docnum)
            for sent in sentbycon[tconcept][sconcept]:
                sentcount += 1
                sent['id'] = 'gold:%s:%d' % (docname,sentcount)
                sent['idx'] = idx
                msentences.append(sent)
                if sentcount == 5:
                    docheader = mnjson.getJSONDocumentHeader(docname,
                                                             "m4mapping gold %s"%(cmdline.lang),
                                                             "gold standard m4mapping set",
                                                             docname,
                                                             "mixed", sentcount, cmdline.lang)
                    docheaders.append(docheader)
                    sentcount = 0
                    docnum += 1
                    docname = u'%s_%s_%d' % (tconcept,sconcept,docnum)
            if sentcount > 0:
                docheader = mnjson.getJSONDocumentHeader(docname,
                                                         "m4mapping gold %s"%(cmdline.lang),
                                                         "gold standard m4mapping set",
                                                         docname,
                                                         "mixed", sentcount, cmdline.lang)
                docheaders.append(docheader)
    jdata = mnjson.getJSONRoot(cmdline.lang, docs=docheaders, sents=msentences)
    mnjson.writefile(fbase+'_m4m_gold.json', jdata)
    
    #
    # to create the input versions-- need to reload from file
    #
    
    jdata = mnjson.loadfile(fbase+'_m4d_gold.json')    
    for sent in jdata['sentences']:
        if 'lms' in sent:
            del sent['lms']
    mnjson.writefile(fbase+'_m4d_input.json',jdata)

    jdata = mnjson.loadfile(fbase+'_m4m_gold.json')
    for sent in jdata['sentences']:
        if 'lms' in sent:
            for lm in sent['lms']:
                for field in ('concept','schemaname','schemanames','schemauri','schemauris'):
                    for tgsc in ('target','source'):
                        if field in lm[tgsc]:
                            del lm[tgsc][field]
    mnjson.writefile(fbase+'_m4m_input.json',jdata)
    
if __name__ == "__main__":
    status = main()
    sys.exit(status)


