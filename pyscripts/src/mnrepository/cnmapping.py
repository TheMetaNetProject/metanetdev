#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: cnmapping
    :platform: Unix
    :synopsis: Expression to concept mapping via the MetaNet conceptual network

Handles search for target and source frames and concepts for
Linguistic Metaphor target and source expressions using the MetaNet conceptual
network.  The system searches for frames in the network that define the
expressions, and maps frames to IARPA concepts.  When possible, and if
necessary, the system extends the lexical coverage of the MetaNet
conceptual network using WordNet, FrameNet, and Wiktionary.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
from mnanalysis.programsources import ProgramSources
from metanetrdf import MetaNetRepository
import sys, re, logging, pprint, argparse, time, setproctitle
from collections import Counter
from mnrepository.gmrdb import GMRDB

class ConceptualNetworkMapper:
    """
    Contains methods for retrieving frames using words, and concepts using frames.
    Uses :py:mod:`mnrepository.metanetrdf` for queries into the conceptual
    network.
    """
    # non-head words to filter out of spanish LMs
    filterwords = {'es': set(['a','desde','detrás','ante','en','segun','bajo','es','del','este',
                              'entre','sin','con','hacia','sobre','contra','hasta','la','el','se',
                              'los','tras','de','por','para']),
                   'en': set(),
                   'ru': set(),
                   'fa': set()}
    
    DLSRANK = 1
    DLSScore = 0.25
    DLSScoreOverride = 0.5
    
    def __init__(self,lang, cachedir=None, useSE=None, targetConceptRank=None,
                 disableFN=False, govOnly=False, expansionTypes=[], expansionScoreScale=1.0,
                 sourceMappingLimit=2,minSecondaryScore=0.1,
                 metanetrep=None,conceptMode='general'):
        """ Initialize a ConceptualNetworkMapper instance.
        :param lang: language
        :type lang: str
        :param cachedir: directory to save/load cache looks from
        :type cachedir: str
        :param useSE: flag to tell the system to use the sparql endpoint rather than rdflib
        :type useSE: str
        :param targetConceptRank: ranked list of target concepts to adjudicate overlapping words
        :type targetConceptRank: list
        :param disableFN: flag to make system ignore closest related frame LUs
        :type disableFN: bool
        :param govOnly: flag to limit mapping to GOV owned concepts only
        :type govOnly: bool
        :param expansionTypes: lexical coverage expansion types to try
        :type expansionTypes: list
        :param expansionScoreScale: scaling to apply to mapping score when expansions are used
        :type expansionScoreScale: float
        :param sourceMappingLimit: maximum number of mappings to include in answer
        :type sourceMappingLimit: int
        :param minSecondaryScore: minimum score for a secondary mapping to be included in answer
        :type minSecondaryScore: float
        :param metanetrep: MetaNet Repository instance
        :type metanetrep: :py:mod:`mnrepository.metanetrdf.MetanetRepository`
        :param conceptMode: IARPA concept mode (general or case)
        :type conceptMode: str
        """
        self.logger = logging.getLogger(__name__)
        self.lang = lang
        if metanetrep:
            self.mr = metanetrep
        else:
            self.mr = MetaNetRepository(lang,cachedir=cachedir,useSE=useSE)
            self.mr.initLookups()
        self.psdata = ProgramSources(progsourcesfile=None,cachedir=cachedir)
        self.framesubd = {}
        self.POSre = re.compile(ur'\.([A-Za-z]|adj|adv|aa)$',flags=re.U)
        self.tconRank = {}
        if targetConceptRank:
            for idx, tcon in enumerate(targetConceptRank):
                self.tconRank[tcon] = idx
        self.disableFN = disableFN
        self.govOnly = govOnly
        if self.lang != 'en':
            self.disableFN = True
        self.expansionTypes = expansionTypes
        self.expansionScoreScale = expansionScoreScale
        self.conceptMode = conceptMode
        self.sourceMappingLimit = sourceMappingLimit
        self.minSecondaryScore = minSecondaryScore

    def filterSourceConcepts(self, scons, mappingLimit=2, secondaryThreshold=0.2):
        """
        Filters a list of source concept tuples based on a cap (mappingLimit) of
        how many candidates to consider for inclusion in the output and a
        secondaryThreshold score that all but the first source concept must
        exceed in order to make the cut.  In other words, the top concept makes
        it.  For second for higher, they must be above the score threshold.
        Returns two lists, one of the filtered source concepts, and another
        which are the list of candidates.  The list of candidates is capped by
        mappingLimit.
        :param scons: list of source concept tupes (name,rank,score)
        :type scons: list
        :param mappingLimit: max number of mappings to allow
        :type mappingLimit: int
        :param secondaryThreshold: score that secondary mappings must exceed in order to be included
        :type secondaryThreshold: float
        """
        sRank = 0
        sourceconcepts = []
        for scon in scons:
            sRank += 1
            if sRank > mappingLimit:
                continue
            if (sRank == 1) or (float(scon[2]) >= secondaryThreshold):
                sourceconcepts.append(scon)
        return sourceconcepts

    def getTargetConceptFromLemma(self, tlemma,contype='general'):
        """ Given a target lemma, return the target concept.  Does not read or write to a database
        :param tlemma: target lemma
        :type tlemma: str
        :param contype: IARPA concept type (general or case)
        :type contype: str
        """
        tframes = self.mr.lookupFramesFromLU(tlemma)
        if not tframes:
            if tlemma:
                self.logger.info(u'Could not find a frame for target word: "%s"', tlemma)
            return None, None, None, None
        return self.getTargetConceptFromFrames(tframes,contype)
    
    def getTargetFrameAndConceptFromLemma(self, tlemma=None, tpos=None, lpos=None, contype='general'):
        """ Given a target lemma, return the target frame and concept.
        Does not read or write to a database.  Target lemma can be passed in together with
        POS as in lpos, or separately, as tlemma and tpos, or without pos.
        :param tlemma: target lemma
        :type tlemma: str
        :param tpos: target POS tag
        :type tpos: str
        :param lpos: target lemma.POS
        :type lpos: str
        :param contype: IARPA concept type (general or case)
        :type contype: str
        """
        tframes = set()
        if (tlemma and tpos) and (not lpos):
            lpos = self.mr.getLemPos(tlemma,tpos)
        elif lpos and (not tlemma):
            tlemma = self.mr.getLemmaFromLemPos(lpos)
        if (not tlemma) and (not lpos):
            self.logger.info(u'Target concept search on null inputs')
            return None, None, None, None
        if lpos:
            tframes = self.mr.lookupFramesFromLU(lpos)
        if (not tframes) and tlemma:
            tframes = self.mr.lookupFramesFromLU(tlemma)
        if tlemma and (not tframes) and (u' ' in tlemma):
            # check if bad mwe in spanish, due to prepositions/particles
            # being included
            twords = tlemma.split(u' ')
            filtered = []
            for w in twords:
                if w.lower() in self.filterwords[self.lang]:
                    continue
                else:
                    tframes.update(self.mr.lookupFramesFromLU(w))
            if filtered:
                tlemma = u' '.join(filtered)
        if (not tframes):
            if (not lpos) and tlemma:
                lpos = tlemma
            tcon, tcongroup = self.mr.getTargetConceptFromWhitelistLU(lpos)
            if tcon:
                return None, None, tcon, tcongroup
        if not tframes:
            if tlemma:
                self.logger.info(u'Could not find a frame for target word: "%s"', tlemma)
            return None, None, None, None
        return self.getTargetConceptFromFrames(tframes, contype)
    
    def prefixizeURIs(self, uriList):
        """ Shorten long known URIs with prefixes
        :param uriList: list of URIs
        :type uriList: list
        """
        return self.mr.prefixizeURIs(uriList)
    
    def getConceptNameFromFrameName(self, framename):
        """ Translate a frame name into an IARPA concept name. Rule based with
        exceptions that are specified.  'Social class' => 'SOCIAL_CLASS'
        :param framename: name of a frame to translate to a concept
        :type framename: str
        """
        if ':' in framename:
            # throw out the namespace prefix
            _, framename = framename.split(':',1)
        if framename=='Election':
            return 'ELECTIONS'
        return framename.upper().replace(' ','_')
    
    def getTargetConceptFromFrames(self, tframes, contype='general'):
        """ Assume that tframes are URIRefs in respective languages.  Returns a
        tuple (tframe uri, tframe name, concept name, concept group).
        :param tframes: a list of target frames (URIs)
        :type tframes: list
        :param contype: IARPA concept type (general or case)
        :type contype: str
        """
        tframe_concept = []
        for ts in tframes:
            for row in self.mr.getTargetConceptFromFrame(ts, contype):
                tframe_concept.append((ts,self.mr.deLitPy(row.framename),
                                        self.mr.deLitPy(row.conceptname),
                                        self.mr.deLitPy(row.conceptgroup)))
        if not tframe_concept:
            return None, None, None, None
        # TARGET CONCEPT: At this point: there is a tframe_concept
        # - narrow down to 1 tframe and 1 sframe concept
        # prioritize the ones in the ranked list
        priority_tconlist = []
        for tframe,tframename,conc,contype in tframe_concept:
            if conc in self.tconRank:
                priority_tconlist.append((tframe,tframename,conc,contype))
        if priority_tconlist:
            priority_tconlist.sort(key=lambda tcontuple: self.tconRank[tcontuple[2]])
            return priority_tconlist[0]
        return tframe_concept[0]

    def sconTupleToString(self,sconTuple):
        """ Convert source concept tuple to a string of the format
        name:rank:score
        :param sconTuple: types (name, rank, score)
        :type sconTuple: tuple
        """
        scon, rank, score = sconTuple
        return u'%s:%d:%.5f' % (scon,int(rank), float(score))

    def getDirectSourceConceptMatch(self, slemma):
        """ Search for source concept directly from a lemma without going through
        the conceptual network (and a frame)
        :param slemma: source lemma
        :type slemma: str
        """
        sconcepts = []
        if slemma in self.mr.lemscon:
            sconset = self.mr.lemscon[slemma]
            for scon in sconset:
                sconcepts.append(u'%s:%d:%f'%(scon,self.DLSRANK,self.DLSScore))
        return u','.join(sconcepts)
    
    def getSourceConceptsFromFrame(self, sframe, scorescale=1.0):
        """ Returns a string in descending order by score of the form
            CON:RANK:SCORE,CON:RANK:SCORE
        :param sframe: source frame (URI)
        :type sframe: str
        :param scorescale: scale with which to alter the mapping score (multiplicative)
        :type float
        """
        conceptscores = {}
        if sframe in self.mr.frameconcept:
            for con, score in self.mr.frameconcept[sframe]:
                if self.govOnly:
                    if self.mr.sconowner[con] != 'GOV':
                        continue
                conceptscores[con] = score
        conlist = sorted(conceptscores.keys(),key=lambda con: conceptscores[con],reverse=True)
        returnconlist = []
        for idx in xrange(len(conlist)):
            rank = idx + 1
            returnconlist.append(u'%s:%d:%f'%(conlist[idx],rank,conceptscores[conlist[idx]] * scorescale))
        return u','.join(returnconlist)
    
    def getSourceConceptsFromFrames(self,sframes, scorescale=1.0):
        """ Given a list of frames, return source concepts.
            Returns a string in descending order by score of the form
            CON:RANK:SCORE,CON:RANK:SCORE
        :param sframes: list of source frames (URI)
        :type sframes: list
        :param scorescale: scale with which to alter the mapping score (multiplicative)
        :type float
        """
        sconlist = []
        for frame in sframes:
            sconlist.append((frame,self.mr.getNameLiteral(frame),'unk',self.getSourceConceptsFromFrame(frame, scorescale),'CNMS'))
        return sconlist
    
    def getSourceFramesAndConceptsFromLemma(self, slemma='', spos='', lpos=''):
        """ Return a list of tuples of the form
            (frame, framename, frame lookup method, concepts, concept mapping method)
            where concepts is a string of the form CON:RANK:SCORE,...
        :param slemma: source lemma
        :type slemma: str
        :param spos: source word's POS tag
        :type spos: str
        :param lpos: source word's lemma.pos
        :type lpos: str
        """
        frameset = self.getFramesFromLemma(slemma, spos, lpos)
        sconceptslist = []
        if not frameset:
            # try looking directly for concepts
            if lpos and (not slemma):
                slemma = self.mr.getLemmaFromLemPos(lpos)
            sconcepts = self.getDirectSourceConceptMatch(slemma)
            if sconcepts:
                sconceptslist.append((None,'',None,sconcepts,'DLS'))
        else:
            for frame, framename, schmethod in frameset:
                sconceptslist.append((frame,framename,schmethod,self.getSourceConceptsFromFrame(frame),'CNMS'))
        return sconceptslist
    
    def getFramesFromLemma(self, lemma='', pos='',lpos=''):
        """ Given lemma, returns frames
        :param lemma: lemma for search for in Conceptual Network
        :type lemma: str
        :param pos: the search word's POS tag
        :type pos: str
        :param lpos: the search word's lemma.pos
        :type lpos: str
        :return: a set of frames (frame, framename, method)
        :type: set
        """
        frames = set()
        if lemma and pos and (not lpos):
            lpos = self.mr.getLemPos(lemma,pos)
        if lpos:
            method = 'wikilpos'
            frames.update([(frame, method) for frame in self.mr.lookupFramesFromLU(lpos)])
            if (not frames) and (self.disableFN==False):
                fnframes = self.mr.lookupFramesFromFNLU(lpos)
                if fnframes:
                    method = 'fnlpos'
                    frames.update([(frame, method) for frame in fnframes])
        elif lemma:
            method = 'wikilem'
            frames.update([(frame, method) for frame in self.mr.lookupFramesFromLU(lemma)])
        else:
            return frames
        if not frames and self.mr.pwf:
            if lpos and (not lemma):
                lemma = self.mr.getLemmaFromLemPos(lpos)
            allforms = self.mr.pwf.getAllForms(lemma)
            for wform in allforms:
                wfframes = self.mr.lookupFramesFromLU(wform)
                if wfframes:
                    method = 'wikipwf'
                    frames.update([(frame, method) for frame in wfframes]) 
        filtered = []
        if (not frames) and (u' ' in lemma):
            # IARPA includes phrases or even non-phrasal spans of text
            # remove non-lexical material and search for each
            method = 'wikifilt'
            words = lemma.split(u' ')
            for w in words:
                if w in self.filterwords[self.lang]:
                    continue
                else:
                    frames.update([(frame,method) for frame in self.mr.lookupFramesFromLU(w)])
                    filtered.append(w)
        if not frames and (self.disableFN==False):
            method = 'fnlem'
            frames.update([(frame,method) for frame in self.mr.lookupFramesFromFNLU(lemma)])
            if (not frames) and filtered:
                for w in filtered:
                    frames.update([(frame,method) for frame in self.mr.lookupFramesFromFNLU(w)])
        try:
            frameset = set([(frame, self.mr.getNameLiteral(frame), method) for frame, method in frames])
        except:
            self.logger.error('Error in frames: %s',pprint.pformat(frames))
            raise
        return frameset

    def getSourceFramesFromConcept(self, scon, minscore=0.1):
        """
        Given a source concept, return a list of source frames that map to that concept
        in descending order of mapping score, where mapping score cannot be below the
        specified minimum.
        :param scon: source concept tuple (name, rank, score)
        :type scon: tuple
        :param minscore: mapping score that needs to be exceeded in order to be included
        :type minscore: float
        """
        sframelist = []
        if scon in self.mr.conceptframe:
            sframelist.append(self.mr.conceptframe[scon][0])
            for sframe, score in self.mr.conceptframe[scon][1:]:
                if score > minscore:
                    sframelist.append((sframe,score))
                else:
                    break
        return sframelist
    
    def runExpansionPhases(self, phases, lemma, pos):
        """
        Runs the lexical coverage expansion phases as listed on the input word.  Returns
        expanded lists of words, and scores, based on the reliability of the relation used.
        :param phases: list of expansion phases to run
        :type phases: list
        :param lemma: lemma to expand coverage for
        :type lemma: str
        :param pos: part of speech
        :type pos: str
        """
        wdicts = []
        wscores = []
        if 'wnlem' in phases:
            self.logger.debug('\n======================= From WN:lemmas =======================')
            fromlemmas, lemscores = self.mr.getFramesViaWN(lemma, pos, "lemmas")    
            self.logger.debug(pprint.pformat(fromlemmas))
            wdicts.append(fromlemmas)
            wscores.append(lemscores)
        
        if 'wnhyper' in phases:    
            self.logger.debug('\n======================== From WN:hyper ========================')
            fromhyper, hyperscores = self.mr.getFramesViaWN(lemma, pos, "hypernyms")    
            self.logger.debug(pprint.pformat(fromhyper))
            wdicts.append(fromhyper)
            wscores.append(hyperscores)
        
        if 'wnhypo' in phases:
            self.logger.debug('\n====================== From WN:hypo ===========================')
            fromhypo, hyposcores = self.mr.getFramesViaWN(lemma, pos, "hyponyms")    
            self.logger.debug(pprint.pformat(fromhypo))
            wdicts.append(fromhypo)
            wscores.append(hyposcores)
    
        if 'wnsisters' in phases:
            self.logger.debug('\n===================== From WN:sisters =========================')
            fromsisters, sisterscores = self.mr.getFramesViaWN(lemma, pos, "sisters")    
            self.logger.debug(pprint.pformat(fromsisters))
            wdicts.append(fromsisters)
            wscores.append(sisterscores)
    
        if 'wik' in phases:
            self.logger.debug('\n===================== From Wiktionary =========================')
            fromwik, wikscores = self.mr.getFramesViaWik(lemma, pos)
            self.logger.debug(pprint.pformat(fromwik))
            wdicts.append(fromwik)
            wscores.append(wikscores)
        
        if 'fnlem' in phases:
            self.logger.debug('\n======================= From FN:lemmas ========================')
            fromfn, fnscores = self.mr.getFramesViaFN(lemma, pos, "lemmas")
            self.logger.debug(pprint.pformat(fromfn))
            wdicts.append(fromfn)
            wscores.append(fnscores)
    
        if 'fnchild' in phases:
            self.logger.debug('\n======================= From FN:child =========================')
            fromfnc, fncscores = self.mr.getFramesViaFN(lemma, pos, "Inheritance.Child")
            self.logger.debug(pprint.pformat(fromfnc))
            wdicts.append(fromfnc)
            wscores.append(fncscores)
    
        if 'fnparent' in phases:
            self.logger.debug('\n====================== From FN:parent =========================')
            fromfnp, fnpscores = self.mr.getFramesViaFN(lemma, pos, "Inheritance.Parent")
            self.logger.debug(pprint.pformat(fromfnp))
            wdicts.append(fromfnp)
            wscores.append(fnpscores)
    
        if 'fnsisters' in phases:
            self.logger.debug('\n================================ From FN:sisters =================================')
            fromfns, fnsscores = self.mr.getFramesViaFN(lemma, pos, "sisters")
            self.logger.debug(pprint.pformat(fromfns))
            wdicts.append(fromfns)
            wscores.append(fnsscores)
        return wdicts,wscores
        
    def getBestFrames(self,wdicts,wscores):
        """
        Return a counter with frames and rankings based on the input words and scores.
        :param wdicts: dictionary of words and their expansions
        :type wdicts: dict
        :param wscores: dicitonary of word expansions and their scores
        :type wscores: dict
        """
        frameranks = {}
        framewords = {}
        framemaxranks = {}
        processedlpos = set()
        for i in range(len(wdicts)):
            wdict = wdicts[i]
            sdict = wscores[i]
            for lpos, frameset in wdict.iteritems():
                if lpos in processedlpos:
                    continue
                factor = sdict[lpos]
                for frame in frameset:
                    if frame in frameranks:
                        frameranks[frame] += factor
                        framemaxranks[frame] += 1.0
                    else:
                        frameranks[frame] = factor
                        framemaxranks[frame] = 1.0
                    if frame in framewords:
                        framewords[frame].append(lpos)
                    else:
                        framewords[frame] = [lpos]
                processedlpos.add(lpos)
                
        if frameranks:
            maxframerank = max(framemaxranks.values())
            for frame in frameranks.iterkeys():
                frameranks[frame] = frameranks[frame] / maxframerank
            rc = Counter(frameranks)
        else:
            rc = Counter()
        return rc
    
    def getFramesByExpansion(self,lemma,pos,expansionTypes=[],maxRank=3):
        """ Expand lexical coverage on the lemma/pos given and return the best matching frames
        :param lemma: lemma of word
        :type lemma: str
        :param pos: POS tag of word
        :type pos: str
        :param expansionTypes: list of expansion types to run (wn, wik, fn)
        :type expansionTypes: list
        :param maxRank: how many of the top answers to report
        :type maxRank: int
        """
        phasesByType = {'wn': ['wnlem','wnhyper','wnhypo','wnsisters'],
                        'wik': ['wik'],
                        'fn': ['fnlem','fnchild','fnparent','fnsisters']}
        if not expansionTypes:
            expansionTypes = self.expansionTypes
        usedTypes = []
        framescores = {}
        for expType in expansionTypes:
            if expType not in phasesByType:
                self.logger.warning('Expansion type %s is not valid. skipping.',expType)
                continue
            wdicts,wscores = self.runExpansionPhases(phasesByType[expType],lemma,pos)
            rc = self.getBestFrames(wdicts,wscores)
            for frame, rscore in rc.iteritems():
                if frame in framescores:
                    framescores[frame].append(rscore)
                else:
                    framescores[frame] = [rscore]
            usedTypes.append(expType)
            self.logger.debug(u'output for expType %s: %s',expType,pprint.pformat(wdicts))
        self.logger.debug('scores for all frames: %s',pprint.pformat(framescores))
        for frame in framescores.iterkeys():
            val = 0.0
            for n in sorted(framescores[frame]):
                val += (1.0 - val) * n
            framescores[frame] = val
        topframes = Counter(framescores)
        method = u':'.join(usedTypes)
        return topframes.most_common(maxRank), method
    
    def getExpansionFramesAndConceptsFromLemma(self,lemma,pos,expansionTypes=[],maxRank=3,threshold=0.0,scorescale=1.0):
        """ Given a word expressed as a lemma and pos, run the given expansion types
        to extend lexical coverage of the conceptual network and return the best matching
        frames and concepts.
        :param lemma: lemma of word
        :type lemma: str
        :param pos: POS tag of word
        :type pos: str
        :param expansionTypes: list of expansion types to run (wn, wik, fn)
        :type expansionTypes: list
        :param maxRank: how many of the top answers to report
        :type maxRank: int
        :param threshold: mapping score required for reporting secondary answers
        :type threshold: float
        :param scorescale: scaling factor on answers (for penalizing answers)
        :type scorescale: float
        """
        topframes, method = self.getFramesByExpansion(lemma,pos,expansionTypes,maxRank)
        self.logger.debug('Top frames from expansion for %s.%s are %s via %s',lemma,pos,pprint.pformat(topframes),method)
        rank = 0
        sframeslist = []
        if topframes:
            for frame, score in topframes:
                rank += 1
                if rank > maxRank:
                    break
                if (rank > 1) and (score < threshold):
                    break
                
                sframeslist.append((frame,self.mr.getNameLiteral(frame),method,self.getSourceConceptsFromFrame(frame,scorescale=scorescale),'CNMS'))
        return sframeslist

    def runTargetMapping(self,lm,force=False):
        """ Run the target word to frame to concept mapping on the LM.  If a mapping is already 
        detected, the method exits, unless force is specified.
        :param lm: lm structure from the JSON
        :type lm: dict
        :param force: flag to force mapping even if one is already there in the lm
        :type force: bool
        """
        lmtarget = lm['target']
        targetmode = self.conceptMode
        if (lmtarget.get('concept') not in (None,'NONE','NULL','')) and (not force):
            return 0
        if lmtarget.get('frameuri'):
            tframe, tframename, tcon, tcgroup = self.getTargetConceptFromFrames([lmtarget['frameuri']],
                                                                                   contype=targetmode)
        else:
            lpos = lmtarget.get('lpos')
            tlemma = lmtarget.get('lemma')
            if not tlemma:
                tlemma = lmtarget.get('form')
            pos = lmtarget.get('pos')
            tframe, tframename, tcon, tcgroup = self.getTargetFrameAndConceptFromLemma(tlemma,pos,lpos,
                                                                                          contype=targetmode)
            lmtarget['frameuri'] = tframe
        lmtarget['framename'] = tframename
        if tcon:
            lmtarget['concept'] = tcon
            lmtarget['congroup'] = tcgroup
            lmtarget['cultconcept'] = tcgroup
        return 1

    def runSourceMapping(self,lm,force=False,sourceMappingLimit=None,minSecondaryScore=None,
                         expansionMaxRank=1,expansionThreshold=0.7):
        """ Run the source word to frame to concept mapping on the LM.  If a mapping is already
        detected, the method exists, unless force is specified.
        :param lm: lm structure from the JSON
        :type lm: dict
        :param force: flag to force mapping even if one is already there in the lm
        :type force: bool
        :param sourceMappingLimit: max number of mappings to return
        :type sourceMappingLimit: int
        :param minSecondaryScore: mapping score that a secondary mapping must exceed in order to be included
        :type minSecondaryScore: float
        :param expansionRank: number of answers that expanded searches are permitted to report
        :type expansionRank: int
        :param expansionThreshold: score that expanded search frame/concepts must exceed
        :type expansionThreshold: score
        """
        if not sourceMappingLimit:
            sourceMappingLimit = self.sourceMappingLimit
        if not minSecondaryScore:
            minSecondaryScore = self.minSecondaryScore
        lmsource = lm['source']
        if (lmsource.get('concept') not in (None,'NONE','NULL','')) and (not force):
            return 0
        # sanity checking
        slemma = lmsource.get('lemma')
        if not slemma:
            slemma = lmsource.get('form')
        lpos = lmsource.get('lpos')
        sconlist = self.getSourceFramesAndConceptsFromLemma(slemma, lpos=lpos)
        if (not sconlist) and self.expansionTypes and slemma and lmsource.get('pos'):
            spos = lmsource['pos']
            sconlist = self.getExpansionFramesAndConceptsFromLemma(slemma,
                                                                    spos,
                                                                    expansionTypes=self.expansionTypes,
                                                                    maxRank=expansionMaxRank,
                                                                    threshold=expansionThreshold,
                                                                    scorescale=self.expansionScoreScale)
        scon2ssconvec = {}
        allMappings = []
        for frame, framename, schmethod, scon, mapmethod in sconlist:
            ffamilies = None
            if frame:
                ffamilies = u','.join(self.mr.getFrameFamilies(frame))
            if scon:
                scontuplist = scon.split(',')
                for sconitem in scontuplist:
                    try:
                        sconname,sconrank,sconscore = sconitem.split(u':')
                    except:
                        self.logger.error('Error splitting sconitem: %s from %s',pprint.pformat(sconitem),pprint.pformat(scon))
                        raise
                    scon2ssconvec[(sconname,sconrank,sconscore)] = (frame, framename, schmethod, sconitem, mapmethod, ffamilies)
            allMappings.append({'frameuri':frame,
                                'framename':framename,
                                'concept':scon,
                                'smapmethod':mapmethod,
                                'family':ffamilies})
        scontuplist = sorted(scon2ssconvec.keys(),key=lambda scontup:scontup[2],reverse=True)
        sourceconcepts = self.filterSourceConcepts(scontuplist,
                                                   sourceMappingLimit,
                                                   minSecondaryScore)
        scontupStrings = []
        sconNameSet = set()
        for scontup in sourceconcepts:
            # make sure no duplicate scon names
            if scontup[0] in sconNameSet:
                continue
            sconNameSet.add(scontup[0])
            scontupStrings.append(self.sconTupleToString(scontup))
        lmsource['concept'] = u','.join(scontupStrings)
        lmsource['conceptraw'] = u','.join([self.sconTupleToString(scontup) for scontup in scontuplist])
        frameset = set()
        framenameset = set()
        dfamilies = set()
        filteredMappings = []
        mapmethodset = set()
        for scontup in sourceconcepts:
            frame, framename, schmethod, sconitem, mapmethod, dfamily = scon2ssconvec[scontup]
            if frame:
                frameset.add(frame)
            if framename:
                framenameset.add(framename)
            if dfamily:
                dfamilies.add(dfamily)
            if mapmethod:
                mapmethodset.add(mapmethod)
            m4score = lm.get('score')
            if m4score:
                m4score = float(m4score)
            else:
                m4score = 0.0
            if (mapmethod=='DLS') and (m4score < self.DLSScoreOverride):
                m4score = self.DLSScoreOverride
            mapScore = float(scontup[2])
            coreness = m4score * mapScore
            filteredMappings.append({'frameuri':frame,
                                     'framename':framename,
                                     'concept':sconitem,
                                     'smapmethod':mapmethod,
                                     'family':dfamily,
                                     'coreness':coreness})
        lmsource[u'frameuris'] = list(frameset)
        lmsource[u'framenames'] = list(framenameset)
        lmsource[u'framefamilies'] = list(dfamilies)
        lmsource[u'mappings'] = filteredMappings
        lmsource[u'allmappings'] = allMappings
        lmsource[u'smapmethods'] = list(mapmethodset)
        lmsource[u'smapmethod'] = u':'.join(mapmethodset)
        if 'DLS' in mapmethodset:
            if (u'score' in lm) and (float(lm[u'score']) < self.DLSScoreOverride):
                lm[u'score'] = self.DLSScoreOverride
                if lm.get(u'scorecom'):
                    lm[u'scorecom'] += u':dlso'
                else:
                    lm[u'scorecom'] = u'dlso'
        return 1
    
    def copyTargetConcept(self, totarget, frtarget, force=False):
        """ Copies target concept from frtarget to totarget.  This is used to populate
        multiple instances of the same LM.
        :param totarget: recepient target
        :type totarget: dict
        :param frtarget: giving target
        :type frtarget: dict
        :param force: flag to force the copy even if totarget already has a concept
        :type force: bool
        """
        if (totarget.get('concept') not in (None,'NONE','NULL','')) and (not force):
            return
        for field in ('concept','congroup','frameuri','framename','cultconcept'):
            if field in frtarget:
                totarget[field] = frtarget[field]
                
    def copySourceConcepts(self, tolm, fromlm, force=False):
        """ Copies source concept from frlm to tolm.  This is used to populate
        multiple instances of the same LM.
        :param tolm: recepient lm
        :type tolm: dict
        :param frlm: giving lm
        :type frlm: dict
        :param force: flag to force the copy even if tolm already has a source concept
        :type force: bool
        """
        tlmsource = tolm['source']
        if (tlmsource.get('concept') not in (None,'NONE','NULL','')) and (not force):
            return
        flmsource = fromlm['source']
        for field in ('concept','conceptraw','frameuris','framenames','framefamilies',
                      'mappings','allmappings','smapmethod'):
            if field in flmsource:
                tlmsource[field] = flmsource[field]
        if 'DLS' in tlmsource['smapmethod']:
            if (u'score' in tolm) and (float(tolm[u'score']) < self.DLSScoreOverride):
                tolm[u'score'] = self.DLSScoreOverride
                if tolm.get(u'scorecom'):
                    tolm[u'scorecom'] += u':dlso'
                else:
                    tolm[u'scorecom'] = u'dlso'
