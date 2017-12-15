"""
.. module: affectlookup
    :platform: Unix
    :synopsis: Compute affect values for LMs
    
Look up affect values for the two terms, return a value for the metaphor as a whole.
By default, affect ratings are loaded from the following path:

``/u/metanet/affectRatings``

This path can be overridden by setting the ``MNAFFECTDIR`` environment variable.
Created on Sep 28, 2013

.. moduleauthor:: Collin Baker <collinb@icsi.berkeley.edu>, Jisup Hong <jhong@icsi.berkeley.edu>

"""
#!/usr/bin/env python
# -*- coding=utf-8 -*-
import sys, os, codecs, logging
import argparse
import re
import json

# default directory containing affectRatings
AFFDIR = '/u/metanet/affectRatings'

class AffectLookup:
    """
    This class ensures that the lookup tables are loaded from the file
    once per language, so that each word lookup is done in memory.
    """
    sourceRatings = {}
    targetRatings = {}
    langs = ['en','es','fa','ru']
    defaff = 0
    
    def __init__(self,lang,affdir=None):
        global AFFDIR
        if affdir == None:
            if 'MNAFFECTDIR' in os.environ:
                affdir = os.environ['MNAFFECTDIR']
            else:
                affdir = AFFDIR
        self.logger = logging.getLogger(__name__)
        self.sourceRatings = {}
        self.targetRatings = {}
        self.intensifiers = {}
        self.verbose = False
        self.useIntensifiers = False
        self.maxAff = 5
        self.minAff = -5
        self.lang = lang
        if lang == "en":
            from nltk.stem.wordnet import WordNetLemmatizer
            self.WNL = WordNetLemmatizer()

        SaffectsName = '%s/%s-sourceAffectRatings_clean.txt'%(affdir,lang.upper())  #assume that the files are in the affdir directory
        TaffectsName = '%s/%s-targetAffectRatings_clean.txt'%(affdir,lang.upper())
        IntensifiersName = '%s/%s-intensifiers.txt'%(affdir,lang.upper())
        if os.path.exists(SaffectsName):
            SaffFile = codecs.open(SaffectsName,'r',encoding='utf-8')
            for line in SaffFile:
                if line.startswith('#'):
                    continue
                try:
                    (word, affVal) = line.rstrip().split('\t')
#                    word = str(word)
#                    affVal = int(str(affVal))
                except ValueError,e:
                    if self.verbose:
                        print >> sys.stderr, e, line
                    continue
                self.sourceRatings[word] = affVal
        else:
            self.logger.error("Saffect file %s doesn't exist", SaffectsName)
            raise IOError
        if os.path.exists(TaffectsName):
            TaffFile = codecs.open(TaffectsName,'r',encoding='utf-8')
            for line in TaffFile:
                try:
                    (word, affVal) = line.rstrip().split('\t')
                except ValueError, e:                    
                    if self.verbose:
                        print >> sys.stderr, e, line
                    continue
#                affVal = int(affVal)
                self.targetRatings[word] = affVal
        else:
            self.logger.error("Taffect file % doesn't exist",TaffectsName)
            raise IOError
        if os.path.exists(IntensifiersName):
            self.useIntensifiers = True
            IntensifiersFile = codecs.open(IntensifiersName,'r',encoding='utf-8')
            for line in IntensifiersFile:
                try:
                    (word, multiplier) = line.rstrip().split('\t')
                except ValueError, e:
                    if self.verbose:
                        print >> sys.stderr, e, line
                    continue
                self.intensifiers[word] = multiplier
        else:
            if lang == 'ru':
                self.logger.info("Intensifiers file %s doesn't exist",IntensifiersName)
            else:
                self.logger.error("Intensifiers file %s doesn't exist",IntensifiersName)
                raise IOError

    def getSourceAffect(self,word):
          if word in self.sourceRatings:
              return self.sourceRatings[word]
          else:
              if self.verbose:
                  print "Source term affect value not found. Returning 999"
              return 999

    def getTargetAffect(self,word):
        if word in self.targetRatings:
            return self.targetRatings[word]
        else:
            if self.verbose:
                print "Target term affect value not found. Returning 999"
            return 999

    def miniMorph(self,lang, term):
        if lang == "en":
            term = re.sub("'s",'',term) # WN lemmatizer doesn't handle apostrophe-s
            term = self.WNL.lemmatize(term)
        return term

    def getLMAffect(self,target,source):
        if self.lang == "en":  # cleanup only for English at the moment
            if self.verbose:
                print "morph1: target: {}, source: {}".format(target, source)
            source = self.miniMorph(self.lang, source)
            target = self.miniMorph(self.lang, target)
            if self.verbose:
                print "morph2: target: {}, source: {}".format(target, source)
        taff = self.getTargetAffect(target)
        saff = self.getSourceAffect(source)
        if taff == 999:  # handle unknown words
            if saff == 999:
                return int(999)
            else:
                return int(saff)
        else:
            if saff == 999:
                return int(taff)
        # (else) we have  values for both
        outVal = round(int(taff) + int(saff))
        if self.useIntensifiers:
            if source in self.intensifiers.keys():
                multiplier = float(self.intensifiers[source])
                outVal = outVal * multiplier
            else:
                multiplier = None
        if outVal > self.maxAff: # trim to predefined range
            outVal = self.maxAff
        elif outVal < self.minAff:
            outVal = self.minAff
        return int(outVal)

    def getLMAffectIARPA(self,target,source):
        aff = self.getLMAffect(target, source)
        if aff == 999:
            return("XXX", 999)
        if aff == 0:
            polarity = 'NEUTRAL'
            intensity = 1
        elif aff > 0:
            polarity = 'POSITIVE'
        else: # assert: aff < 0:
            polarity = 'NEGATIVE'
        intensity = abs(aff)
        return (polarity, intensity)


