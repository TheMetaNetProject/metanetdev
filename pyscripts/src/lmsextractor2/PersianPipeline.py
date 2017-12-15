#!/usr/bin/python
#  -*- coding: utf-8 -*-


import codecs
import sys, logging, os
import re
from nltk.tag.stanford import POSTagger

from behmalt import MaltParser

sys.stdout = codecs.getwriter("utf8")(sys.stdout)


class PersianPipeline:

	def __init__(self, posTagModelPath, posTaggerPath, parserModelPath, workingDir):
		
		
		
		try:
			self.logger = logging.getLogger(__name__)
			self.posTagger = POSTagger(posTagModelPath, posTaggerPath,encoding="UTF-8", java_options='-Xmx16000m')
			#self.posTagger = POSTagger(posTagModelPath, posTaggerPath,"UTF-8")
			#print "pos tagger is loaded"
		except:
			self.logger.warning("Error in loading POS tagger!")
			e = sys.exc_info()[0]
			self.logger.warning("Error:" + str(e))
					
		
		try:
			self.parser = MaltParser(tagger=None, mco = parserModelPath, working_dir= workingDir, additional_java_args=['-Xmx16000m']) 
			#print "parser is loaded"
		except:
			self.logger.warning("Error in loading the MALT Parser")
			e = sys.exc_info()[0]
			self.logger.warning("Error:" + str(e))				
	
	# tokenizes, fixes some of the detached affixes
	def preprocess(self, s):
		# remove the diacritics
		drs = s
		for c in range(1611, 1619):
			drs = drs.replace(unichr(c),"")
		# normalize the Arabic yaa
		drs = drs.replace(unichr(1610),unichr(1740))
		drs = drs.replace(unichr(1609),unichr(1740))
		
		# tokenize the sentence
		ts = self.seperatePuncs(drs)
		# fix the affixes
		afs = self.fixAffixes(ts)
		
		# replace slashes and pounds and underlines
		afs= afs.replace("#","-")
		afs= afs.replace("/","-")
		afs = afs.replace("_","-")
		return afs
	
	def preprocess4Annotation(self, s):
		ps = self.preprocess(s)
		ts = self.posTagASentence(ps)
		if ts:
			print "pos tagged"
		else:
			print "tagging failed"
		attS = self.attachPerCompounds(ts)
		#" ".join(attS.split)
		# get the first element of pos tuples and join them to form the sentence
		# replace the ^ sign (from compound attaching) with space
		finalS = " ".join(map(lambda x: x[0].replace("^"," "), attS))
		return finalS
	# tokenize a persian sentence
	def seperatePuncs(self, s):
		
		s = re.sub(ur"([\[{\(\\`\"‚„†‡‹‘’“”•\.–—›««])", r"\1 ", s)
		s = re.sub(ur"([\]}\'\`\"\),;:!\?\%‚„…†‡‰‹‘’“”•–—›»\.])", r" \1", s)
		# persian specific
		s = re.sub(ur"([،؛؟،\.])", r" \1 ", s)
		s = s.replace("  ", " ")
		return s
	
	

	def fixAffixes(self, sent):
		suffList = [u"ها", u"های"]
		sSent = sent.split(" ")
		newTokSent = []
		sentLen = len(sSent)
		i = 0
		try:
			while i < sentLen:
	
				if sSent[i] in suffList and newTokSent:
					#print "+++ Affix problem got fixed"
					# attach the suffix to the previous word
					newTokSent[-1] = newTokSent[-1] + u"\u200c" + sSent[i]
				else:
					newTokSent.append(sSent[i])
				i += 1
			return " ".join(newTokSent)
		except:
			return sent 

	
		
	def posTagASentence(self, sent):
		try:
			sent = sent.replace("/","-")
			posSent = self.posTagger.tag(sent.split())
			return posSent
		except:
			self.logger.warning("problem in pos!" + sent)
			return None

	# Function reads in a POS tagged sentence (list) and if there are two adjacent verbs, it attaches them together and make them one word.
	def attachPerCompounds(self, posSent):
			
		prFlag = False
		ct = senCt = prCt = 0
		i = 0
		senCt += 1
		pos = wd = outWd = ""
		sentLen = len(posSent)
		newPOSSent = []
		while i < sentLen - 1:
			ct += 1
			tok = posSent[i]
			nexTok = posSent[i+1]
			(wd, pos) = tok
			(nwd, npos) = nexTok
			outWd = wd 
			if pos == "V":
				if npos == "V":
					prFlag = True
					outWd = wd + '^' + nwd
					pos = "V"
					i += 1
			# attaching the "mi" prefix for present continious form
			if npos == "V" and wd.strip() == u"می":		
				prFlag = True
				outWd = u"می" + u"\u200c" + nwd
				pos = "V"
				i += 1
				#print "the mi case "
				#t.write("outWd:" + outWd + "\n")
				
				
			newPOSSent.append((outWd, pos))
			i += 1
		
		# don't forget the last word (if not processed)
		if i < sentLen:
			ct += 1
			tok = posSent[-1]
			newPOSSent.append(tok)
			
		# counting the lines with compound verbs patterns
		if prFlag:
			prCt += 1
		#print prCt
		
		#t.write(newPOSSent[-2][0] + "--" + newPOSSent[-1][0] + "\n")
		return newPOSSent