def main():
    """ for testing
    """
    datestring = time.strftime("%Y%m%d")
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="CN mapping test script")
    parser.add_argument('--lemma', help="Map this word (lemma)")
    parser.add_argument('--frame', help="Map this frame (lemma)")
    parser.add_argument('-s','--source',action='store_true',
                        help='Find source concept')
    parser.add_argument('-t','--target',action='store_true',
                        help='Find target concept')
    parser.add_argument('-l','--lang', help="Language of input files.",
                        required=True)
    parser.add_argument('--gdb-user',dest='gdbuser',default='gmruser',
                        help='GMR database username')
    parser.add_argument('-p','--gdb-pw',dest='gdbpw',default=None,required=True,
                        help='GMR database password')
    parser.add_argument('--gdb-name',dest='gdbname',default='icsi_'+datestring,
                        help='GMR database name')
    parser.add_argument('-v','--verbose',action='store_true',
                        help='Display more status messages')
    parser.add_argument('--use-se',dest="useSE",default=None,
                        help='SPARQL endpoint for conceptual graph searches')
    cmdline = parser.parse_args()
    
    # proc title manipulation to hide PW
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(--gdb-pw|--mdb-pw)(=|\s+)(\S+)',ur'\1\2XXXX',pstr)
    setproctitle.setproctitle(pstr)
    
    # this routine has to write its own files
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if cmdline.verbose:
        deflevel = logging.DEBUG
    else:
        deflevel = logging.INFO
    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)
    
    gmrdb = GMRDB(socket='/tmp/mysql.sock',
                  user=cmdline.gdbuser,
                  passwd=cmdline.gdbpw,
                  dbname=cmdline.gdbname)
    
    uri = u'https://metaphor.icsi.berkeley.edu/%s/MetaphorRepository.owl#' % (cmdline.lang)
    
    # retrieve possible target concepts, prioritize newer concepts
    tconlist = reversed([trow.target_concept for trow in gmrdb.getTargetConcepts()])
    
    logging.debug("tcon list is %s", pprint.pformat(tconlist))
    
    cnmapper = ConceptualNetworkMapper(cmdline.lang, useSE=cmdline.useSE, targetConceptRank=tconlist)
    
    if cmdline.lemma:
        if cmdline.target:
            print "Target concept:", cnmapper.getTargetConceptFromLemma(cmdline.lemma)
        if cmdline.source:
            print "Source concept:", pprint.pformat(cnmapper.getSourceConceptsFromLemma(cmdline.lemma))
    if cmdline.frame:
        framelist = [uri+cmdline.frame.replace(u' ',u'_')]
        if cmdline.target:
            print "Target concept:", cnmapper.getTargetConceptFromFrames(framelist)
        if cmdline.source:
            print "Source concept:", pprint.pformat(cnmapper.getSourceConceptsFromFrames(framelist))
        
    
if __name__ == "__main__":
    status = main()
    sys.exit(status)
