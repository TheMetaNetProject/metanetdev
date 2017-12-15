#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import csv
from xml.dom import minidom

def main():
	"""
	analyze results from compare.py
	"""
	if len(sys.argv) < 2 or len(sys.argv) > 3:
	      print "usage: %s 'Corrected CSV file[s]' file" % sys.argv[0]
	      print ""
	
	for file in sys.argv[1:]:
		print file+":"
		cfil = open(file, 'r')
		cdoc = csv.reader(cfil)
		fnpars = "parse"
		recall,precision = globals()[fnpars](cdoc)
		print recall
		print precision
		cfil.close()
	return 0 

def parse(cvsdoc):
	prenum,recnum,prednm=0,0,0
	#(Start at negative one due to header row)
	recdnm=-1
	for row in cvsdoc:
		if row[4] != "y":
			recdnm+=1
			try:
				i = float(row[12])
			except:
				i = 0
			if i==1:
				recnum+=1
		try:
			j = float(row[3])
		except:
			j = 0
		if (row[7] != "y") & ((j != 0)|(i == 1)):
			prednm+=1
	

	recall = "recall: %s/%s = %.2f"%(recnum,recdnm,float(recnum)/float(recdnm))
	precision = "precision: %s/%s = %.2f"%(recnum,prednm,float(recnum)/float(prednm))
	return (recall, precision)


if __name__ == "__main__":
    status = main()
    sys.exit(status)

