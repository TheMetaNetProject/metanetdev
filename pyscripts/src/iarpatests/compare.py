#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: compare
    :platform: Unix
    :synopsis: Gold standard testing comparison script

A script that compares the output of the LM extractor with gold standard answers
and outputs recall and precision scores.  Compares the extractor's XML output
to responses in a CSV file.

.. moduleauthor:: Luke Gottlieb <luke@icsi.berkeley.edu>
"""
import os
import sys
from optparse import OptionParser
import csv
from xml.dom import minidom

def main():
	"""
	compare m4detect ouput file to expected output from gsdb2-m4detect-input.py
	"""


	parser=OptionParser()
	parser.add_option("-g", dest="gov",
			  help="File containing responses from government")
	parser.add_option("-i", dest="icsi",
			  help="File containing responses from icsi")
	parser.add_option("-o", dest="out",
			  help="Optional output filename, if not present outputs to command line")
	
	(options, args) = parser.parse_args()
	
	if not options.gov:
		print 'ERROR: Government file missing'
		parser.print_help()
		return 75
# 		sys.exit(75)
	if not options.icsi:
		print 'ERROR: ICSI file missing'
		parser.print_help()
		return 75 
# 		sys.exit(75)
	
	
	xdoc = minidom.parse(options.icsi)
	cfil = open(options.gov, 'r')
	cdoc = csv.reader(cfil)
	 
	#Populate dictionary from csv file
	csvholder = {}
	i = 0
	for row in cdoc:
		csvholder[i]=(row[4],row[2],row[8],row[9],row[7],row[6],row[10])
		i+=1
	
	#Remove header rows from dictionary
	del csvholder[0]
	del csvholder[1]
	
	#Parse xml file
	metads = xdoc.getElementsByTagName("metad:Result")
	
	if options.out:
		file = open(options.out, "w")
	else:
		import tempfile
		file = tempfile.TemporaryFile()
	
	recallnum=0
	recalldenum=0
	precisionnum=0
	precisiondenum=0
	file.write("Gov Target ID,Gov Source ID,ICSI Target ID,ICSI Source ID,Gov Duplicated,Gov Target,Gov Source,ICSI Duplicated,ICSI Target,ICSI Source,Target Match,Source Match,Both Match,Sentence\n")
	for key in csvholder:
		csvcount=0
		gtId = csvholder[key][1]
		gsId = csvholder[key][0]
		gLmTT = csvholder[key][2]
		gLmST = csvholder[key][3]
		gsent = csvholder[key][5]
		tconc = csvholder[key][6]
		recalldenum+=1
		gcnt=0
		for key in csvholder:
			gtId2 = csvholder[key][1]
			gsId2 = csvholder[key][0]
			if (gtId==gtId2)&(gsId==gsId2):
				gcnt+=1
		if gcnt > 1:
			gdup = "y"
		else:
			gdup = ""
				
		for metad in metads:
			sId = unicode(metad.getAttribute("sentenceId")).encode('utf8')
			tId = unicode(metad.getAttribute("testItemId")).encode('utf8')
			LmTT = unicode(metad.getElementsByTagName("metad:LmTargetText")[0].firstChild.data).encode('utf8')
			LmST = unicode(metad.getElementsByTagName("metad:LmSourceText")[0].firstChild.data).encode('utf8')
			icnt = 0
			for metad in metads:
				sId2 = unicode(metad.getAttribute("sentenceId")).encode('utf8')
				tId2 = unicode(metad.getAttribute("testItemId")).encode('utf8')
				if (tId==tId2)&(sId==sId2):
					icnt+=1
				if icnt > 1:
					idup = "y"
				else:
					idup = ""
	
	
	
			if (sId == gsId) & (int(tId[2:]) == int(gtId)):
				csvcount+=1
				precisiondenum+=1
				if csvcount==1:
					recallnum+=1
				TT=0
				ST=0
				M=0
				if (gLmTT.lower() in LmTT.lower())|(LmTT.lower() in gLmTT.lower()):
					if gLmTT.lower():
						TT=1
				if (gLmST.lower() in LmST.lower())|(LmST.lower() in gLmST.lower()):
					if gLmST.lower():
						ST=1
				
				if (ST==1)&(TT==1):
					precisionnum+=1
					M=1
				file.write('%s,%s,%s,%s,%s,"%s","%s",%s,"%s","%s",%s,%s,%s,"%s","%s"\n'%(gtId,gsId,tId,sId,idup,gLmTT,gLmST,gdup,LmTT,LmST,TT,ST,M,gsent.replace('"','""'),tconc))
		if csvcount == 0:
			if not gLmST:
				file.write('%s,%s,%s,%s,,"%s","%s",,%s,%s,1,1,1,"%s","%s"\n'%(gtId,gsId,0,0,gLmTT,gLmST,0,0,gsent.replace('"','""'),tconc))
			else:
				file.write('%s,%s,%s,%s,,"%s","%s",,%s,%s,0,0,0,"%s","%s"\n'%(gtId,gsId,0,0,gLmTT,gLmST,0,0,gsent.replace('"','""'),tconc))
	try:
		recall = float(recallnum)/recalldenum
	except ZeroDivisionError:
		recall = float(0)
	
	try:
		precision = float(precisionnum)/precisiondenum
	except ZeroDivisionError:
		precision = float(0)
	
	if not options.out:
		file.seek(0)
		print file.read().strip()
	
	print "Recall: %s/%s=%s"%(recallnum,recalldenum,recall)
	print "Precision = %s/%s=%s"%(precisionnum,precisiondenum,precision)
	
	file.close()
	
	return 0


if __name__ == "__main__":
    status = main()
    sys.exit(status)


	
