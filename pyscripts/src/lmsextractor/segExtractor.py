# -*- coding: utf-8 -*-
"""
.. module:: segExtractor
    :platform: Unix
    :synopsis: metaphor segment extractor for Persian LMS system

Extracts metaphor segments from sentences using precomputed language model data.

"""
import codecs
import os
import sys
from finalTagger import hmm_tagger
from persiantagger import PersianPOSTagger
import random
# readinLM
def readLM(lmPath):
    """
    Read a language model into a dictionary.
    """
    lmFile = codecs.open(lmPath)
    lmHash = {}
    while 1:
        lmLine = lmFile.readline()
        if not lmLine or lmLine.strip() == "":
            break
        tokList = lmLine.split("\t")

        try:
            prob = float(tokList[0])
        except:
            print lmLine
            print tokList
        #print prob
        ngr = tokList[1] 

        lmHash[ngr.strip()] = prob
    return lmHash

###################################################
def readInLex(lexPath):
    """
    Loads a lexicon into a dictionary and returns the dictionary
    """
    lexFile = open(lexPath)
    lexHash = {}
    while 1:
        lex = lexFile.readline()
        if not lex:
            break
        lex = lex.strip()
        if lex not in lexHash:
            lexHash[lex] = 1
    return lexHash
#########################################
def analyzeMozafs(posSent, srcHash, tgtHash, mozList):
    """
    Reads in a pos tagged sentence, the source and target lexicons 
    (dictionaries) and the list of extracted ezaafeh constructions 
    (extracted from the sentences.  The method analyzes the ezaafeh construct
    using the source and target lexicons and decides if the construct 
    is potentially metaphoric.
    """
    [wd,pos] = [prevWd,prevPos] = ["",""]

    srcList = []
    tgtList = []
    for moz in mozList:
        #print moz
        tokMoz = moz.split()
        srcWds = []
        tgtWds = []
        # bigram moz in which there is a tgt word, just take them
        if len(tokMoz) == 2 and tokMoz[1] in tgtHash:
            
            #print "bigram moz", moz
            #if tokMoz[1] in ["ثروت", "فقر", "مالیات", "مالیاتها", "مالیاتهای", "ثروتها", "ثروتهای"]:
            #    print "UUUUUUUUUUUUUUUUUUUUpdating lexicon", tokMoz[0], "--", moz
            #    srcHash[tokMoz[0]] = 1
            srcList.append(tokMoz[0])
            tgtList.append(tokMoz[1])
            continue

        # revisit
        for tok in tokMoz:
            # if not seen a target word and see a source word
            if not tgtWds and tok in srcHash:
                srcWds.append(tok)
            # if seen a source word and now see a target word
            if srcWds and tok in tgtHash:
                tgtWds.append(tok)
        # if seen both target and source words
        if srcWds and tgtWds:
            tgtList.extend(tgtWds)
            srcList.extend(srcWds)
        # buggy
        # elif srcWds:
        #    srcList.append(moz)
        #elif tgtWds:
        #    tgtList.append(moz)
    # there is something in both lists
    if srcList and tgtList:
        return [srcList, tgtList]
    return None
####################################################################


def analyzeTrigrams(posSent,uniHash,biHash,triHash, srcHash, tgtHash):
    """
    Reads in a pos tagged sentence, the source and target lexicons 
    (dictionaries) and the dictionaries associated with the language model.  
    The method uses the language model to extract potentially metaphoric trigrams
    """
    focusPOS = ["N", "ADJ"]

    [wd,pos] = [prevWd,prevPos] = ["",""]
    srcWd = tgtWd = ""
    srcTrigr = tgtTrigr = ""
    srcList = []
    tgtList = []
    for tup in posSent:
        tup = tup.encode("utf-8")
        [pprevWd, pprevPos]=[prevWd, prevPos] 
        [prevWd, prevPos]= [wd,pos]
        try:
            [wd, pos] = tup.split("/")
        except ValueError:
            pass
        
        trigram = (pprevWd + " " + prevWd + " " + wd).strip()
        
        if (pprevWd == "") or (prevWd == "") or (pos not in focusPOS) or (prevPos not in focusPOS) or (pprevPos not in focusPOS) or (wd not in uniHash) or (prevWd not in uniHash) or (pprevWd not in uniHash):
            continue

        if (trigram not in triHash) or triHash[trigram] < -0.3:
            # if the context is not familiar, skip this trigram
            tmpBigr = pprevWd + " " + prevWd
            if tmpBigr not in biHash:
                continue

            if (wd in srcHash) or (prevWd in srcHash) or (pprevWd in srcHash):
                
                for w in [pprevWd,prevWd,wd]:
                    if w in srcHash:
                        srcWd = w
                        srcTrigr = trigram
                        
                    # if there is a target word in the trigram, then undo
                    if w in tgtHash:
                        srcWd = ""
                        srcTrigr = ""
                        break
                if srcTrigr:
                    srcList.append(srcTrigr)
            if (wd in tgtHash) or (prevWd in tgtHash) or (pprevWd in tgtHash):
                for w in [pprevWd,prevWd,wd]:
                    if w in tgtHash:
                        tgtWd = w
                        tgtTrigr = trigram
                    # if there is a target word in the trigram, then undo
                    if w in srcHash:
                        tgtWd = ""
                        tgtTrigr = ""
                        break
                if tgtTrigr:
                    tgtList.append(tgtTrigr)
    if srcWd or tgtWd:
        return [srcList, tgtList]
    return None
