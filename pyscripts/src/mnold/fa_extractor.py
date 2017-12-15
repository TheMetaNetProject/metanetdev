#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import codecs
import os

#
# This script combines externalExtr.py and segExtractor.py into
# a single script.
#

# the script reads in a json file, calls the extractor and generates a new
# json file (with a 'processed.' prefix and adds the extracted LMs to
# the output file.
#     python externalExtr.py inputJsonFile (old)

ECONMETFILE = "/u/metanet/extraction/persian/EconMetLex.txt"

def main():
    global ECONMETFILE
    if len(sys.argv) == 1:
        print "use the following:"
        print "python externalExtr.py input-json-file"
        print "   e.g. \"python externalExtr.py TestInput-fa.json\""
        sys.exit() 
    jsFile = codecs.open(sys.argv[1],'r', 'utf-8')
    jsOut = codecs.open("processed."+os.path.basename(sys.argv[1]),'w','utf-8')
    jsStr = jsFile.read()

    jObj = json.loads(jsStr)

    sents = jObj['sentences']
    # for all sentences, call the extracor to get metaphoric segments.
    # create an LM list and add each segment under the "name" field.
    for snt in sents:
        txt = snt["text"]

        # call the extract method to find a list of metaphoric expressions  
        # returns empty list if nothing found
        metList = extract(ECONMETFILE, txt)

        lmsList = []
        for metSeg in metList:
            lmsDict = {}
            lmsDict["name"] = metSeg
            lmsList.append(lmsDict)
        # if there is any metaphoric segment, then add it to the snt
        if len(lmsList) > 0:
            snt["lms"] = lmsList
    jsFile.close()

    # package and write
    jsDump =json.dumps(jObj,indent=2,sort_keys=True,ensure_ascii=False)
    jsOut.write(jsDump)
    jsOut.close()
    return 0

# read the econ inequality lexicon
def readLexicon(lexFile):
    lexList = []
    lexHash = {}
    while 1:
        lex = lexFile.readline()
        if not lex:
            break
        lex = lex.strip() 
        lexList.append(lex)
        lexHash[lex] = 0
    lexFile.close()
    return lexHash


def extract(perLexPath, perSent):

    perLexFile = codecs.open(perLexPath,"r", "utf-8")
    lexHash = readLexicon(perLexFile)
    lexList = lexHash.keys()
    ct = -1
    if 1:
        ct += 1
        flag = False

        lineList = perSent.strip().split()
        for lex in lexList:
            if lex in lineList:
                lexHash[lex] += 1
                if flag:
                    return [firstLex, lex]
                    break

                # first lexeme is observed
                flag = True
                firstLex = lex
        return []


if __name__ == "__main__":
    status = main()
    sys.exit(status)
