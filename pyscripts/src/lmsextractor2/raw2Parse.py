# -*- coding: utf-8 -*-

import sys
from PersianPipeline import *
import os, codecs

        
def main():
    #sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    #sys.stdin = codecs.getreader("utf-8")(sys.stdin)
    os.environ["JAVAHOME"] = "/usr/lib/jvm/jre-1.7.0-oracle.x86_64/bin/java"
    posModPath = "/u/metanet/persianCode/PersianPipeline/models/persian-train.model"
    posJar = "/u/metanet/nlptools/stanford-postagger-full-2014-06-16/stanford-postagger.jar"
    parseModPath = "PerParseModelWithCompoundTerms"
    ppl = None
    try:
        
        # am skiping the change directory way of running the parser.  prefer to create the temp files in the current directory
        #cuDir = os.getcwd()
        #os.chdir("/u/metanet/persianCode/PersianPipeline/models/")
        parseModelSymLink = "./PerParseModelWithCompoundTerms.mco"
        
        # creating a symbolic link to the parsing model
        if not os.path.isfile(parseModelSymLink):
            os.symlink("/u/metanet/persianCode/PersianPipeline/models/PerParseModelWithCompoundTerms.mco", parseModelSymLink)
            
        # instantiating a Persian Pipeline for preprocessing, pos tagging and parsing 
        ppl = PersianPipeline(posModPath, posJar, parseModPath, "./")
    except:
        print "problem in loading the Persian Pipeline"
        exit(0)
    while True:
        s = sys.stdin.readline().strip()
        p = ""
        if not s:
            break
        # making a unicde object
        s = s.decode("utf-8")
        try:
            # calling the raw to parse method from the Persian pipleine
            p = ppl.rawtoParse(s)
        
        except:
            print "problem with processing a sentence"
            
        if p:
            sys.stdout.write(p)
            
    
if __name__ == "__main__":
    main()
    