#########################################

def analyzeBigrams(posSent,uniHash,biHash,srcHash, tgtHash):
    """
    Reads in a pos tagged sentence, the source and target lexicons 
    (dictionaries) and the dictionaries associated with the language model.  
    The method uses the language model to extract potentially metaphoric bigrams
    """
    focusPOS = ["N", "ADJ"]

    [wd,pos] = ["",""]
    srcWd = tgtWd = ""
    srcBigr = tgtBigr = ""
    srcList = []
    tgtList = []
    for tup in posSent:
        tup = tup.encode("utf-8")
        [prevWd, prevPos] = [wd,pos]
        try:
            [wd, pos] = tup.split("/")
        except ValueError:
            pass
        bigram = (prevWd + " " + wd).strip()
        if (prevWd == "") or (pos not in focusPOS) or (prevPos not in focusPOS) or (wd not in uniHash) or (prevWd not in uniHash) or (bigram.replace(" ","") in uniHash):
            continue
        
        if (bigram not in biHash) or biHash[bigram] < -0.3:
            if (wd in srcHash) or (prevWd in srcHash):
                for w in [prevWd,wd]:
                    if w in srcHash:
                        srcWd = w
                        srcBigr = bigram
                    # if there is a target word in the trigram, then undo
                    if w in tgtHash:
                        srcWd = ""
                        srcBigr = ""
                        break
                if srcWd:
                    srcList.append(srcBigr)

            if (wd in tgtHash) or (prevWd in tgtHash):
                for w in [prevWd,wd]:
                    if w in tgtHash:
                        tgtWd = w
                        tgtBigr = bigram
                    # if there is a target word in the trigram, then undo
                    if w in srcHash:
                        tgtWd = ""
                        tgtBigr = ""
                        break
                if tgtWd:
                    tgtList.append(tgtBigr)

    if srcWd or tgtWd:
        return [srcList,tgtList]
    return None
#########################################
def analyzeUnigrams(posSent,uniHash, srcHash, tgtHash):
    """
    Reads in a pos tagged sentence, the source and target lexicons 
    (dictionaries) and the dictionaries associated with the language model.  
    The method uses the language model to extract potentially metaphoric 
    unigrams.
    """
    focusPOS = ["N", "ADJ"]
    [wd,pos] = ["",""]
    srcWd = tgtWd = ""
    srcList = []
    tgtList = []
    for tup in posSent:
        tup = tup.encode("utf-8").strip()
        try:
            [wd, pos] = tup.split("/")
        except ValueError:
            pass

        if (pos not in focusPOS) or (wd not in uniHash):
            continue
        if True:
            if (wd in srcHash):
                
                srcWd = wd
                srcList.append(srcWd)
            if (wd in tgtHash):
                tgtWd = wd
                tgtList.append(tgtWd)

    if srcWd or tgtWd:
        return [srcList, tgtList]
    return None

##############################################
def tokenize(perSent):
    """
    Preprocesses a sentence and calls an external Persian tokenizer.
    Returns the a tokenized form of the input sentence. 
    """
    owd = os.getcwd()
    temppath = '/scratch/tmp/metaextracttemp'
    if not os.path.isdir(temppath):
        os.makedirs(temppath)
    randStr = str(random.randint(0, 100000000))
    tempIN= temppath + "/IN" + randStr + ".txt"
    tempOUT = temppath + "/OUT"+ randStr + ".txt"
    tmpFile = codecs.open(tempIN,"w","utf-8")
    tmpFile.write(perSent)
    tmpFile.close()
    os.system("/u/metanet/extraction/persian/tokenizer-per.sed " + tempIN + " > " + tempOUT)
    tmpFile = codecs.open(tempOUT,'r','utf-8')
    tokSent = tmpFile.readline().strip()
    tmpFile.close()
    os.remove(tempIN)
    os.remove(tempOUT)
    return tokSent