def handlePair(lang,sTerm, tTerm, affectlookup):
    SaffVal = affectlookup.getSourceAffect(sTerm)
    TaffVal = affectlookup.getTargetAffect(tTerm)
    result = affectlookup.getLMAffect(tTerm, sTerm)

    sOut = codecs.encode(sTerm,'utf-8','replace')
    tOut = codecs.encode(tTerm,'utf-8','replace')
    print "LMAffect result is {}".format(result)
    result = affectlookup.getLMAffectIARPA(tTerm, sTerm)
    print "IARPA results, polarity = {}, intensity = {}\n--------------\n".format(result[0], result[1])
    print "HandlePair: lang: "+lang+", input source term: "+sOut+" ("+str(SaffVal)+"), input target term: "+tOut+" ("+str(TaffVal)+")"
#    print u"HandlePair: lang: {}, input source term: {} ({}), input target term: {} ({})".format(lang, sOut, SaffVal, tOut, TaffVal)

def main():

  logging.basicConfig()
  Bparser = argparse.ArgumentParser(description="Accepts a language abbreviation and two words as parameters \
  ; the languages must be  one of [EN, ES, RU and FA] and the words should be a word in the source domain \
  and a word in the target domain of the metaphor respectively.  Looks up the affect values of  both words and \
  returns an average. (Should perform a more reasonable calculation eventually.) ")
  Bparser.add_argument('lang', type = str,
                       help='Abbreviation for language name.')
  Bparser.add_argument('sourceTerm',  type = str, nargs="?",
                       help='Term in the source domain')
  Bparser.add_argument('targetTerm', type=str, nargs="?",
                       help='Term in the target domain')
  Bparser.add_argument("-v", "--verbose",  help="give more verbose reports", \
                       action="store_true", default = False)
  Bparser.add_argument("-t", "--textFile",  help="take input from text file rather than command line." )
  Bparser.add_argument("-j", "--jsonFile",  help="take input from JSON file rather than command line." )

  
  args = Bparser.parse_args()
  jsonFileName = ""
  textFileName = ""
  sTerm = args.sourceTerm
  tTerm = args.targetTerm
  textFileName = args.textFile
  jsonFileName = args.jsonFile

  lang = args.lang
  if not lang in AffectLookup.langs:
      print "Invalid language specification; must be one of {}.\n".format(AffectLookup.langs)
      Bparser.print_help()
      exit()
  if args.verbose:
      verbose = True
  else:
      verbose = False
  if verbose:
      print args

  affectlookup = AffectLookup(lang)
  if textFileName:
      infile = codecs.open(textFileName,'r','utf-8')
      for line in infile:
          (sTerm, tTerm) = line.strip().split("\t")
          handlePair(lang, sTerm, tTerm, affectlookup)
  elif jsonFileName:
      infile = codecs.open(jsonFileName, encoding='utf-8')
#      outfile = open(outfileName,'w')
      myObj = json.load(infile)
      for sentence in myObj['sentences']:
          for lm in sentence['lms']:
              lmSor = lm['source']
              lmTar = lm['target']
              lmSorF = lmSor['form']
              lmTarF = lmTar['form']
              handlePair(lang,lmSorF, lmTarF, affectlookup)
  elif (sTerm and tTerm):
      handlePair(lang, sTerm, tTerm, affectlookup)
  else:
      print "Wrong number of arguments; please run again with -h for help."
      
if __name__ == "__main__":
    main()

