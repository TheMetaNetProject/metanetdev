#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: comparegold
    :platform: Unix
    :synopsis: Gold standard testing comparison script

Augmented version of the gold standard compare script written by Luke G.  This version
reads the XML output file for the extractor LMs, but also the JSON output file to
collect other information that's in the JSON but not the XML.  The extractor output
is compared to the gold standard answers that are in CSV format, and an output
CSN file is generated that allows for correction and direct recalculation of
recall/precision from Excel.

.. moduleauthor:: Jisup Hong<jhong@icsi.berkeley.edu>
"""
import os, sys, logging, pprint, codecs, argparse
import unicodecsv as csv
from xml.dom import minidom
from mnformats import mnjson

METAPHORPREF=u'https://metaphor.icsi.berkeley.edu/%s/MetaphorRepository.owl#Metaphor_'

def overlaps(span1, span2):
	"""
	Given two character span tuples (start, end) return True if the spans
	overlap and False if they don't.
	:param span1: a start,end tuple
	:type span1: tuple
	:param span2: a start,end tuple
	:type span2: tuple
	"""
	start1, end1 = span1
	start2, end2 = span2
	if (start1 >= start2) and (start1 <= end2):
		return True
	if (start2 >= start1) and (start2 <= end1):
		return True
	return False

def printCompRow(ofile, sentId, gold=None, result=None, mode=None,header=False):
	"""
	Print a row in the comparison spreadsheet:
	sid, gold_num, gold_cxn, gold_text,  gold_tform, gold_sform,
	result_tform, result_sform, matchval, extractor, seed/cxn, score, sframe, cms
	:param ofile: output file handle
	:type ofile: file
	:param sentId: sentence id of sentence to write
	:type sentId: str
	:param gold: gold data on the sentence
	:type gold: dict
	:param result: the extractor result being evaluated
	:type result: dict
	:param mode: display mode based on comparison: trueneg, falsepos, etc.
	:type mode: str
	:param header: flag to print header row and then exit
	:type header: bool
	"""
	global METAPHORPREF
	if header:
		print >> ofile, u'"SID","GS_URL","GS_TCON","GS_CXN","GS_TFORM","GS_SFORM",'\
			u'"R_TFORM","R_SFORM","MATCH","R_EXT","R_SEED/CXN","R_SCORE","R_SCHEMA","R_CM","GS_TEXT"'
		return
	template = u'"%s","%s","%s","%s","%s","%s","%s","%s",%d,"%s","%s",%.4f,"%s","%s","%s"'
	if mode=='falsepos':
		vec1 = [sentId, gold['url'],'', '', '', '']
	else:
		vec1 = [sentId, gold['url'],gold['tconc'], gold['cxn'],
				gold['tform'], gold['sform']]	
	if mode in ('falsepos','truepos'):
		rlm = result['lm']
		seedcxn = ''
		if 'SBS' in rlm['extractor']:
			seedcxn = rlm['seed']
		elif 'CMS' in rlm['extractor']:
			seedcxn = rlm['cxn']
		sframe = ''
		if 'framenames' in rlm['source']:
			sframe = u','.join(rlm['source']['framenames'])
		cmstr = ''
		if rlm.get('cms'):
			cmstr = u','.join([cm.replace(METAPHORPREF,u'') for cm in rlm['cms']])
		matchVal = 0
		if mode=='truepos':
			matchVal = 1
		vec2 = [rlm['target']['form'],rlm['source']['form'],matchVal,
				rlm['extractor'],seedcxn,rlm['score'],
				sframe, cmstr,  gold['sent_text'].replace(u'"',u'""')]
	elif (mode=='trueneg') or (mode=='falseneg'):
		vec2 = ['','',0,'','',0.0,'','', gold['sent_text'].replace(u'"',u'""')]
	print >> ofile, template % tuple(vec1+vec2)

	
def main():
	"""
	Compare m4detect output file to expected output from gsdb2mndetectinput.py
	"""
	global METAPHORPREF
	parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Compares gold standard answers CSV with XML and JSON "\
			  "extractor output",
        epilog="")

    # required (positional) args
	parser.add_argument("-g","--gold",dest="goldcsv",
                        help="CSV files containing gold standard answers",
						required=True)
	parser.add_argument("-x","--xml",dest="xmlfile",
                        help="XML file containing extractor output",
                        required=True)
	parser.add_argument("-j", "--json",dest="jsonfile",
						help="JSON file containing extractor output",
                        required=True)
	parser.add_argument("-o", "--outputfile",dest="outputfile",
						help="CSV file containing comparison output")
	parser.add_argument("-v","--verbose",action='store_true',
						help="Display verbose error messages")
	cmdline = parser.parse_args()
	
	logLevel = logging.WARN
	if cmdline.verbose:
		logLevel = logging.INFO
	logging.basicConfig(level=logLevel,
                        format='%(asctime)s %(levelname)s %(message)s')
	
	if not cmdline.outputfile:
		cmdline.outputfile = 'comp-'+cmdline.goldcsv
	
	xdoc = minidom.parse(cmdline.xmlfile)
	csvfile = open(cmdline.goldcsv, 'rb')
	cdoc = csv.reader(csvfile, encoding='utf-8')
	jdata = mnjson.loadfile(cmdline.jsonfile)
	lang = jdata['lang']
	METAPHORPREF = METAPHORPREF % (lang)
	sentences = jdata['sentences']

	sid2sent = {}
	for sent in sentences:
		sid2sent[sent['id']] = sent['idx']
	
	testsetid = '%sdetect'%lang
	
	# Pre-process GOLD standard answers, there will be a row for everything
	# including negatives
	goldlmrows = {}
	i = 0
	for row in cdoc:
		i += 1
		if i==1:
			header = list(row)
		else:
			rowdict = {}
			for k in range(len(row)):
				rowdict[header[k]] = row[k]
			sentId = '%s:%s%03d:%s' % (testsetid,lang,int(rowdict['ti_num']),rowdict['sent_num'])
			if sentId in goldlmrows:
				goldlmrows[sentId].append(rowdict)
			else:
				goldlmrows[sentId] = [rowdict]
	
	
	# Parse xml file: Our system's answers
	# An entry will exist only for answers (not for negatives)
	metads = xdoc.getElementsByTagName("metad:Result")

	testresponses = {}
	for metad in metads:
		tId = unicode(metad.getAttribute("testItemId")).encode('utf8')
		sId = unicode(metad.getAttribute("sentenceId")).encode('utf8')
		LmTT = unicode(metad.getElementsByTagName("metad:LmTargetText")[0].firstChild.data).encode('utf8')
		LmST = unicode(metad.getElementsByTagName("metad:LmSourceText")[0].firstChild.data).encode('utf8')
		sentId = '%s:%s:%s' % (testsetid,tId,sId)
		sent = sentences[sid2sent[sentId]]
		# find the LM
		theLM = None
		if LmTT and LmST:
			for lm in sent['lms']:
				if (lm['target']['lemma']==LmTT) and (lm['source']['lemma']==LmST):
					theLM = lm
					break
		else:
			logging.error('XML parsing error: a <Result> with no lemmas')
			# negative example
			
		if sentId in testresponses:
			testresponses[sentId].append({'target':LmTT,'source':LmST,'lm':theLM})
		else:
			testresponses[sentId] = [{'target':LmTT,'source':LmST,'lm':theLM}]
	
	#logging.warning('testresponses:\n%s',pprint.pformat(testresponses))
	ofile = codecs.open(cmdline.outputfile, "w", encoding='utf-8')
	
	truepos = 0
	goldcount = 0
	rcount = 0
	
	#logging.info(u'testresponses:\n%s',pprint.pformat(testresponses))
	#sys.exit(1)
	
	printCompRow(ofile, None, header=True)
	
	# iterating through gold rows
	for sentId in sorted(goldlmrows.keys()):
		goldrows = goldlmrows[sentId]
		responserows = testresponses.get(sentId)			
		countedresponses = set()
		
		if (len(goldrows)==1) and (not goldrows[0]['tform']) and (not goldrows[0]['sform']):
			# it's a negative example.
			if not responserows:
				# we correctly got nothing
				logging.debug(u'true negative: gold=%s\n\n\nresponse=%s',pprint.pformat(goldrows),pprint.pformat(responserows))
				printCompRow(ofile,sentId, gold=goldrows[0], mode='trueneg')
		else:
			for grow in goldrows:
				goldcount += 1
				try:
					if grow['tspan'] and grow['sspan']:
						gtspan = tuple([int(cpos) for cpos in grow['tspan'].split(u',')])
						gsspan = tuple([int(cpos) for cpos in grow['sspan'].split(u',')])
					else:
						gtspan = (-1,-1)
						gsspan = (-1,-1)
				except ValueError:
					logging.error(u'error extracting spans: %s', pprint.pformat(grow))
					raise
				foundMatch = False
				if responserows:
					for i, rrow in enumerate(responserows):
						if i in countedresponses:
							continue
						rtspan = (rrow['lm']['target']['start'],rrow['lm']['target']['end'])
						rsspan = (rrow['lm']['source']['start'],rrow['lm']['source']['end'])
						if overlaps(gtspan,rtspan) and overlaps(gsspan,rsspan):
							# it's a match
							logging.debug(u'true positive: gold=%s\n\n\nresponse=%s',pprint.pformat(goldrows),pprint.pformat(responserows))
							printCompRow(ofile,sentId,gold=grow,result=rrow,mode='truepos')
							countedresponses.add(i)
							foundMatch = True
							truepos += 1
							rcount += 1
						else:
							logging.debug(u'no overlap: %s <> %s, and %s <> %s',
											pprint.pformat(gtspan),pprint.pformat(rtspan),
											pprint.pformat(gsspan),pprint.pformat(rsspan))
				if not foundMatch:
					# false negative
					logging.debug(u'false negative: gold=%s\n\n\nresponse=%s',pprint.pformat(goldrows),pprint.pformat(responserows))
					printCompRow(ofile,sentId,gold=grow,mode='falseneg')
			
		# remaining responserows had no match
		if not responserows:
			continue
		for i, rrow in enumerate(responserows):
			if i in countedresponses:
				continue
			logging.debug('false positive: gold=%s\n\n\nresponse=%s',pprint.pformat(goldrows),pprint.pformat(responserows))
			printCompRow(ofile,sentId, gold=goldrows[0], result=rrow,mode='falsepos')
			rcount += 1
			# these had no gold match: false positives
	
	if goldcount > 0:
		recall = float(truepos) / float(goldcount)
		print "Recall: %d / %d = %.4f" % (truepos, goldcount, recall )
	if goldcount > 0:
		precision = float(truepos) / float(rcount)
		print "Precision: %d / %d = %.4f" % (truepos, rcount, precision)
	if recall and precision:
		print "Accuracy: %.4f" % (recall * precision)
		
	return 0


if __name__ == "__main__":
    status = main()
    sys.exit(status)


	
