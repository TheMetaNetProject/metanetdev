# -*- coding: utf-8 -*-
"""
.. module:: mozextractor
	:platform: Unix
	:synopsis: helper utility for extracting ezafe constructions

Helper utility for extracting ezafe constructions using dependency parse information.

.. moduleauthor:: Kouros Falati <kourosf@icsi.berkeley.edu>

"""
import sys, re, codecs, os, inspect, random
def mozextract(lines):
	"""
	The functions is a simple Python wrapper around the Malt dependency
	parser in which the Ezaafeh constructs are being extracted and returned.
	the function reads a set of sentences and perform the preprocessing to form
	a pre-parser file, runs the parser and then processes the parsed ouput.
	While processing it looks for the Persian Ezafeh constructions and 
	returns all of them in a list of lists (one list of Ezafeh constructs
	per sentence)
	"""
	if not lines:
		#print "please provide valid POS-tagged sentences"
		quit()
	#posinput = open(sentence, 'r')
	#lines = posinput.readlines()
	#posinput.close()
	
	owd = os.getcwd()
	temppath = '/scratch/tmp/metaextracttemp'
	if not os.path.isdir(temppath):
		os.makedirs(temppath)

	#creates temporary conll file to feed to maltparser with only the token and tags filled in
	tempname = temppath + '/temp'+str(random.random())
	temp = codecs.open(tempname, 'w')
	i=1
	for line in lines:
		token = line.rstrip("\n").encode("utf-8").split("/")
		a = token[0]
		#if a == '.' or a == "!" or a == u'\u061F':
		if line.strip() == "":
			#temp.write('%d' % (i)+'\t'+a+'\t'+'_'+'\t'+token[1]+'\t'+token[1]+'\t'+'_'+'\t'+'_'+'\t'+'_'+'\t'+'_'+'\t'+'_'+'\n\n')
			temp.write("\n")
			i=1
		else:
			temp.write('%d' % (i)+'\t'+token[0]+'\t'+'_'+'\t'+token[1]+'\t'+token[1]+'\t'+'_'+'\t'+'_'+'\t'+'_'+'\t'+'_'+'\t'+'_'+'\n')
			i+=1
	temp.close()

	#parses the temporary file with the specified option tile and parser and outputs it to a temporary parsed file
	outputtempname = temppath + '/tempparsed'+str(random.random())
	trainpath = '/u/metanet/extraction/persian'
	os.chdir(trainpath)
	os.system("java -Xmx1024m -jar /u/metanet/extraction/persian/maltparser-1.7.2/maltparser-1.7.2.jar -c traindefault -i %s -o %s -m parse -v off" % (tempname, outputtempname))
	os.chdir(owd)

	#opens parsed sentences
	outtemp = codecs.open(outputtempname, 'r')
	multi = outtemp.read()
	sentence = multi.split('\n\n')
	outtemp.close()
	os.remove(tempname)
	os.remove(outputtempname)

	finallist = []
	for item in sentence:
		try: #try/except is used in case there are multiple blank lines in the input
			sentencefinal = [] 
			lines = item.split('\n')
			prevset = set()
			for item in lines:
				wanted = {} #this is the dictionary containing the words for the final output
				moznumbers = [] #these are the ID numbers of the MOZ words
				headnumbers = []
				word = item.rstrip('\n').split('\t')
				relation = word[7] #dependency relation
				number = word[0] #ID number
				head = word[6] #ID number of head
				if relation == "MOZ":
					wanted[number] = word[1] #records MOZ token 
					moznumbers.append(number) #stores ID number of MOZ token
					headnumbers.append(head) #stores ID number of head

					for item in lines:
						word = item.rstrip('\n').split('\t')
						relation = word[7]
						number = word[0]
						head = word[6]
						if head in moznumbers and relation == "MOZ": #finds MOZ tokens dependent on MOZ words and stores their ID numbers
							wanted[number] = word[1]
							moznumbers.append(number)


					for item in lines:
						word = item.rstrip('\n').split('\t')
						relation = word[7]
						number = word[0]
						head = word[6]
						if number in headnumbers and word[3] != "PUNC": #finds heads of MOZ tokens and outputs them
							wanted[number] = word[1]

				#this block only outputs MOZ tokens if something is dependent on them and eliminates redundancies in case of recursive dependencies
				if len(wanted) > 1: 
					sortedwanted = [x for x in wanted.iteritems()] 
					sortedwanted.sort(key=lambda x: int(x[0])) # sorts by ID number so words come out in order
					sortedset = set(sortedwanted)
					if not sortedset.issubset(prevset): #checks if the tokens have already been outputted to avoid duplicates
						phraseitems = []
						for item in sortedwanted:
							phraseitems.append(item[1])
						prevset = sortedset
						phrase = ' '.join(phraseitems) #creates strings of each relevant construction
						sentencefinal.append(phrase)	
			if sentencefinal: #adds the list of strings to the final list
				finallist.append(sentencefinal)
			else:
				finallist.append([])
		except:
			pass
	#print "done with MOZ extraction"
	return finallist
		  