################################################################
		
		
	def parseATaggedSentence(self, tSent):
		try:

			compTSent = self.attachPerCompounds(tSent)
			depParse = self.parser.tagged_parse(compTSent)

			if depParse:
				pl = depParse.to_conll(10).replace("^", " ")
				return pl
			else:
				return None
			
		except Exception, e:
			print "Error in parsing a sentence!" + str(e)  
			return None
		
	def parseASentence(self, sent):
		pass
	
	def rawtoParse(self, sent):
		if not sent:
			return None
		try:
			s = self.preprocess(sent)
			ts = self.posTagASentence(s)
			if not ts:
				print "problem in pos tagging in raw to parse"
			# attaching the compound verbs with a ^ sign
			attS = self.attachPerCompounds(ts)
			parsedLine = self.parseATaggedSentence(attS)
			# make the compounds more readable
			return parsedLine
		except:
			print "Error in Raw2Parse"
			return None
			
			
		

def main():
	
	posModPath = "/u/metanet/persianCode/PersianPipeline/models/persian-train.model"
	posJar = "/u/metanet/nlptools/stanford-postagger-full-2014-06-16/stanford-postagger.jar"
	#parserModPath = "test"
	parseModPath = "PerParseModelWithCompoundTerms"
	#parserPath = "/u/metanet/nlptools/maltparser-1.8/"
	workDir = "./" 
	ct = 0

	FORMAT = '%(asctime)-15s - %(message)s'
	DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
	logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT,level=logging.INFO)

	sampleF = codecs.open(sys.argv[1], "r", "utf-8")
	# instantiating the persian pipeline with path to the parser and pos tagger and their models
	pPipeline = PersianPipeline(posModPath, posJar, parseModPath, workDir,logger)
	outPath = sys.argv[2]
	outFile = codecs.open(outPath, "w", "utf-8")
	while True:
		ct += 1
		line = sampleF.readline()
		if not line:
			break
		print "sentence ", ct,
		outFile.write(line + "\n")
		parsedL = pPipeline.rawtoParse(line)
		outFile.write(parsedL + "\n")
		"""
		tokLine = pPipeline.preprocess4Annotation(line)
		outFile.write(tokLine + "\n")
		#tokLine = pPipeline.preprocess(line)
		taggedLine = pPipeline.posTagASentence(tokLine)
		print "tagged", 
		
		parsedLine = pPipeline.parseATaggedSentence(taggedLine)
		# make the compounds more readable
		print "parsed"
		outFile.write(parsedLine + "\n")
		"""

if __name__ == "__main__":
    status = main()

