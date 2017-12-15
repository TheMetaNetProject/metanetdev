#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: externalExtr
    :platform: Unix
    :synopsis: Language Model System (LMS) linguistic metaphor extractor for Persian.

DEPRECATED.

Language Model System (LMS) linguistic metaphor extractor for Persian.  Uses lexicons,
unigram, bigram, and trigram frequency data which is stored by default in

``/u/metanet/extraction/persian``

This path can be changes via a initialization parameter.

"""
import segExtractor
from finalTagger import hmm_tagger
import json
import sys, logging, pprint
import codecs
import re
import os
import random
from mozextractor import mozextract
from persiantagger import PersianPOSTagger

REPDIR = '/u/metanet/extraction/persian'

# the script reads in a json file, calls the extractor and generates a new
# json file (with a '.lms' extension and adds the extracted LMs to the output
# file.
# python externalExtr.py inputJsonFile

class PersianMetaphorExtractor:
    """
    The class is the main interface for Persian Metaphor Extraction.
    It includes methods for loading various lexicons and the complete
    pipeline for preprocessing, metaphor extraction, and output
    generation, and allows for the overhead of loading resources
    to be paid at initialization time.
    """
    def __init__(self, repDir=None, verbose=False):
        """
        :param repDir: path to distributional statistical data
        :type repDir: str
        :param verbose: flag for verbose messages
        :type verbose: bool
        """
        global REPDIR
        self.logger = logging.getLogger(__name__)
        # for pos tagger
        if repDir:
            self.repDir = repDir
        else:
            self.repDir= REPDIR
        self.verbose = verbose
        self.fpOne = codecs.open(self.repDir + '/bigramProb.txt','r','utf-8').read()
        self.fpTwo = codecs.open(self.repDir + '/lexProb.txt','r','utf-8').read()
        
        # read in the LM
        self.triModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.trigram")
        self.bigModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.bigrams")
        self.uniModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.unigrams.sortCleaned")
        
        self.tgtHash = self.readInLex(self.repDir + "/tgtLexExt3.txt")
        self.srcHash = self.readInLex(self.repDir + "/srcLexExt3.txt")
        self.mozList = []
        #self.posFile = codecs.open(self.repDir + '/tmpPOS.txt','w','utf-8')

    def readLM(self, lmPath):
        """
        Load a language model into a dictionary.
        """        
        lmFile = codecs.open(lmPath)
        bigHash = {}
        while 1:
            biLine = lmFile.readline()
            if not biLine or biLine.strip() == "":
                break
            tokList = biLine.split("\t")
    
            try:
                prob = float(tokList[0])
            except:
                self.logger.error(u'biLine: %s',biLine)
                self.logger.error(u'tokList %s',pprint.pformat(tokList))
            bigr = tokList[1]
            bigHash[bigr.strip()] = prob
        return bigHash
    
    ###################################################
    def readInLex(self, lexPath):
        """
        Loads a lexicon into a dictionary and returns it.
        """
        lexFile = codecs.open(lexPath)
        lexHash = {}
        while 1:
            lex = lexFile.readline()
            if not lex:
                break
            lex = lex.strip()
            if lex not in lexHash:
                lexHash[lex] = 1
        return lexHash
    ###################################################
    # prepare the hash for writing the element info into json
    def prepElement(self, elem, sent):
        """
        Prepares a dictionary for writing an element into a json object.
        """
        elemDict = {}
        #start = unicode(sent).find(elem)
        #end = start + len(elem)
        elemDict["start"] = 0#start
        elemDict["end"] = 1#end
        elemDict["form"] = elem
        elemDict["lemma"] = elem
        elemDict["rel"] = 'None'
        return elemDict

    ###################################################    
    def combineSrcTgt(self, src, tgt, sent):
        """
        Combines the extracted source and target segments and returns the
        metaphoric segment.
        """
        sent =sent.encode("utf-8")
        srcInx = tgtInx = 0

        # locating the src tgt in the sentence
        srcTgtInx = sent.find (src + " " + tgt)
        tgtSrcInx = sent.find (tgt + " " + src)
        
        if srcTgtInx >= 0:
            srcInx = srcTgtInx
            tgtInx = srcTgtInx + len(src) + 1
        elif tgtSrcInx >= 0:
            tgtInx = tgtSrcInx
            srcInx = tgtSrcInx + len(tgt) + 1
        # if source and target are not next to each other, locate them separately
        else:
            srcInx = sent.find(src)
            tgtInx = sent.find(tgt)
        
        #srcInx = sent.find(src)
        #tgtInx = sent.find(tgt)
        start = min(srcInx, tgtInx)
        end = 0
        
        if srcInx < tgtInx:
            #print "src < tgt"
            # if target is not very far from source, the get the maximum span 
            if tgtInx < (srcInx + len(src) + 10):
                end = tgtInx + len(tgt)
                try: 
                    #print "@@@@@", sent[start:end]
                    return sent[start:(end)].decode('utf-8')
                except UnicodeDecodeError:
                    self.logger.error(u'unicode error in sentence: %s',sent)
        else:
            #print "tgt < src", srcInx, tgtInx, sent
            # if target is after source, return only the source
            if srcInx < (tgtInx + len(tgt) + 10):
                end = srcInx + len(src)
                try:
                    return sent[start:end].decode('utf-8')
                except UnicodeDecodeError:
                    self.logger.error(u'unicode error in sentence: %s',sent)
        return None
    

 
##############################################                                    
    def tokenize(self, perSent):
        """
        Preprocesses a sentence and calls an external Persian tokenizer.
        Returns the a tokenized form of the input sentence. 
        """
        owd = os.getcwd()
        # BEH
        temppath = '/scratch/tmp/metaextracttemp'
        #temppath = './'
        
        if not os.path.isdir(temppath):
            os.makedirs(temppath)
        randStr = str(random.randint(0, 100000000))
        tempIN= temppath + "/IN" + randStr + ".txt"
        tempOUT = temppath + "/OUT"+ randStr + ".txt"
        tmpFile = codecs.open(tempIN,"w","utf-8")
        tmpFile.write(perSent)
        tmpFile.close()
        os.system(self.repDir + "/tokenizer-per.sed " + tempIN + " > " + tempOUT)
        tmpFile = codecs.open(tempOUT,'r','utf-8')
        tokSent = tmpFile.readline().strip()
        tmpFile.close()
        os.remove(tempIN)
        os.remove(tempOUT)
        return tokSent

    ###################################################    

    def parse(self, jObj):
        """
        Reads in a json object for a set of sentences.  The method calls 
        the POS tagger and parser on the set of sentences and extracts and 
        returns Persian Ezafeh constructions from the sentences.
        """
        self.logger.info('running Persian HMM POS tagger...')
        persianPOSTagger = PersianPOSTagger()
        sents = jObj['sentences']
        # for all sentences, call the extracor to get metaphoric segments.
        # create an LM list and add each segment under the "name" field.
        probList = []
        sntCt = -1
        posLines = []
        for snt in sents:
            sntCt += 1
            txt = snt["text"]
            if txt.strip() != "":
                perSent = persianPOSTagger.cleanText(txt).replace("/","-")
                try:
                    posLines += persianPOSTagger.run_hmm_tagger(perSent)
                    posLines += ["\n"]
                except:
                    #print "problem pos tagging the following sentence which will be skipped"
                    #print perSent
                    posLines += ["NONE/NN\n"]
                

        try:
            self.mozList = mozextract(posLines)
            return self.mozList
        except:
            self.logger.debug("problem with parsing")
            self.mozList = []
            for i in range(len(sents)):
                self.mozList.append([])
                    
    def find_LMs(self, jObj):
        """
        A higher level method that reads in a json object (containing 
        a set of sentences, preprocesses, parses and extract metaphoric segments
        and write the results into a new a json object which will be returned 
        
        :param jObj: MetaNet JSON format structure
        :type jObj: dict
        :returns: MetaNet JSON format structure
        """
        sents = jObj['sentences']
        # for all sentences, call the extracor to get metaphoric segments.
        # create an LM list and add each segment under the "name" field.
        ct = -1
        for snt in sents:
            # BEH has to be removed later
            # snt["lms"] = []
            ct += 1
            txt = snt["text"]
            
            # call the extract method to find a list of metaphoric expressions  
            # returns empty list if nothing found
            # print ct
            # print self.mozList
            metList = segExtractor.extract(txt,self.uniModel,self.bigModel,self.triModel,
                                           self.srcHash, self.tgtHash, self.repDir,
                                           self.fpOne, self.fpTwo, self.mozList[ct])
            
            lmsList = []
            
            if metList:
                lmsDict = {}
        
                for extrSrc in metList[0]:
                    for extrTgt in metList[1]:
                        combLM = self.combineSrcTgt(extrSrc, extrTgt, txt)
                        if not combLM:
                            continue
                        lmsDict["name"] = combLM
                        lmsDict["seed"] = u'NA'
                        lmsDict["extractor"] = u'LMS'
                        #print txt
                       
                        #print "src:", extrSrc
                        #print "tgt:", extrTgt
                        srcElem = self.prepElement(extrSrc, txt)
                        lmsDict["source"] = srcElem
                        
                        tgtElem = self.prepElement(extrTgt, txt)
                        lmsDict["target"] = tgtElem
                        if (lmsDict not in lmsList) and srcElem != tgtElem:
                            lmsList.append(lmsDict)
                            #print "metaphor:", combLM
            #else:
            #    print "-----", txt
            # if there is any metaphoric segment, then add it to the snt
            if len(lmsList) > 0:
                snt["lms"] = lmsList
        return jObj
    
    def writejson(self,jObj,fname):
        """
        Custom json writer to circumvent Persian-specific bugs in json handling.
        """
        jOut = codecs.open(fname,"w",encoding='utf-8')
        json.dump(jObj, jOut, encoding='utf-8')
	

def main():
    if len(sys.argv) < 2:
        print "use the following:"
        print "python externalExtr.py input-json-file"
        print "   e.g. \"python externalExtr.py TestInput-fa.json\""
        sys.exit()
    logging.basicConfig()
    # BEH
    repDir = '/u/metanet/extraction/persian'
    #repDir = './'
    jObj = json.load(file(sys.argv[1]), encoding='utf-8')

    # process and write
    pext = PersianMetaphorExtractor(repDir)
    pext.parse(jObj)
    jObj = pext.find_LMs(jObj)
    pext.writejson(jObj,'processed.'+sys.argv[1])
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

