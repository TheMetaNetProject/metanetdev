#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: externalExtr
    :platform: Unix
    :synopsis: Language Model System (LMS) linguistic metaphor extractor for Persian.

Language Model System (LMS) linguistic metaphor extractor for Persian.  Uses lexicons,
unigram, bigram, and trigram frequency data which is stored by default in

``/u/metanet/extraction/persian``

This path can be changes via a initialization parameter.

"""
import segExtractor
import json
import sys, logging
import codecs
import re
import os
import random
from PersianPipeline import *
import inflectPersian
import processParseTree

REPDIR = '/u/metanet/extraction/persian/lms2/'

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
        #B#self.fpOne = codecs.open(self.repDir + '/bigramProb.txt','r','utf-8').read()
        #B#self.fpTwo = codecs.open(self.repDir + '/lexProb.txt','r','utf-8').read()
        
        # read in the LM
        #B#self.triModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.trigram")
        #B#self.bigModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.bigrams")
        #B#self.uniModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.unigrams.sortCleaned")
        
        #B#self.tgtHash = self.readInLex(self.repDir + "/tgtLexExt3.txt")
        #B#self.srcHash = self.readInLex(self.repDir + "/srcLexExt3.txt")
        
        posModPath = "/u/metanet/persianCode/PersianPipeline/models/persian-train.model"
        posJar = "/u/metanet/nlptools/stanford-postagger-full-2014-06-16/stanford-postagger.jar"
        parseModPath = "PerParseModelWithCompoundTerms"
        parserPath = "/u/metanet/nlptools/maltparser-1.8/"
        
        parseModelSymLink = self.repDir +"/PerParseModelWithCompoundTerms.mco"
        if not os.path.isfile(parseModelSymLink):
            os.symlink("/u/metanet/persianCode/PersianPipeline/models/PerParseModelWithCompoundTerms.mco", parseModelSymLink)
            
        # Steve: comment cause already set in /u/metanet/etc/metanet.bashrc
        #os.environ["JAVAHOME"] = "/usr/lib/jvm/jre-1.7.0-oracle.x86_64/bin/java"
        #os.environ["JAVA_HOME"] = "/usr/lib/jvm/jre-1.7.0-oracle.x86_64"
        #os.environ["MALTPARSERHOME"] = "/u/metanet/nlptools/maltparser-1.8/maltparser-1.8.jar"
        #oPath = os.environ["PATH"]
        #os.environ["PATH"] = "/usr/lib/jvm/jre-1.7.0-oracle.x86_64/bin:" + oPath     
        self.lemHash = {}
        self.srcHash = inflectPersian.readLUs("/u/metanet/extraction/persian/lms2/LUList.src.txt", True, self.lemHash)
        self.tgtHash = inflectPersian.readLUs("/u/metanet/extraction/persian/lms2/LUList.tgt.txt", False, self.lemHash)
        #self.srcHash = inflectPersian.readLUs("/u/metanet/persianCode/beh/code/sysOct2014/LUListBks/tempLUList10.src.txt", True, self.lemHash)
        #self.tgtHash = inflectPersian.readLUs("/u/metanet/persianCode/beh/code/sysOct2014/LUListBks/tempLUList10.tgt.txt", False, self.lemHash)
                
        
        self.srcLUList = self.srcHash.keys()
        self.tgtLUList = self.tgtHash.keys()
        
        self.stopList = [u"ان", u"در", u"بر",u"از", u"تا"]

        # note: parser's working directory is repDir.  That's the place NLTK writes the temp parsing files
        # We need to have a symbolic link from that working directory to the actual persian parse model (*.mco)
        #self.currDir = os.getcwd()
            
        self.perPipeline = PersianPipeline(posModPath, posJar, parseModPath, self.repDir)
        #os.chdir(self.currDir)
        #print "done with loading the persian pipeline"
        
        self.mozList = []
        
    ###################################################
    # prepare the hash for writing the element info into json
    def prepElement(self, elem, sent, infHash, isSrc):
        """
        Prepares a dictionary for writing an element into a json object.
        """
        elemDict = {}
        start = unicode(sent).find(elem)
        end = start + len(elem) - 1
        elemDict["start"] = start
        elemDict["end"] = end
        elemDict["form"] = elem
        # source element
        if isSrc:
            if elem in self.srcHash:
                elemDict["concept"] = self.srcHash[elem][0]
        # it's a target element
        else:
            if elem in self.tgtHash:
                elemDict["concept"] = self.tgtHash[elem][0]
        
        # if segment in an inflected form of a lemma, then get the lemma
        if elem in infHash:
            elemDict["lemma"] = infHash[elem]
        else:
            elemDict["lemma"] = elem
        
        return elemDict
    ###################################################    
    def noOverlap(self, s1, s2):
        if s1 == s2:
            return False
        if s1 in s2:
            return False
        if s2 in s1:
            return False    
        return True

    ###################################################    
    # this method checks if the extracted src+target segment together is not stored as a lexical unit in the 
    # source or target lexicons
    def filterSrcTgtOnlyMets(self, src, tgt, seg):
        m1 = src.strip() + " " + tgt.strip()
        if m1 in seg and m1 not in self.srcHash and m1 not in self.tgtHash:
            return True
        m2 = tgt.strip() + " " + src.strip()
        if m2 in seg and m2 not in self.srcHash and m2 not in self.tgtHash:
            return True
        if m1 not in seg and m2 not in seg:
            return True
        return False
    
    ###################################################  
    def combineSrcTgt(self, src, tgt, sent):
        """
        Combines the extracted source and target segments and returns the
        metaphoric segment.
        """
        #sent =sent.encode("utf-8")
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
            
            # if target is not very far from source, the get the maximum span 
            if tgtInx < (srcInx + len(src) + 10):
                end = tgtInx + len(tgt)
                try: 
                    return sent[start:(end)]#.decode('utf-8')
                except UnicodeDecodeError:
                    self.logger.error(u'unicode error in sentence: %s',sent)
        else:
            #print "tgt < src", srcInx, tgtInx, sent
            # if target is after source, return only the source
            if srcInx < (tgtInx + len(tgt) + 10):
                end = srcInx + len(src)
                try:
                    return sent[start:end]#.decode('utf-8')
                except UnicodeDecodeError:
                    self.logger.error(u'unicode error in sentence: %s',sent)
        return None
    ######################################################################
 
    def selectTheLMsBoundary(self, extracts,sen):
        lmsList = [] 
        # this lists keeps tracks of extracted metaphoric segments that we avoid repetitions
        metSegList =  []
        srcTgtTupList = []
        for exSet in extracts:
            k = -1
            for extr in exSet:
                mFlag = False
                extrSrc = extrTgt = ""
                lmsDict = {}                    
                k += 1
                if extr != []:                        
                    lmsDict["name"] = extr[0]
                    lmsDict["seed"] = u'NA'
                    lmsDict["extractor"] = u'LMS2'
                    lmsDict["score"] = 0.5
                    ys = 0
                    yt = 0
                    
                    # look for the match, skip the source of target LU matches if they're stop word.                    
                    while (ys < len(extr[1])) and (yt < len(extr[2])):
                        #ys += 1
                        #yt += 1
                        extrSrc = extr[1][ys]
                        extrTgt = extr[2][yt]                                                
                        if extrSrc in self.stopList:
                            ys += 1
                            continue
                        if extrTgt in self.stopList:
                            yt += 1
                            continue
                        
                        ###############################
                        # this was an effort to extend the boundary of source or target beyond the 1-2 tokens.  
                        # but experiments proved that the original code was better and more accurate.
                        """
                        tgtInx = extr[0].find(extrTgt)
                        srcInx = extr[0].find(extrSrc) 
                                                    
                        if tgtInx > srcInx:
                            #extrSrc = extr[0][srcInx:tgtInx]
                            newTgtInx = srcInx + len(extrSrc) + 1
                            endOldTgt = tgtInx + len(extrTgt)
                            extrTgt = extr[0][newTgtInx:endOldTgt] 
                            
                        """
                        ###############################                        
                        #If there is no overlap between the src and tgt then, we are done 
                        if self.noOverlap(extrSrc, extrTgt):# and self.filterSrcTgtOnlyMets(extrSrc, extrTgt, extr[0]):
                            mFlag = True
                            break
                        # if source and target are the same LUs, skip
                        else:
                            if (len(extr[1]) - ys) > (len(extr[2]) - yt):
                                ys += 1
                            else:
                                yt += 1
                            continue
                                                        
                # if we have both src and tgt segments and it's not a repetitive segment, insert it into the json 
                if mFlag and extr[0] not in metSegList and (extrSrc, extrTgt) not in srcTgtTupList:
                    self.logger.debug("seg:" + extr[0]) 
                    self.logger.debug("src:" + extrSrc)
                    self.logger.debug("tgt:" + extrTgt)  
                    #out.write("seg:" + extr[0] + "\n")
                    #out.write("src:" + extrSrc + "\n")
                    #out.write("tgt:" + extrTgt + "\n")
                    # keep track of metaphoric segments
                    metSegList.append(extr[0])
                    srcTgtTupList.append((extrSrc, extrTgt))
                
                    srcElem = self.prepElement(extrSrc, sen, self.lemHash, True)
                    lmsDict["source"] = srcElem
                
                    tgtElem = self.prepElement(extrTgt, sen, self.lemHash, False)
                    lmsDict["target"] = tgtElem                                                            
                    lmsList.append(lmsDict)
        return lmsList

    ################################################################################################
                                
    def processASentence4Met(self, txt, senCt, pTree):

        mFlag = False        
        # if reading parse tree from json, then can't do any further preprocessing
        # sticking to what the parse tree is providing
        if pTree:
            sen = txt            
        else:
            self.logger.warning("No parse tree from JSON")
            s = self.perPipeline.preprocess(txt)
            ts = self.perPipeline.posTagASentence(s)
            if not ts:
                self.logger.warning("Error in POS tagging")
                return []
            # attaching the compound verbs with a ^ sign
            attS = self.perPipeline.attachPerCompounds(ts)
        
            # get the first element of pos tuples and join them to form the sentence
            # replace the ^ sign (from compound attaching) with space
            sen = " ".join(map(lambda x: x[0].replace("^"," "), attS))


        self.logger.warning("Sent " + str(senCt))
        self.logger.debug(sen)
        
        # call the extract method to find a list of metaphoric expressions  
        # returns empty list if nothing found
        srcExtList = segExtractor.findLUsInSent(sen, self.srcHash)
        tgtExtList = segExtractor.findLUsInSent(sen, self.tgtHash)
        
        metList = [srcExtList, tgtExtList]
        
        # metaphor list for this sentence            
        lmsList = []
        # if there is source and target terms and they do not overlap, then parse the sentence    
        if srcExtList and tgtExtList and ((len(srcExtList) != len(tgtExtList)) or (self.noOverlap(srcExtList[0],tgtExtList[0]))):
                        
            # parse the sentence with the compound verbs attached to each other

            if pTree:
                parsedLine = pTree
                self.logger.warning("Read the parse Tree from JSON")
            else:
                parsedLine = self.perPipeline.parseATaggedSentence(attS)
                if not parsedLine:
                    self.logger.warning("Error in parsing")
                    return []
                self.logger.info("pos and parsing went fine!")
            
            # get a list of extracts for different constructions (moz, tosifi, etc) along with the list of src and target segments for each 
            # extracted metaphor
            extracts = segExtractor.locateMetSeg(parsedLine, self.srcHash, self.tgtHash)
            
            # among various extracts pick the one            
            lmsList = self.selectTheLMsBoundary(extracts, sen)    
            numLMs = len(lmsList)
            
            self.logger.info("Done with extraction of " + str(numLMs) + " LMs")
        else:
            self.logger.info("No LU match! Skipping the sentence!")
                        
        return lmsList        


    ##########################################################################################
    
    def processASentence4Met2(self, txt, senCt, pTree):
        mFlag = False
        
        s = self.perPipeline.preprocess(txt)
        ts = self.perPipeline.posTagASentence(s)
        if not ts:
            self.logger.warning("Error in POS tagging")
            return []
        # attaching the compound verbs with a ^ sign
        attS = self.perPipeline.attachPerCompounds(ts)
        
        # get the first element of pos tuples and join them to form the sentence
        # replace the ^ sign (from compound attaching) with space
        sen = " ".join(map(lambda x: x[0].replace("^"," "), attS))        
                
        self.logger.warning("Sent " + str(senCt))
        self.logger.debug(sen)
        
        # call the extract method to find a list of metaphoric expressions  
        # returns empty list if nothing found
        srcExtList = segExtractor.findLUsInSent(sen, self.srcHash)
        tgtExtList = segExtractor.findLUsInSent(sen, self.tgtHash)
        
        metList = [srcExtList, tgtExtList]
        
        # metaphor list for this sentence            
        lmsList = []
        # if there is source and target terms and they do not overlap, then parse the sentence    
        if srcExtList and tgtExtList and ((len(srcExtList) != len(tgtExtList)) or (self.noOverlap(srcExtList[0],tgtExtList[0]))):
            
            
            # parse the sentence with the compound verbs attached to each other

            if pTree:
                parsedLine = pTree
                self.logger.warning("Read the parse Tree from JSON")
            else:
                parsedLine = self.perPipeline.parseATaggedSentence(attS)
                if not parsedLine:
                    self.logger.warning("Error in parsing")
                    return []
                self.logger.info("pos and parsing went fine!")
            
            # get a list of extracts for different constructions (moz, tosifi, etc) along with the list of src and target segments for each 
            # extracted metaphor
            extracts = segExtractor.locateMetSeg(parsedLine, self.srcHash, self.tgtHash)
                         
            # this lists keeps tracks of extracted metaphoric segments that we avoid repetitions
            metSegList =  []
            srcTgtTupList = []
            for exSet in extracts:
                
                #print "size of exSet:", len(exSet)
                k = -1
                for extr in exSet:
                    mFlag = False
                    extrSrc = extrTgt = ""
                    lmsDict = {}                    
                    k += 1
                    if extr != []:                        
                        lmsDict["name"] = extr[0]
                        lmsDict["seed"] = u'NA'
                        lmsDict["extractor"] = u'LMS2'
                        lmsDict["score"] = 0.5
                        ys = 0
                        yt = 0
                        
                        # look for the match, skip the source of target LU matches if they're stop word.                    
                        while (ys < len(extr[1])) and (yt < len(extr[2])):
                            #ys += 1
                            #yt += 1
                            extrSrc = extr[1][ys]
                            extrTgt = extr[2][yt]
                            
                            
                            if extrSrc in self.stopList:
                                ys += 1
                                continue
                            if extrTgt in self.stopList:
                                yt += 1
                                continue
                            
                            ###############################
                            # this was an effort to extend the boundary of source or target beyond the 1-2 tokens.  
                            # but experiments proved that the original code was better and more accurate.
                            """
                            tgtInx = extr[0].find(extrTgt)
                            srcInx = extr[0].find(extrSrc) 
                                                        
                            if tgtInx > srcInx:
                                #extrSrc = extr[0][srcInx:tgtInx]
                                newTgtInx = srcInx + len(extrSrc) + 1
                                endOldTgt = tgtInx + len(extrTgt)
                                extrTgt = extr[0][newTgtInx:endOldTgt] 
                                
                            """
                            
                            
                            ###############################
                            
                            #If there is no overlap between the src and tgt then, we are done 
                            if self.noOverlap(extrSrc, extrTgt):# and self.filterSrcTgtOnlyMets(extrSrc, extrTgt, extr[0]):
                                mFlag = True
                                break
                            # if source and target are the same LUs, skip
                            else:
                                if (len(extr[1]) - ys) > (len(extr[2]) - yt):
                                    ys += 1
                                else:
                                    yt += 1
                                continue
                                                            
                    # if we have both src and tgt segments and it's not a repetitive segment, insert it into the json
                    #out.write("out of for with k=" + str(k) + "\n")   
                    if mFlag and extr[0] not in metSegList and (extrSrc, extrTgt) not in srcTgtTupList:
                        self.logger.debug("seg:" + extr[0]) 
                        self.logger.debug("src:" + extrSrc)
                        self.logger.debug("tgt:" + extrTgt)  
                        #out.write("seg:" + extr[0] + "\n")
                        #out.write("src:" + extrSrc + "\n")
                        #out.write("tgt:" + extrTgt + "\n")
                        # keep track of metaphoric segments
                        metSegList.append(extr[0])
                        srcTgtTupList.append((extrSrc, extrTgt))
                    
                        srcElem = self.prepElement(extrSrc, sen, self.lemHash, True)
                        lmsDict["source"] = srcElem
                    
                        tgtElem = self.prepElement(extrTgt, sen, self.lemHash, False)
                        lmsDict["target"] = tgtElem                                                            
                        lmsList.append(lmsDict)
            
            numLMs = len(lmsList)
            
            self.logger.info("Done with extraction of " + str(numLMs) + " LMs")
        else:
            self.logger.info("No LU match! Skipping the sentence!")
                        
        return lmsList        

    ##########################################################################################  
 
    def parse(self, jObj):
        self.logger.info("calling the empty parse")
        return ""
    
    ##########################################################
    def reconsParseTreeFromJson(self, parseList):
        numWds = len(parseList)
        # parse word dictionary
        parseTree = ""
        posSent = []
        sent = ""
        for pWD in parseList:
            num = pWD["n"]
            parseTree += (str(num) + "\t")
            wd = pWD["form"]
            sent += (wd + " ") 
            parseTree += (wd + "\t_\t") 
            pos = pWD["pos"]
            parseTree += (pos + "\t" + pos + "\t_\t")
            posSent.append((wd, pos))
            #dependecny dict
            depD = pWD["dep"]
            head = depD["head"]
            parseTree += (str(head) + "\t")
            role = depD["type"]
            parseTree += (role + "\t_\t_\n")
        sent = sent.strip()
        return (sent, parseTree)
        #self.logger.warning(sent + "\n")
        #self.logger.warning("parse: " + parseTree)
            
            
    ##########################################################                
    def find_LMs(self, jObj):
        """
        A higher level method that reads in a json object (containing 
        a set of sentences, preprocesses, parses and extract metaphoric segments
        and write the results into a new a json object which will be returned 
        
        :param jObj: MetaNet JSON format structure
        :type jObj: dict
        :returns: MetaNet JSON format structure
        """
        
        """
        # The entire file logging is skipped for now and we only use the Python logger
        randStr = str(random.randint(100000, 500000))
        #randStr = "1"
        
        out = codecs.open(self.repDir+ "blog_" + randStr + ".txt","w", "utf-8")
        lmsg = "The LOG File is at", self.repDir+ "blog_" + randStr + ".txt"
        self.logger.info(lmsg)
        """
        sents = jObj['sentences']
        # for all sentences, call the extracor to get metaphoric segments.
        # create an LM list and add each segment under the "name" field.
        sentCt = -1
        mFlag = False
        lmsList = []
        for snt in sents:
            sentCt += 1 
            parseTree = ""
            sntText = snt["text"]
            # get the word list along with the parse information from the json
            if ("parseword" in snt):
                sntParseList = snt["parseword"]
                (sent, parseTree) = self.reconsParseTreeFromJson(sntParseList)
                if sent and parseTree:
                    sntText = sent
                    
            # skip the very long sentences
            if len(sntText.split()) > 128:
                self.logger.warning("skipping the long sentenece" + str(sentCt))
                continue
                                          
            lmsList = self.processASentence4Met(sntText, sentCt, parseTree)                                 
            if len(lmsList) > 0:
                #print "adding a list of ", len(lmsList), "LMs to the jobj"
                snt["lms"] = lmsList
                
            else:
                pass
                         
        return jObj
    ##########################################################
    def findLMs4RawText(self, inputPath):
        """
        A higher level method that reads in a json object (containing 
        a set of sentences, preprocesses, parses and extract metaphoric segments
        and write the results into a new a json object which will be returned 
        
        :param jObj: MetaNet JSON format structure
        :type jObj: dict
        :returns: MetaNet JSON format structure
        """
        lmList = []
        randStr = str(random.randint(0, 100000))
        randStr = "1"
        out = codecs.open(self.repDir+ "blog_" + randStr + ".txt","w", "utf-8")
        fle = codecs.open(inputPath, "r", "utf-8")
        sents = fle.read().split("\n") 
        # for all sentences, call the extracor to get metaphoric segments.
        # create an LM list and add each segment under the "name" field.
        sentCt = -1
        mFlag = False
        for snt in sents:
            sentCt += 1
            # calling with an empty parse tree and empty pos list                               
            lmsList = self.processASentence4Met(snt, sentCt,"")                                 
            if len(lmsList) > 0:
                print "adding a list of ", len(lmsList), "LMs to the jobj"
                
            else:
                print "--- A sentence with no metaphor"            
        return lmList
    
    ##########################################################    
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

    FORMAT = '%(asctime)-15s - %(message)s'
    DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
    logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT,level=logging.INFO)
    

    rDir = '/u/metanet/persianCode/beh/code/sysOct2014/'
    pext = PersianMetaphorExtractor(rDir)
    
    jObj = None
    filePath = sys.argv[1]
    fileName = filePath
    if filePath.find("/") > -1:
        fileName = filePath.split("/")[-1]
    if filePath.endswith(".json"):
        jObj = json.load(file(filePath), encoding='utf-8')
        jObj = pext.find_LMs(jObj)
        pext.writejson(jObj,rDir + "/lms2." + fileName)
    # it's raw text file, no json
    else:
       lmsL = pext.findLMs4RawText(filePath) 
       
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