##############################################        
def extract(rawSent,unigrHash, bigrHash, trigrHash, srcLex, tgtLex, repDir, fp1, fp2, mozList):
    """
    A higher level function that reads in a sentence and various dicitonaries
    related to the language model and different lexicons and extracts 
    metaphoric segments and return them as a list.
    """
    extSrcList = []
    extTgtList = []
    ct = -1
    persianPOSTagger = PersianPOSTagger()

    # call the external tokenizer
    try:
        perSent = persianPOSTagger.cleanText(rawSent)
    except:
        #print "problem with tokenizing the following sentence"
        #print rawSent
        perSent = rawSent
    try:
        posSent = persianPOSTagger.run_hmm_tagger(perSent)        
    except:
        print "problem pos tagging the following sentence which will be skipped"
        print rawSent
        return []

    srcFlag = tgtFlag = False
    retMoz = []
    if mozList:
        retMoz = analyzeMozafs(posSent, srcLex, tgtLex, mozList)
        if retMoz:
            extSrcList.extend(retMoz[0])
            extTgtList.extend(retMoz[1])
            if extSrcList and extTgtList:                
                #print "SRC MOZ"
                #for t in retMoz[0]:
                #    print t
                #print "TGT MOZ"
                #for t in retMoz[1]:
                #    print t
                #for t in extSrcList:
                #    print "sss", t
                #for t in extTgtList:
                #    print "ttt", t                
                return [extSrcList, extTgtList]

    ret3 = analyzeTrigrams(posSent,unigrHash,bigrHash,trigrHash, srcLex, tgtLex)
    ret2 = analyzeBigrams(posSent,unigrHash, bigrHash,srcLex, tgtLex)
    ret1 = analyzeUnigrams(posSent,unigrHash, srcLex, tgtLex)    
            

    if ret3:
        extSrcList.extend(ret3[0])
        extTgtList.extend(ret3[1])

        
    if ret2:
        extSrcList.extend(ret2[0])
        extTgtList.extend(ret2[1])    

    if ret1:
        extSrcList.extend(ret1[0])
        extTgtList.extend(ret1[1])
    if extSrcList and extTgtList:
        #print "^^^^^^^ NO MOZ Extract ++++++++++++"
        return [extSrcList, extTgtList]
    
    else:
        #print "^^^^^^^ NO MOZ Extract -----------"
        return []
###################################################
def combineSrcTgt(src, tgt, sent):
    sent =sent.encode("utf-8")
    srcInx = sent.find(src)
    tgtInx = sent.find(tgt)
    start = min(srcInx, tgtInx)
    end = 0
    if srcInx < tgtInx:
        # if target is not very far from source, the get the maximum span      
        if tgtInx < (srcInx + len(src) +5):
            end = tgtInx + len(tgt)
            #print "@@@@@@", sent[start:end]
            return sent[start:(end)].decode('utf-8')
    
    else:
        if srcInx < (tgtInx + len(tgt) + 5):
            end = srcInx + len(src)
            return sent[start:end].decode('utf-8')

    return None

###################################################
def main():
    repDir = sys.argv[2]

    # for the pos tagger
    #fpOne = codecs.open(repDir + '/bigramProb.txt','r','utf-8').read()
    #fpTwo = codecs.open(repDir + '/lexProb.txt','r','utf-8').read()        

    trigrHash = readLM(repDir + "/cleanTextCorp-UPEC-PerTB.trigram")
    bigrHash = readLM(repDir + "/cleanTextCorp-UPEC-PerTB.bigrams")
    unigrHash = readLM(repDir + "/cleanTextCorp-UPEC-PerTB.unigrams.sortCleaned")
    tgtHash = readInLex(repDir + "/tgtLexExt2.txt")
    srcHash = readInLex(repDir + "/srcLexExt2.txt")
    inFile = codecs.open(sys.argv[1],"r",'utf-8')

    while 1:
        sent = inFile.readline()
        
        if not sent or sent.strip() == "":
            break
        sent = sent.strip()
        ret = extract(sent, unigrHash, bigrHash, trigrHash, srcHash, tgtHash, repDir,fpOne, fpTwo)
        
        if ret:

            for extrSrc in ret[0]:

                for extrTgt in ret[1]:

                    combLM = combineSrcTgt(extrSrc, extrTgt, sent)
                    if not combLM:
                        continue
                    print sent
                    print "metaphore:", combLM
                    print "src:", extrSrc
                    print "tgt:", extrTgt

if __name__ == "__main__":
    main()
