#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: cms
    :platform: Unix
    :synopsis: Construction Matching System (CMS) Linguistic Metaphor Extractor

The Construction Matching System (CMS) Linguistic Metaphor (LM) extractor functions as follows:

* find sentences that contain words from the target concept group, concepts, or frames, retrieved from the MetaNet conceptual network
    (via :py:mod:`mnrepository.metanetrdf`)
* use constructional pattern queries to find all source words that are related to the target words by the given constructions
    (via :py:mod:`cmsextractor.docdf`)
* search for frames in the MetaNet conceptual network for the source words, using FrameNet, WordNet, and Wiktionary
  if necessary and possible, to determine if it is metaphorical (via :py:mod:`mnrepository.metanetrdf`)

The system takes as input a json document file in the MetaNet format and outputs a file in the same format
with LM annotations added.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
import sys, argparse, codecs, re, time, os, numpy, logging, pprint, traceback, hashlib
from docquery import DocumentRepository
from mnrepository.metanetrdf import MetaNetRepository
from mnrepository.cnmapping import ConceptualNetworkMapper
from mnformats import mnjson
from depparsing.dep2json import parse
from mnpipeline.persiantagger import PersianPOSTagger
from multiprocessing import Pool
import cPickle as pickle

reload(sys)
sys.setdefaultencoding('utf-8')

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

class ConstructionMatchingSystem:
    """ CMS system class
    """
    # translations for russian dependency relations
    RUgrelmap = {u'предик': 'subj',
              u'1-компл': 'dobj',
              u'опред': 'adjmod',
              u'PUNC': 'term',
              u'ROOT': 'top',
              u'сент-соч': 'conj',
              u'соч-союзн': 'conj',
              u'1-компл': 'dobj',
              u'обст': 'spmod',
              u'атриб': 'spmod',
              u'предл': 'objprep',
              u'соотнос': 'conj',
              u'пролепт': 'ref',
              u'аппоз': 'ta',
              u'сочин': 'conj',
              u'подч-союзн': 'vsubord',
              u'огранич': 'prt',
              u'вводн':'mod',
              u'квазиагент': 'qamod'}
    
    # translations for Persian dependency relations: note that not all
    #   relations are translated.  This is for lack of understanding.
    FAgrelmap = {u'SBJ':'subj',
                 u'OBJ':'dobj',
                 u'PREDEP':'dep',
                 u'POSDEP':'dep',
                 u'MOS':'mos',
                 u'MOZ':'moz',
                 u'ADV':'dverb',
                 u'NPOSTMOD':'mod',
                 u'NPREMOD':'mod',
                 u'VCONJ':'conj',
                 u'NPP':'dep',
                 u'NEZ':'dep',
                 u'NCONJ':'conj',
                 u'PRD':'dep',
                 u'AJPP':'adjmod',
                 u'NE':'dep',
                 u'NVE':'dep',
                 u'MESU':'dep',
                 u'VCL':'dep',
                 u'APREMOD':'mod'}

    GRELMAP = {'ru': RUgrelmap,
               'fa': FAgrelmap}
    
    # for title filter
    titles = {'en': set(['President', 'Vice-President', 'Vice President',
                         'Chancellor', 'Prime Minister', 'King', 'Queen',
                         'General', 'Colonel', 'Professor', 'Senator',
                         'Congressman', 'Representative', 'Minister']),
              'es': set([u'El Presidente', u'El primer ministro']),
              'fa': set(),
              'ru': set([u'Президент',u'Премьер-министр'])}
        
    # Max/min number of words in a sentence.  Any sentence that exceeds this length
    # is skipped.  (For reasons of processing resources, and garbage filtering)
    # These are defaults
    MAX_WORDS_IN_SENTENCE = 128
    MIN_WORDS_IN_SENTENCE = 4
    
    def __init__(self,lang="en",lemfield="lem",posfield="pos",useSE=None,
                 skipInit=False,forcecache=False,engine='rdflib',nodepcheck=False,
                 excludedFamilies=[],noWCache=False,metanetrep=None,cnmapper=None,
                 metarcfname=None):
        """
        :param lang: language
        :type lang: str
        :param lemfield: name of the lemma field within the dicts contained in 'word'
        :type lemfield: str
        :param posfield: name of the POS field with in the dicts contained in 'word'
        :type posfield: str
        :param useSE: domain name or IP Address of SPARQL endpoint to use (optional)
        :type useSE: str
        :param skipInit: flag to run initialization only and then to exit (e.g. for running only dep parsing)
        :type skipInit: bool
        :param forcecache: force regeneration of target word cache
        :type forcecache: bool
        :param engine: library to use for Document querying.  Options are (rdflib, redland, sesame)
        :type engine: string
        :param nodepcheck: when true, do not check if there is a dependency parse (assumes that one exists)
        :type nodepcheck: bool
        :param excludedFamilies: list of frame family names.  All descendent frames are excluded as possible source frames via a strong penalty
        :type excludedFamilies: list
        :param noWCache: when true, the CMS does not generate or use the target word cache
        :type noWCache: bool
        :param metanetrep: a MetaNetRepository instance to use (otherwise, one is instantiated)
        :type metanetrep: MetaNetRepository
        :param cnmapper: a ConceptualNetworkMapper instance to use (otherwise, one is instantiated)
        :type cnmapper: ConceptualNetworkMapper
        
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing CMS instance')
        self.cachedir = '.'
        self.engine = engine
        self.forcecache = forcecache
        self.lang = lang
        self.lfield = lemfield
        self.pfield = posfield
        self.useSE = useSE
        self.nodepcheck = nodepcheck
        self.posre = re.compile(r'\.(a|v|n|p|prep|adj|adv|aa)$',flags=re.U|re.I)
        self.noWCache = noWCache
        self.exitAfterWCache = False
        self.lmlist = None
        
        # skip init option is for initializing the class for preprocessing only:
        # - for example, to just do dependency parsing and then stop
        if skipInit:
            return
        if metanetrep:
            self.mr = metanetrep
        else:
            self.mr = MetaNetRepository(lang, useSE=useSE)
            self.mr.initLookups()
        if cnmapper:
            self.cnmapper = cnmapper
        else:
            self.cnmapper = ConceptualNetworkMapper(lang, metanetrep=self.mr)
        self.excludedFrames = set()
        self.excludedFramesByTarget = {}
        self.excludedLUsByTarget = {}
        
        # there is a frame family called 'Excluded frames' which contains frames that
        # should always be excluded from consideration as posible source domain frames.
        # For the other languages, we get the excluded frames from the frame family
        # that corresponds to the English 'Excluded frames' family.
        # In addition to that, it is possible to pass in additional excluded frame
        # families, using the English frame family names.  Frames in those families
        # will also be excluded from consideration.  The correspondence works in the
        # same way for those frame families.
        #
        if self.lang=='en':
            self.excludedFrames.update(self.mr.getFramesFromFamily('Excluded frames'))
            for fam in excludedFamilies:
                self.excludedFrames.update(self.mr.getFramesFromFamily(fam))
        else:
            for fam in self.mr.getFrameFamiliesFromENC('Excluded frames'):
                self.excludedFrames.update(self.mr.getFramesFromFamily(fam))
            for enfam in excludedFamilies:
                for fam in self.mr.getFrameFamiliesFromENC(enfam):
                    self.excludedFrames.update(self.mr.getFramesFromFamily(fam))
        if not metarcfname:
            metarcfname = u'%s/metarcs_%s.txt' % (self.mr.cachedir, lang)
        self.loadMetaRCQueries(metarcfname)
    
    def setMaxSentenceLength(self, maxlen):
        self.MAX_WORDS_IN_SENTENCE = maxlen

    def setMinSentenceLength(self, minlen):
        self.MIN_WORDS_IN_SENTENCE = minlen
    
    def setSearchWordCaching(self, twcaching):
        self.noWCache = not twcaching

    def setAggregateLMs(self, lmlist):
        self.lmlist = lmlist
    
    def _initTargetPatterns(self):
        self.search_lus = {}
        self.search_wl = {}

    def createWordListStructs(self, lutups):
        """ Retrieves a list of LU tuples (lempos, frame, framename, familyname,
        conceptname,concepttype, conceptgroup) and returns a list of wordlist
        structs, which can be used for cxn match filtering.
        :param lutups: list of LU tuples
        :type lutups: list
        :return: list of wordlist structs
        :rtype: list
        """
        wlstructlist = []
        lemposCheck = set()
        for (lempos, frame, framename, familyname, conceptname,
             concepttype, conceptgroup) in lutups:
            #
            # Get rid of duplicate words: priority goes to lempos that occur
            # first, which means that the concepts, conceptgroups, etc. that are listed
            # first are prioritized
            #
            if lempos in lemposCheck:
                continue
            lemposCheck.add(lempos)
            npieces, searchregexp = self.mr.getMWELemposRegexp(lempos)
            self.logger.debug('Search string for lempos %s is %s' % (lempos, searchregexp))
            wstruct = {'lempos':lempos,
                       'frameuri':frame,
                       'framename':framename,
                       'family':familyname,
                       'concept':conceptname,
                       'contype':concepttype,
                       'congroup': conceptgroup,
                       'npieces':npieces,
                       'regexp': searchregexp,
                       're':re.compile(searchregexp,flags=re.U|re.I)}
            wlstructlist.append(wstruct)
        return wlstructlist
    
    def retrieveSearchWords(self, searchtype, famlist=[], framelist=[],
                            conlist=[], tcongrouplist=[]):
        """ Retrieves words from the MetaNet conceptual network with which to
        begin the LM search.  These words can be retrieved by reference to and
        combination of the following types:
        
        * list of IARPA target concept groups (GOVERNANCE, ECONOMIC INEQUALITY)
        * list of IARPA source/target concepts (GOVERNMENT, WEALTH, ABYSS. etc.)
        * list of MetaNet frame families
        * list of MetaNet frames

        Words are retrieved and regular expressions are pre-computed.
        Retrieved words/regular expressions are stored within the class in
        self.search_lus['target'|'source'] and self.search_wl['target'|'source']
        depending on whether the search is for target or source.  To search
        for both, the command should be run twice.  Note that tcongrouplist is
        ignored for source searches, as it applies only to targets.
        
        :param searchtype: either 'target' or 'source'
        :type searchtype: str
        :param famlist: list of frame families to search LMs for (list of strings)
        :type famlist: list
        :param framelist: list of frames to search LMs for
        :type framelist: list
        :param conlist: list of target concepts to search LMs for
        :type conlist: list
        :param tcongrouplist: list of target concept groups to search LMs for
        :type tcongrouplist: list
        
        """
        if searchtype not in ('target','source'):
            self.logger.error(u'invalid searchtype %s',searchtype)
            raise ValueError
        
        # Cache functionality: create 2 files, 1 with the binary cache, another that
        # explains whats in it
        if not self.noWCache:
            hashstr = u''.join(famlist) + u''.join(framelist) + u''.join(conlist) + \
                u''.join(tcongrouplist);
            fileid = hashlib.md5(hashstr).hexdigest()
            cachef = u'%s/.%s_wcache_%s_%s' % (self.cachedir, searchtype, self.lang, fileid)
            cacheidxf = u'%s/.%s_wcache_idx_%s_%s' % (self.cachedir, searchtype, 
                                                      self.lang, fileid)
            if os.path.exists(cachef) and (not self.forcecache):
                # load cache
                f = open(cachef,'rb')
                self.logger.info(u'Loading cached %s words ...',searchtype)
                try:
                    (self.search_lus[searchtype], self.search_wl[searchtype]) = pickle.load(f)
                    f.close()
                    return
                except:
                    self.logger.warn(u'Malformed %s cache at %s. Bypassing cache.', 
                                     searchtype, cachef)
        search_wl = []
        search_lus = []
        if searchtype=='source':
            for conname in conlist:
                lutups = self.mr.getLUsFromSourceConcept(conname,
                                                         self.cnmapper.sourceMappingLimit,
                                                         self.cnmapper.minSecondaryScore)
                self.logger.debug(u'retrieved %d source words from source concept %s.',
                                  len(lutups),conname)
                search_lus.extend(lutups)
        if searchtype=='target':
            for conname in conlist:
                lutups = self.mr.getLUsFromTargetConcept(conname)
                self.logger.debug(u'retrieved %d target words from target concept %s.',
                                  len(lutups),conname)
                search_lus.extend(lutups)
            for tcgroup in tcongrouplist:
                lutups = self.mr.getLUsFromTargetConceptGroup(tcgroup)
                self.logger.debug(u'retrieved %d target words from target concept group %s.'% (len(lutups),tcgroup))
                search_lus.extend(lutups)
        for frame in framelist:
            lutups = self.mr.getLUsFromFrameHierarchy(frame)
            self.logger.debug(u'retrieved %d %s words from frame %s.',len(lutups),
                                                                         searchtype,
                                                                         frame)
            search_lus.extend(lutups)
        for familyname in famlist:
            lutups = self.mr.getLUsFromFrameFamily(familyname)
            self.logger.debug(u'retrieved %d %s words from %s family.', len(lutups),
                                                                        searchtype,
                                                                        familyname)
            search_lus.extend(lutups)
        
        if search_lus:
            search_wl = self.createWordListStructs(search_lus)
            if searchtype in self.search_lus:
                self.search_lus[searchtype].update(search_lus)
            else:
                self.search_lus[searchtype] = search_lus
        else:
            self.logger.error('No search LUs retrieved.')
            return
        
        # sort from longest to shortest so expressions like 'income tax' match before 'tax'
        self.search_wl[searchtype] = sorted(search_wl, key=lambda tw: tw['npieces'],
                                            reverse=True)
        
        # save target word/struct list cache
        if not self.noWCache:
            f = open(cachef,'wb')
            self.logger.info(u'Caching retrieved %s words ...',searchtype)
            pickle.dump((self.search_lus[searchtype], self.search_wl[searchtype]),f,2)
            f.close()
            f = codecs.open(cacheidxf, mode="w", encoding="utf-8")
            for fam in famlist:
                print >> f, "Frame family", fam
            for sch in framelist:
                print >> f, "Frame", sch
            for tcg in tcongrouplist:
                print >> f, "Target concept group", tcg
            for tc in conlist:
                print >> f, "Concept", tc
            f.close()
    
        
    def retrieveSourceBlacklists(self, tcongrouplist, tconlist):
        """ Target concept specifications in the MetaNet wiki also allow for the specification
        of source domain blacklists.  The two types of blacklists allowed are
        words and frames.  These are later penalized by the system so that LM
        candidates with a blacklisted source later receive a lower metaphoricity score.
        
        :param tcongrouplist: list of target concept groups
        :type tcongrouplist: list
        :param tconlist: list of target concepts
        :type tconlist: list
        """
        bkframes = set()
        bklus = set()
        for tcon in tconlist:
            frames = self.mr.getBlacklistSourceFramesFromTargetConcept(conceptname=tcon)
            bkframes.update(frames)
            lus = self.mr.getBlacklistSourceLUsFromTargetConcept(conceptname=tcon)
            bklus.update(lus)
        for tcongroup in tcongrouplist:
            frames = self.mr.getBlacklistSourceFramesFromTargetConcept(conceptgroup=tcongroup)
            bkframes.update(frames)
            lus = self.mr.getBlacklistSourceLUsFromTargetConcept(conceptgroup=tcongroup)
            bklus.update(lus)
        # excluded frames lists
        bkframeByTarget = {}
        for bkframe, tcon in bkframes:
            if tcon not in bkframeByTarget:
                bkframeByTarget[tcon] = set()
            bkframeByTarget[tcon].add(bkframe)
        # excluded LUs lists
        bklusByTarget = {}
        for bklpos, tcon in bklus:
            if tcon not in bklusByTarget:
                bklusByTarget[tcon] = set()
            bklusByTarget[tcon].add(bklpos)
        self.excludedFramesByTarget.update(bkframeByTarget)
        self.excludedLUsByTarget.update(bklusByTarget)
        
    def searchForTargets(self,sentences):
        """ Load JSON doc and create a filtered list of sentences that are known
        to contain the target expressions of interest.  The target expressions
        should be loaded using retrieveTargetWords prior to running this method.
        
        Additional nodes are added to the sentence item:
        
        * mtext: string containing lemma and POS tags for each word for regexp searches
        * CMS: contains
            - idxset: set of word indices of all target-relevant words in the sentence
            - targetlist: list of target match structures which include
                * form, lemma, pos, start, end, frame, domain, idxlist
        
        :param sentences: list of sentences as per the JSON format
        :type sentences: list
        :returns: sublist of sentences that contain target expressions
        """
        targetsents = []
        sentence_testidx = -1
        fixedS = False
        #sllist = []
        #slhash = {}
        for sentence in sentences:
            sentence_testidx += 1
            if sentence['idx'] != sentence_testidx:
                # need to fix id numbers
                sentence['idx'] = sentence_testidx
                docpref, sidpart = sentence['id'].rsplit(u':',1)
                sentence['id'] = u'%s:%d' % (docpref, sentence_testidx + 1)
                fixedS = True
                #self.logger.info('Fixing id info for sentence at index %d', sentence_testidx)
            sentcontainstarget = False
            # for now skip sentences that exceed max num words
            if (not sentence['text'].strip()):
                self.logger.info(u'skipping zero length sentence %s',sentence['id'])
                continue
            if len(sentence['word']) > self.MAX_WORDS_IN_SENTENCE:
                self.logger.info(u'skipping sentence %s: length %d > MAX=%d',
                                 sentence['id'],
                                 len(sentence['word']),
                                 self.MAX_WORDS_IN_SENTENCE)
                continue
            if len(sentence['word']) < self.MIN_WORDS_IN_SENTENCE:
                self.logger.info(u'skipping sentence %s: length %d < MIN=%d',
                                 sentence['id'],
                                 len(sentence['word']),
                                 self.MIN_WORDS_IN_SENTENCE)
                continue
            if u'|' in sentence['text']:
                # skip sentences that contain a | character
                self.logger.info(u'skipping sentence %s: contains invalid character (|)',sentence['id'])
                continue
            
            # create match string
            matchwords = []
            for w in sentence['word']:
                try:
                    matchwords.append(u'%s=%s=%s=%s' % (w['form'],w[self.lfield],
                                                        w[self.pfield],w['idx']))
                except KeyError:
                    # may be because of pos field being missing
                    if self.pfield not in w:
                        w[self.pfield] = 'XX'
                    matchwords.append(u'%s=%s=%s=%s' % (w['form'],w[self.lfield],
                                                        w[self.pfield],w['idx']))
                    
            sentence['mtext'] = u' '.join(matchwords)
            sentence['CMS'] = {'idxset': set(),
                               'targetlist':[]}
            
            for tw in self.target_wl:
                # this is in case the same string occurs multiple times in the same sentence
                self.logger.debug('Searching for pattern %s in sentence: %s'%(tw['regexp'],sentence['mtext']))
                for matches in tw['re'].finditer(sentence['mtext']):
                    tmatch = {}
                    try:
                        idxlist = [int(matches.group(n+1)) for n in range(tw['npieces'])]
                    except:
                        print sentence['mtext']
                        pprint.pprint(tw)
                        pprint.pprint(tw['npieces'])
                        pprint.pprint(matches.group(0))
                        for n in range(tw['npieces']):
                            print 'N=',n,'=',matches.group(n+1)
                        raise
                    formlist = []
                    lemmalist = []
                    startlist = []
                    endlist = []
                    for idx in idxlist:
                        #self.logger.debug('idx=%d and form is %s'%(idx, sentence['word'][idx]['form']))
                        try:
                            formlist.append(sentence['word'][idx]['form'])
                            lemmalist.append(sentence['word'][idx][self.lfield])
                            startlist.append(sentence['word'][idx]['start'])
                            endlist.append(sentence['word'][idx]['end'])
                        except:
                            print >> sys.stderr, "Idx is", idx
                            print >> sys.stderr, "error in,", sentence['text']
                            pprint.pprint(sentence['word'])
                            raise
                    tmatch = {'form': u' '.join(formlist),
                              'lemma': u' '.join(lemmalist),
                              'start': min(startlist),
                              'end': max(endlist),
                              'mword': tw['lempos'],
                              'frameuri': tw['frameuri'],
                              'framename': tw['framename'],
                              'wdomain': tw['family'],
                              'framefamily': tw['family'],
                              'concept':tw['concept'],
                              'contype':tw['contype'],
                              'congroup':tw['congroup'],
                              'idxlist': idxlist}
                    if len(idxlist)==1:
                        tmatch['pos'] = sentence['word'][idxlist[0]][self.pfield]
                        
                    #print 'form=%s frame=%s wdomain=%s' % (tmatch['form'],tmatch['framename'],tmatch['wdomain'])
                    if set(idxlist).issubset(sentence['CMS']['idxset']):
                        # discard if this match is a subset of an earlier one:
                        #   this is to prevent 'tax' from matching if 'income tax' matched
                        self.logger.debug('Match %s discarded because or prior longer match.' % (tmatch['form']))
                        continue
                    self.logger.debug(u'Adding match %s from target lempos %s (%s):\t%s'%(tmatch['form'],tmatch['mword'],tw['regexp'],sentence['mtext']))
                    sentence['CMS']['idxset'].update(idxlist)
                    sentence['CMS']['targetlist'].append(tmatch)
                    sentcontainstarget = True
            if sentcontainstarget:
                #self.logger.info('sent %d has length %d and %d words',sentence_testidx,len(sentence['text']),len(sentence['word']))
                #sentlen = len(sentence['word'])
                #sllist.append(sentlen)
                #if sentlen in slhash:
                #    slhash[sentlen].append(str(sentence_testidx))
                #else:
                #    slhash[sentlen] = [str(sentence_testidx)]
                targetsents.append(sentence)
            else:
                del sentence['CMS']
        #slmean = numpy.mean(sllist)
        #slstd = numpy.std(sllist)
        #self.logger.info("Average sentence length: %f", slmean)
        #self.logger.info("Standard dev: %f", slstd)
        #abnorm = []
        #for l in sllist:
        #    if abs(l - slmean) > 2*slstd:
        #        abnorm.append(str(l))
        #self.logger.info("Abnormal sentence lengths: %s", ','.join(sorted(abnorm)))
        #for l in sorted(abnorm):
        #    self.logger.info(" sents of length %s: %s", l, ','.join(slhash[int(l)]))
        if fixedS:
            self.logger.info("one or more sentence ids fixed")
        return targetsents

    def searchForWords(self,sentences):
        """ Load JSON doc and create a filtered list of sentences that are known
        to contain the target or source expressions of interest.  The expressions
        should be loaded using retrieveSearchWords prior to running this method.
        
        Additional nodes are added to the sentence item:
        
        * mtext: string containing lemma and POS tags for each word for regexp searches
        * CMS: contains
            - tidxset: set of word indices of all target-relevant words in the sentence
            - targetlist: list of target match structures which include
                * form, lemma, pos, start, end, frame, domain, idxlist
            - sidxset: set of word indices of all target-relevant words in the sentence
            - sourcelist: list of source match structures which include
                * form, lemma, pos, start, end, frame, domain, idxlist
        
        :param sentences: list of sentences as per the JSON format
        :type sentences: list
        :return: sublist of sentences that contain target expressions
        :rtype: list
        """
        filteredsents = []
        sentence_testidx = -1
        fixedS = False
        #sllist = []
        #slhash = {}
        for sentence in sentences:
            sentence_testidx += 1
            # kludge to repair bad id numbers on some sentences
            if sentence['idx'] != sentence_testidx:
                # need to fix id numbers
                sentence['idx'] = sentence_testidx
                docpref, sidpart = sentence['id'].rsplit(u':',1)
                sentence['id'] = u'%s:%d' % (docpref, sentence_testidx + 1)
                fixedS = True
                #self.logger.info('Fixing id info for sentence at index %d', sentence_testidx)
            # for now skip sentences that exceed max num words
            if (not sentence['text'].strip()):
                self.logger.info(u'skipping zero length sentence %s',sentence['id'])
                continue
            if len(sentence['word']) > self.MAX_WORDS_IN_SENTENCE:
                self.logger.info(u'skipping sentence %s: length %d > MAX=%d',
                                 sentence['id'],
                                 len(sentence['word']),
                                 self.MAX_WORDS_IN_SENTENCE)
                continue
            if len(sentence['word']) < self.MIN_WORDS_IN_SENTENCE:
                self.logger.info(u'skipping sentence %s: length %d < MIN=%d',
                                 sentence['id'],
                                 len(sentence['word']),
                                 self.MIN_WORDS_IN_SENTENCE)
                continue
            if u'|' in sentence['text']:
                # skip sentences that contain a | character
                self.logger.info(u'skipping sentence %s: contains invalid character (|)',sentence['id'])
                continue
            
            # create match string
            matchwords = []
            for w in sentence['word']:
                try:
                    matchwords.append(u'%s=%s=%s=%s' % (w['form'],w[self.lfield],
                                                        w[self.pfield],w['idx']))
                except KeyError:
                    # may be because of pos field being missing
                    if self.pfield not in w:
                        w[self.pfield] = 'XX'
                    matchwords.append(u'%s=%s=%s=%s' % (w['form'],w[self.lfield],
                                                        w[self.pfield],w['idx']))
                    
            sentence['mtext'] = u' '.join(matchwords)
            sentence['CMS'] = {'targetidxset': set(),
                               'targetlist':[],
                               'sourceidxset': set(),
                               'sourcelist':[]}
            searchcheck = {}
            for searchtype in self.search_wl.keys():
                searchmatched = False
                search_idxset = searchtype + u'idxset'
                search_list = searchtype + u'list'
                for wstruct in self.search_wl[searchtype]:
                    # this is in case the same string occurs multiple times in the same sentence
                    self.logger.debug('Searching for pattern %s in sentence: %s',
                                      wstruct['regexp'],sentence['mtext'])
                    for matches in wstruct['re'].finditer(sentence['mtext']):
                        try:
                            idxlist = [int(matches.group(n+1)) for n in range(wstruct['npieces'])]
                        except:
                            print sentence['mtext']
                            pprint.pprint(wstruct)
                            pprint.pprint(wstruct['npieces'])
                            pprint.pprint(matches.group(0))
                            for n in range(wstruct['npieces']):
                                print 'N=',n,'=',matches.group(n+1)
                            raise
                        formlist = []
                        lemmalist = []
                        startlist = []
                        endlist = []
                        for idx in idxlist:
                            #self.logger.debug('idx=%d and form is %s'%(idx, sentence['word'][idx]['form']))
                            try:
                                formlist.append(sentence['word'][idx]['form'])
                                lemmalist.append(sentence['word'][idx][self.lfield])
                                startlist.append(sentence['word'][idx]['start'])
                                endlist.append(sentence['word'][idx]['end'])
                            except:
                                print >> sys.stderr, "Idx is", idx
                                print >> sys.stderr, "error in,", sentence['text']
                                pprint.pprint(sentence['word'])
                                raise
                        wmatch = {'form': u' '.join(formlist),
                                  'lemma': u' '.join(lemmalist),
                                  'start': min(startlist),
                                  'end': max(endlist),
                                  'mword': wstruct['lempos'],
                                  'frameuri': wstruct['frameuri'],
                                  'framename': wstruct['framename'],
                                  'wdomain': wstruct['family'],
                                  'framefamily': wstruct['family'],
                                  'concept':wstruct['concept'],
                                  'contype':wstruct['contype'],
                                  'congroup':wstruct['congroup'],
                                  'idxlist': idxlist}
                        if len(idxlist)==1:
                            wmatch['pos'] = sentence['word'][idxlist[0]][self.pfield]
                            
                        #print 'form=%s frame=%s wdomain=%s' % (tmatch['form'],tmatch['framename'],tmatch['wdomain'])
                        if set(idxlist).issubset(sentence['CMS'][search_idxset]):
                            # discard if this match is a subset of an earlier one:
                            #   this is to prevent 'tax' from matching if 'income tax' matched
                            self.logger.debug('Match %s discarded because or prior longer match.',
                                              wmatch['form'])
                            continue
                        self.logger.debug(u'Adding match %s from target lempos %s (%s):\t%s',
                                          wmatch['form'],wmatch['mword'],wstruct['regexp'],
                                          sentence['mtext'])
                        sentence['CMS'][search_idxset].update(idxlist)
                        sentence['CMS'][search_list].append(wmatch)
                        searchmatched = True
                if searchmatched:
                    searchcheck[searchtype] = True
                else:
                    searchcheck[searchtype] = False
            if all(searchcheck.values()):
                filteredsents.append(sentence)
            else:
                del sentence['CMS']
        if fixedS:
            self.logger.info("one or more sentence ids fixed")
        return filteredsents

            
    def _createGraph(self):
        """ Create an RDF graph which will contain the sentences
        """
        #self.sg = SentenceGraph(self.lang,self.pfield,self.lfield,useSE=self.useSE)
        self.sg = DocumentRepository(self.lang,self.pfield,self.lfield,engine=self.engine)
        
    def _translateFromEnFamilyNames(self, famlist):
        """ From English families, return their non-English correspondents in current
        language.
        
        :param famlist: list of English family names
        :type famlist: list
        :returns: list of non-English family names in the current language
        """
        famset = set()
        for enfam in famlist:
            for fam in self.mr.getFrameFamiliesFromENC(enfam):
                famset.add(fam)
        return list(famset)
    
    def _retrieveFramesFromNames(self, snamelist, translateFromEn=False):
        """ From English frame names, return frames in the current language
        for each.  Unlike for frame families, this method returns a list of URIRefs
        """
        if (self.lang != 'en') and translateFromEn:
            getFrameMethod = self.mr.getFrameFromEnName
        else:
            getFrameMethod = self.mr.getFrameFromName
        framelist = []
        for tsname in snamelist:
            tframe = getFrameMethod(tsname)
            if tframe:
                framelist.append(tframe)
        return framelist
    
    def _doesLMExist(self,sent,tmatch=None,sidxlist=[],smatch=None,tidxlist=[]):
        """ Method to check if an LM has already been found (for duplicate filtering)
        based on either passing ins a tmatch and and sidxlist, or a smatch and
        tidxlist.
        
        :param sent: sentence JSON structure
        :type sent: dict
        :param tmatch: target match structure
        :type tmatch: dict
        :sidxlist: list of source expression word indices
        :type sidxlist: list
        :param smatch: source match structure
        :type smatch: dict
        :tidxlist: list of target expression word indices
        :type tidxlist: list
        :return: true/false whether it exists
        :rtype: bool
        
        """
        if 'lms' not in sent:
            return False
        if tmatch:
            match = tmatch
            idxlist = sidxlist
            matchfield = 'target'
            idxlistfield = 'source'
        elif smatch:
            match = smatch
            idxlist = tidxlist
            matchfield = 'source'
            idxlistfield = 'target'
        else:
            self.logger.error('_doesLMExist called with no smatch or tmatch')
            raise ValueError
        for lm in sent['lms']:
            startword = sent['word'][idxlist[0]]
            endword = sent['word'][idxlist[-1]]
            if (lm[matchfield]['start'] == match['start']) and \
                (lm[matchfield]['end'] == match['end']) and \
                (lm[idxlistfield]['start'] == startword['start']) and \
                (lm[idxlistfield]['end'] == endword['end']):
                return True
        return False
        
    def _checkForMWE(self, wordidx, sent):
        """ Check if the word index falls inside of a Multiword Expression.
        If so, return the list of indices occupied by the MWE and its lempos
        
        :param sidx: source word index
        :type sidx: int
        :param sent: sentence structure
        :type sent: dict
        :returns: tuple(list, str)
        """
        word = sent['word'][wordidx]
        lpos = self.mr.getLemPos(word[self.lfield],
                                 word[self.pfield])
        # look for MWE
        mwelist = set()
        if lpos in self.mr.lpos2mwe:
            mwelist.update(self.mr.lpos2mwe[lpos.lower()])
        if word['form'] in self.mr.wf2mwe:
            mwelist.update(self.mr.wf2mwe[word['form']])
        if not mwelist:
            if word['form'].lower() in self.mr.wf2mwe:
                mwelist.update(self.mr.wf2mwe[word['form'].lower()])
        
        if not mwelist:
            return [wordidx],lpos
        sent['mwelist'] = mwelist
        midxlist = [wordidx]
        mlpos = lpos
        for mwe in mwelist:
            npieces, mweregexp = self.mr.mwere[mwe]
            try:
                for mmatches in re.finditer(mweregexp, sent['mtext'], flags=re.U|re.I):
                    try:
                        idxlist = [int(mmatches.group(n+1)) for n in range(npieces)]
                    except:
                        print sent['mtext']
                        pprint.pprint(npieces)
                        pprint.pprint(mmatches.group(0))
                        for n in range(npieces):
                            print 'N=',n,'=',mmatches.group(n+1)
                        raise
                    if (wordidx in idxlist) and (len(idxlist) > len(midxlist)):
                        midxlist = idxlist
                        mlpos = mwe
            except:
                print >> sys.stderr, sent['mtext']
                print >> sys.stderr, u'Error with %d piece regexp %s' % (npieces, mweregexp)
                raise
        return midxlist, mlpos

    def _checkExcludedSourceFrames(self, framelist):
        """ Filter out frames that are specifically excluded for source domains.
        
        :param framelist: list of frames
        :type framelist: list
        :returns: list of non-excluded frames, number of frames that were excluded
        """
        oklist = []
        nolist = []
        for frame in framelist:
            if frame in self.excludedFrames:
                nolist.append(frame)
                continue
            oklist.append(frame)
        return oklist, nolist
    
    def _checkPerTargetExcludedSourceFrames(self, targetconceptname, framelist):
        """ Filter out frames that are specifically excluded for source domains.

        :param targetconceptname: name of target concept
        :type targetconceptname: str
        :param framelist: list of frames
        :type framelist: list
        :returns: list of non-excluded frames, number of frames that were excluded
        """
        oklist = []
        nolist = []
        if targetconceptname not in self.excludedFramesByTarget:
            return framelist, []
        excludedFrames = self.excludedFramesByTarget[targetconceptname]
        for frame in framelist:
            if frame in excludedFrames:
                nolist.append(frame)
                continue
            oklist.append(frame)
        return oklist, nolist
            
    def _alreadyParsed(self, sent):
        """ Check if a sentence has already been dependency parsed.
        """
        for w in sent['word']:
            if 'dep' in w:
                return True
        return False
    
    def getUnparsed(self, sentences):
        """ Filter.  Return just the sentences within the given list that have not been
        dependency parsed.
        """
        usents = []
        for s in sentences:
            if 'dparse' in s:
                continue
            if 'word' in s:
                if self._alreadyParsed(s):
                    continue
            usents.append(s)
        return usents
    
    def getUnparsedRU(self, sentences):
        """ Filter.  Return just the sentences within the given list that have not been
        dependency parsed.  For RU, also check if the sentence has problematic .'s in it
        that will cause MALT to think it is multiple sentences
        """
        usents = []
        interdot = re.compile(r'(\S)\.(\S)',flags=re.U)
        for s in sentences:
            if 'dparse' in s:
                continue
            if 'word' in s:
                if self._alreadyParsed(s):
                    continue
            if u'.' in s['ctext'][:-1]:
                # there is a period in the middle of the sentence!
                # try substitutions
                s['ctext'] = re.sub(interdot,r'\1_\2',s['ctext'])
                if u'.' in s['ctext'][:-1]:
                    self.logger.error('skipping sentence %s due to multiple sentence terminators',
                                      s['id'])
                    continue
            usents.append(s)
        return usents
    
    def frameSearch(self, lemma, pos, lpos):
        SCORE_BASELINES = {'wikilpos': 0.6,
                           'wikilem': 0.5,
                           'fnlpos': 0.4,
                           'wikipwf': 0.6,
                           'wikifilt': 0.5,
                           'fnlem': 0.3} 
        BASELINE_EXP_INWIKI = 0.45
        frame_set = self.cnmapper.getFramesFromLemma(lemma=lemma,
                                                       pos=pos,
                                                       lpos=lpos)
        frames = []
        linkmethods = set()
        score = 0.0
        for frame, framename, method in frame_set:
            if (method in SCORE_BASELINES) and (SCORE_BASELINES[method] >= score):
                linkmethods.add(method)
                frames.append(frame)
                score = SCORE_BASELINES[method]
            
        if not frames:
            topframes, method = self.cnmapper.getFramesByExpansion(lemma,
                                                                     pos,
                                                                     maxRank=1)
            if topframes:
                for frame, score in topframes:
                    frames.append(frame)
                score = BASELINE_EXP_INWIKI
                linkmethods.add(method)
            
        linkmethod = u':'.join(linkmethods)
        return frames, linkmethod, score

    def loadMetaRCQueries(self, infname=None):
        """ Method that parses and loads metaphoric relational config query specification files.
        :param infname: file path to query file
        :type infname: str
        """
        if not infname:
            infname = self.defaultMetaRCQueryFile
        metarcname = None
        mscore = 0.0
        metarcqueries = {}
        metarcscores = {}
        negmetarc = []
        posmetarc = []
        linebuffer = []
        with codecs.open(infname, encoding='utf-8') as f:
            for line in f:
                # skip comments / blanks
                if line.startswith('#') or (not line.strip()):
                    continue
                if line.startswith('START METARC:'): # read CXN name
                    metarcname = line[13:].strip()
                    continue
                if line.startswith('END METARC'):
                    if linebuffer:
                        metarcqueries[metarcname] = u''.join(linebuffer)
                        linebuffer = []
                        metarcscores[metarcname] = mscore
                        if mscore > 0:
                            posmetarc.append(metarcname)
                        elif mscore < 0:
                            negmetarc.append(metarcname)
                        mscore = 0.0
                        continue
                if line.startswith('METAPHORICITY SCORE:'):
                    mscore = float(line[20:].strip())
                    continue
                linebuffer.append(line)

        self.metarcqueries = metarcqueries
        self.metarcscores = metarcscores
        self.posmetarc = sorted(posmetarc,
                                key=lambda metarcname: metarcscores[metarcname], reverse=True)
        self.negmetarc = sorted(negmetarc,
                                key=lambda metarcname: metarcscores[metarcname])
        self.logger.info('Loaded %d positive and %d negative metarc queries from %s.',
                         len(posmetarc),len(negmetarc),infname)

    
    def scoreLMCandidate(self, sentences, cxn, tlemma, slemma, sentidx, tidx, sidx):
        """ Given an LM candidate, compute a score and add it to the sentence's LM list,
        unless exclusion criteria apply.  Note that sentences are modified in-place.
        
        :param sentences: list of sentences (JSON structs)
        :type sentences: list
        :param cxn: the construction that found the LM
        :type cxn: str
        :param tlemma: the target lemma
        :type tlemma: str
        :param slemma: the source lemma
        :type slemma: str
        :param sentidx: the index of the sentence (in the input file)
        :type sentidx: int
        :param tidx: the index of the target word (relative to sentence)
        :type tidx: int
        :param sidx: the index of the source word (relative to sentence)
        :type sidx: int
        """
        #
        # constants
        BASELINE = 0.25
        BASELINE_INPUT = 0.7          # baseline on inputted parameters
        BASELINE_WN_2_WIKI = 0.4
        BASELINE_ALL_EXCLUDED = 0.1
        BASELINE_TITLE = 0.2
        EXCLUDED_SCHEMA_PENALTY = 0.3
        EXCLUDED_SCHEMA_PENALTY = 0.5
        EXCLUDED_LU_PENALTY = 0.8
        NON_MET_SCHEMA_PENALTY = 0.5
        SCHEMA_FILTER_SURVIVAL_BONUS = 0.3

        # set the baseline to 1/4 -- assumption about frequency of metaphorical use
        score = BASELINE

        # see if tidx is a target in the sidx sentence
        sent = sentences[sentidx]
        try:
            # candidates just match a cxn, so we need to check if there's even a target
            # domain word in the target slot and/or source domain word in the source
            # slow.  If there isn't, then we don't want to  even bother with trying to
            # score it.
            if sent['CMS']['targetidxset'] and (tidx not in sent['CMS']['targetidxset']):
                self.logger.debug(u'skipping %s because not in targetidxlist', tlemma)
                return
            if sent['CMS']['sourceidxset'] and (sidx not in sent['CMS']['sourceidxset']):
                self.logger.debug(u'skipping %s because not in sourceidxlist', slemma)
        except:
            self.logger.error(traceback.format_exc())
            self.logger.error(u'sent:\n%s',pprint.pformat(sent))
            self.logger.error(u'cxn: %s, tlemma: %s, slemma: %s, sentidx: %d, tidx: %d, sidx: %d',
                              cxn, tlemma, slemma, sentidx, tidx, sidx)
            raise
        # check that the cxn_source does not match a target expression and vice versa
        if sent['CMS']['targetidxset'] and (sidx in sent['CMS']['targetidxset']):
            # if the source term matches something in the target set, then skip it.
            self.logger.debug(u'skipping tmatch %s: source %s is in the target idx list',
                              tlemma,slemma)
            return
        if sent['CMS']['sourceidxset'] and (tidx in sent['CMS']['sourceidxset']):
            self.logger.debug(u'skipping smatch %s: target %s is in the source idx list',
                              slemma,tlemma)
        tword = sent['word'][tidx]
        # fix POS based on construction if possible
        tword[self.pfield] = self.mr.fixSourcePOS(cxn, tword[self.pfield],
                                                  tword['rpos'] if 'rpos' in tword else '')
        sword = sent['word'][sidx]
        # fix POS based on construction if possible
        sword[self.pfield] = self.mr.fixSourcePOS(cxn, sword[self.pfield],
                                                  sword['rpos'] if 'rpos' in sword else '')
        
        tlpos = self.mr.getLemPos(tword[self.lfield],
                                  tword[self.pfield])
        tidxlist = [tidx]
        slpos = self.mr.getLemPos(sword[self.lfield],
                                  sword[self.pfield])
        sidxlist = [sidx]

        # check if the source/target word and its context to see if being used as a part
        # of a MWE identified in our system.  if so, retrieve the MWE.  but only if
        # it was not part of the search constraint
        if not sent['CMS']['targetidxset']:
            tidxlist, tlpos = self._checkForMWE(tidx, sent)
        if not sent['CMS']['sourceidxset']:
            sidxlist, slpos = self._checkForMWE(sidx, sent)
        
        
        # An initial check was done to discard matches where the target slot
        # filler didn't match any of the pre-identified target/source expressions, where
        # such were passed into the system.  But now, we have to figure out which
        # of the target/source expressions fills the target/source slot in the cxn.
        #
        foundTmatch = {}
        if sent['CMS'].get('targetlist'):
            for tmatch in sent['CMS']['targetlist']:
                # make sure that we aren't finding an LM we already found in the same sentence
                if self._doesLMExist(sent,tmatch=tmatch,sidxlist=sidxlist):
                    self.logger.info('skipping LM %s %s because it already exists',
                                     tmatch['lemma'], slpos)
                    continue
                if tidx in tmatch['idxlist']:
                    foundTmatch = tmatch
                    break
            if not foundTmatch:
                # weird case where tmatch couldn't be found
                return
        foundSmatch = {}
        if sent['CMS'].get('sourcelist'):
            for smatch in sent['CMS']['sourcelist']:
                # make sure that we aren't finding an LM we already found in the
                # same sentence
                if self._doesLMExist(sent,smatch=smatch,tidxlist=tidxlist):
                    self.logger.info('skipping LM %s %s because it already exists',
                                     tlpos, smatch['lemma'])
                    continue
                if sidx in smatch['idxlist']:
                    foundSmatch = smatch
                    break
            if not foundSmatch:
                # weird case where smatch couldn't be found, since if source
                # contraint words were given, we shouldn't have gotten here
                # unless there was a source match
                return

        score_comments = []
        tlinkmethod = None
        slinkmethod = None
        tscore = BASELINE
        sscore = BASELINE
        # if foundTmatch is set, then the target expression was passed into the
        # extractor as a search parameter. So we do not need to search for a frame.
        # But if it is not set, then we need to find a frame, and or concept
        if foundTmatch:
            target_frames = [foundTmatch['frameuri']]
            tlinkmethod = 'input'
            tscore = BASELINE_INPUT
            score_comments.append(u'target(%s)'%(tlinkmethod))
        else:
            target_frames, tlinkmethod, tscore = self.frameSearch(tlemma,
                                                                    tword[self.pfield],
                                                                    tlpos)
            score_comments.append(u'target(%s)'%(tlinkmethod))
        
        if foundSmatch:
            # then there's no need to lookup the slemma to find a frame, since the
            # LM search started from a frame or a concept.
            source_frames = [smatch['frameuri']]
            slinkmethod = 'input'
            sscore = BASELINE_INPUT
            score_comments.append(u'source(%s)'%(slinkmethod))
        else:
            # search for a source domain frame
            # lpos sometimes has pos extensions, sometimes not, e.g. in case of MWE
            self.logger.debug('Looking up frame for "%s"', slpos)
            source_frames, slinkmethod, sscore = self.frameSearch(slemma,
                                                                    sword[self.pfield],
                                                                    slpos)
            score_comments.append(u'source(%s)'%(tlinkmethod))
        
        score = (tscore + sscore) / 2.0
        
        excluded_source_frames = set()
        
        # check if any of the source_frames are in the exclusion list,
        # if so, remove it, apply 10% penalty
        source_frames, excluded_sframes = self._checkExcludedSourceFrames(source_frames)
        if source_frames:
            if excluded_sframes:
                score = score - (score * EXCLUDED_SCHEMA_PENALTY)
                score_comments.append('exclpenalty')
        else:
            if excluded_sframes:
                score = BASELINE_ALL_EXCLUDED
                score_comments.append('allexcluded')
        excluded_source_frames.update(excluded_sframes)
        
        # target concept specific blacklist exclusions (only if there is a target concept)
        targetconceptname = None
        if foundTmatch.get('concept'):
            targetconceptname = foundTmatch['concept']
            if source_frames:
                source_frames, excluded_sframes = self._checkPerTargetExcludedSourceFrames(targetconceptname,
                                                                                              source_frames)
                if source_frames:
                    if excluded_sframes:
                        score = score - (score * EXCLUDED_SCHEMA_PENALTY)
                        score_comments.append('texclpenalty')
                else:
                    if excluded_sframes:
                        score = BASELINE_ALL_EXCLUDED
                        score_comments.append('tallexcluded')
                excluded_source_frames.update(excluded_sframes)
        
        vetted_target_source_pairs = set()
        removed_target_source_tups = set()
        mrcfactor = 1.0
        for tframe in target_frames:
            for sframe in source_frames:
                # check if the target is a subcase or other derivative
                # of the source
                matched_neg_config = False
                for metarcname in self.negmetarc:
                    mrcquery = self.metarcqueries[metarcname]
                    mrcfactor = abs(self.metarcscores[metarcname])
                    resultvars = ['tframe','sframe']
                    if '?otherframe' in mrcquery:
                        resultvars.append('otherframe')
                    if '?otherframename' in mrcquery:
                        resultvars.append('otherframename')
                    resultlist = self.mr.getQueryResultList(mrcquery,
                                                            {'tframe':tframe, 'sframe':sframe},
                                                            resultvars)
                    if resultlist:
                        if 'otherframename' in resultvars:
                            otherframes = u','.join([item['otherframename'] for item in resultvars])
                            self.logger.debug('Skipping: tframe %s and sframe %s are related by %s via (%s)',
                                              tframe,sframe,metarcname,otherframes)                            
                        else:
                            self.logger.debug('Skipping: tframe %s and sframe %s are related by %s',
                                              tframe,sframe,metarcname)
                        removed_target_source_tups.add((tframe,sframe,metarcname))
                        score_comments.append(metarcname)
                        matched_neg_config = True
                        break
                if not matched_neg_config:
                    vetted_target_source_pairs.add((tframe,sframe))
        
        if removed_target_source_tups:
            score = score * NON_MET_SCHEMA_PENALTY * (1.0 - mrcfactor)
            score_comments.append('nonmetpenalty')
                
        if vetted_target_source_pairs:
            score_comments.append('vetsurvival')
            score += ((1.0 - score)*SCHEMA_FILTER_SURVIVAL_BONUS)
        
        allcms = set()
        cmblessed_target_source_tups = set()
        sframes = set()
        tframes = set()
        sframenames = set()
        tframenames = set()
        for tframe,sframe in vetted_target_source_pairs:
            for metarcname in self.posmetarc:
                self.logger.debug(u'checking for %s (target=%s, source=%s)',
                                 metarcname,
                                 pprint.pformat(tframe),
                                 pprint.pformat(sframe))
                cmquery = self.metarcqueries[metarcname]
                sfactor = self.metarcscores[metarcname]
                qresult = self.mr.getQueryResultList(cmquery,
                                                     {'tframe':tframe,'sframe':sframe},
                                                     ['cm'])
                cms = [item['cm'] for item in qresult]
                if cms:
                    allcms.update(cms)
                    cmblessed_target_source_tups.add((tframe,sframe,metarcname,tuple(cms)))
                    score += ((1.0-score)*sfactor)
                    score_comments.append('cmb_'+metarcname)
                    break
            sframes.add(sframe)
            tframes.add(tframe)
            ssname = self.mr.getNameString(sframe)
            tsname = self.mr.getNameString(tframe)
            if ssname:
                sframenames.add(ssname)
            if tsname:
                tframenames.add(tsname)

        # excluded source LUs by target concept
        if targetconceptname and (targetconceptname in self.excludedLUsByTarget):
            if slpos in self.excludedLUsByTarget[targetconceptname]:
                score = score - (score * EXCLUDED_LU_PENALTY)
                score_comments.append('texclLU')        

        # filter out titles
        if (tword['form'] in self.titles[self.lang]) and sword['form'][0].isupper():
            score = BASELINE_TITLE
            score_comments.append('title')
        if (sword['form'] in self.titles[self.lang]) and tword['form'][0].isupper():
            score = BASELINE_TITLE
            score_comments.append('title')       

        # kludge: temporary
        if self.lang=='en':
            if cxn in ['T-noun_mod_S-noun','T-noun_poss_S-noun','T-noun_poss_S-noun.POSseq','S-noun_of_T-noun']:
                if tlemma.lower() in ['government','state']:
                    if sword[self.lfield].lower() in ['building','troop','soldier','militia',
                                                      'army','house','residence','bond']:
                        score = 0.2
                        score_comments.append('NNexcl')
            elif cxn=='S-adj_mod_T-noun':
                if tlemma.lower() in ['gun','weapon','firearm',
                                                    'pistol','handgun']:
                    if sword[self.lfield].lower() in ['illegal','dangerous','illicit',
                                                      'lawful','legal']:
                        score = 0.2
                        score_comments.append('NNexcl')
        

        # SJD: sort lists to make regression tests re-runnable
        self.addLM(sent, cxn, foundTmatch, foundSmatch,
                   sidxlist, slpos, sorted(list(sframes)), sorted(list(sframenames)), slinkmethod,
                   tidxlist, tlpos, sorted(list(tframes)), sorted(list(tframenames)), tlinkmethod,
                   sorted(list(allcms)),
                   sorted(list(cmblessed_target_source_tups)),
                   sorted(list(removed_target_source_tups)),
                   score, scorecomments=u':'.join(score_comments))
    
    def setWCacheOnlyRun(self, docacheonly):
        """ Method to cause the CMS instance to exit after generating the target word cache
        """
        self.exitAfterWCache = docacheonly

    def prepSearchWords(self,
                        tfamlist=[], tsnamelist=[],tconlist=[],tcongrouplist=[],
                        sfamlist=[], ssnamelist=[],sconlist=[],
                        translateEn=False):
        # clears the data structure that hold to target search patterns
        self._initTargetPatterns()
        tframelist = []
        sframelist = []
        if (self.lang != 'en') and translateEn:
            # convert English family names to LANG family names if needed
            if tfamlist:
                tfamlist = self._translateFromEnFamilyNames(tfamlist)
            if sfamlist:
                sfamlist = self._translateFromEnFamilyNames(sfamlist)
        if tsnamelist:
            tframelist = self._retrieveFramesFromNames(tsnamelist, translateEn)
        if ssnamelist:
            sframelist = self._retrieveFramesFromNames(ssnamelist, translateEn)
        self.logger.warn('retrieving search words from conceptual network')
        if tfamlist or tframelist or tcongrouplist or tconlist:
            self.retrieveSearchWords('target',tfamlist,tframelist,tconlist,tcongrouplist)
        if sfamlist or sframelist or sconlist:
            self.retrieveSearchWords('source',sfamlist,sframelist,sconlist)
        if tcongrouplist or tconlist:
            self.retrieveSourceBlacklists(tcongrouplist,tconlist)
        
    def getSubcorpus(self, in_sentences,
                        forcePOScomp=False):
        """ Create a subcorpus of sentences filtered according to the specified
        configuration of target/source families.  The list of sentences is
        returned.
        """
        out_sentences = []
        
        # start sentence processing
        # skip the first sentence if id is none (for garbage in ruwac)
        if not in_sentences[0]['id']:
            in_sentences = in_sentences[1:]
        
        if ('word' not in in_sentences[0]) or forcePOScomp:
            self.computePOS(self.lang,in_sentences,self.logger,self.pfield,self.lfield)
        out_sentences = self.searchForWords(in_sentences)
        return out_sentences
    
    def runCMS(self, sentences,
               tfamlist=[], tsnamelist=[],tconlist=[],tcongrouplist=[],
               sfamlist=[], ssnamelist=[],sconlist=[],
               cxnlist=None, cxnfname=None, doallcxns=False,
               forcePOScomp=False, translateEn=False):
        
        """ Run the CMS system.  This method wraps two approaches.  One which uses
        python's rdflib to process SPARQL queries on cxns and the conceptual network,
        and one that queries an external stand-alone Sparql endpoint server (sesame).
        
        :param sentences: sentences to search (JSON structs)
        :type sentences: list
        :param enfamlist: list of target domain families to search. In English
        :type enfamlist: list
        :param entsnamelist: list of names of target frames to search. In English.
        :type entsnamelist: list
        :param tcongrouplist: list of target concept groups to search. In English.
        :type tcongrouplist: list
        :param tconlist: list of target concepts to search. In English.
        :type tconlist: list
        :param cxnlist: list of constructions to search for (names of cxns from cxn definition file)
        :type cxnlist: list
        :param cxnfname: file path to cxn definition file
        :type cxnfname: str
        :param doallcxns: flag to process all cxns rather than just the ** ones
        :type doallcxns: bool
        :param forcePOScomp: force POS tagger to run even if tags are already in the input
        :type forcePOScomp: bool
        """
        
        self.logger.info('start search for target patterns')
        # clears the data structure that hold to target search patterns
        self._initTargetPatterns()
        tframelist = []
        sframelist = []
        if (self.lang != 'en') and translateEn:
            # convert English family names to LANG family names if needed
            if tfamlist:
                tfamlist = self._translateFromEnFamilyNames(tfamlist)
            if sfamlist:
                sfamlist = self._translateFromEnFamilyNames(sfamlist)
        if tsnamelist:
            tframelist = self._retrieveFramesFromNames(tsnamelist, translateEn)
        if ssnamelist:
            sframelist = self._retrieveFramesFromNames(ssnamelist, translateEn)
        self.logger.warn('retrieving search words from conceptual network')
        if tfamlist or tframelist or tcongrouplist or tconlist:
            self.retrieveSearchWords('target',tfamlist,tframelist,tconlist,tcongrouplist)
        if sfamlist or sframelist or sconlist:
            self.retrieveSearchWords('source',sfamlist,sframelist,sconlist)
        if self.exitAfterWCache:
            return
        if tcongrouplist or tconlist:
            self.retrieveSourceBlacklists(tcongrouplist,tconlist)
        
        # start sentence processing
        # skip the first sentence if id is none (for garbage in ruwac)
        if not sentences[0]['id']:
            sentences = sentences[1:]
        
        if ('word' not in sentences[0]) or forcePOScomp:
            self.computePOS(self.lang,sentences,self.logger,self.pfield,self.lfield)
        self.logger.warn('searching sentences for search words')
        self.match_sents = self.searchForWords(sentences)
        self.logger.info('end search for target patterns')
        self.logger.warn('searching for construction matches')
        self._createGraph()
        self.sg.loadCXNQueries(cxnfname)
        # run dependency parse: only on subset that have target terms and
        # which have not already been parsed
        if self.match_sents:
            if self.nodepcheck==False:
                self.logger.info('Determining which sentences need parsing.')
                if self.lang == 'ru':
                    parseFilter = self.getUnparsedRU
                else:
                    parseFilter = self.getUnparsed
                sentsToParse = parseFilter(self.match_sents)
                if sentsToParse:
                    self.parseDependencies(self.lang,sentsToParse,self.logger)
            if self.lang=='ru':
                # for russian, even if we are not parsing, run translator
                # this is because relation names are in russian
                self.translateDependencies(self.match_sents)
        else:
            self.logger.warn('List of target sents is empty!')
            
        if self.engine != 'rdflib':
            self.runSearchSE(sentences, cxnlist, doallcxns)
        else:
            self.runSearchPy(sentences, cxnlist, doallcxns)

    def runSearchPy(self, sentences, cxnlist=None, doallcxns=False):
        """ Python rdflib-based LM search method.
        In this case the search engine is not powerful enough to run over all the sentences.
        We iterate over sentences and run all the queries on each sentence.
        :param sentences: list of sentences
        :type sentences: list
        :param cxnlist: list of cxns names to search for
        :type cxnlist: list
        :param doallcxns: flag to ignore cxnlist and search for all available cxns
        :type doallcxns: bool
        """     
        self.logger.info('start CMS search on %d sentences with target matches'%(len(self.match_sents)))
        for sent in self.match_sents:
            self.logger.warn(u'searching sentence %s' % (sent['id']))
            self.logger.debug(u'Searching sentence: %s' % (sent['text']))
            self.sg.newSentence(sent)
            cxn_related_pairs = self.sg.getCXNRelatedPairs(cxns=cxnlist,allcxns=doallcxns)
            self.logger.warn('scoring %s cxn-related pairs' % (len(cxn_related_pairs)))
            for (cxn, tlemma, slemma, sentidx, tidx, sidx) in cxn_related_pairs:
                self.logger.debug(u'... target=%s source=%s cxn=%s',tlemma,slemma,cxn)
                self.scoreLMCandidate(sentences, cxn, tlemma, slemma, sentidx, tidx, sidx)
            # cleanup: sets cannot be serialized to JSON
            sent['CMS']['idxset'] = list(sent['CMS']['idxset'])
        self.logger.info('end CMS search')

    def runSearchSE(self, sentences, cxnlist=None, doallcxns=False):
        """ SPARQL Endpoint based LM search method.
        In this case we run the cxn queries over all the sentences at once.
        :param sentences: list of sentences
        :type sentences: list
        :param cxnlist: list of cxns names to search for
        :type cxnlist: list
        :param doallcxns: flag to ignore cxnlist and search for all available cxns
        :type doallcxns: bool
        """
        self.sg.createSentencesGraph(self.match_sents)
        try:
            self.logger.info('start CMS search on %d sentences with target matches',len(self.match_sents))
            self.logger.info('start cxn querying')
            cxn_related_pairs = self.sg.getCXNRelatedPairs(cxns=cxnlist,allcxns=doallcxns)
            self.logger.warn('scoring %d candidate LMs returned by cxn queries',len(cxn_related_pairs))
            for (cxn, tlemma, slemma, sentidx, tidx, sidx) in cxn_related_pairs:
                self.logger.debug(u'... target=%s source=%s cxn=%s',tlemma,slemma,cxn)
                self.scoreLMCandidate(sentences, cxn, tlemma, slemma, sentidx, tidx, sidx)
        except:
            self.sg.deleteSentencesGraph()
            raise
        self.sg.deleteSentencesGraph()
        for sent in self.match_sents:
            # cleanup: this is because sets cannot be serialized to JSON
            if 'tidxset' in sent['CMS']:
                sent['CMS']['tidxset'] = list(sent['CMS']['tidxset']) 
            if 'sidxset' in sent['CMS']:
                sent['CMS']['sidxset'] = list(sent['CMS']['sidxset']) 
        self.logger.info('end CMS search')
        
    def addLM(self, sent, cxn, tmatch, smatch,
              sidxlist, slpos, sframes, sframenames,slinkmethod,
              tidxlist, tlpos, tframes, tframenames,tlinkmethod,
              allcms, goodtups, badtups,
              score, scorecomments=None):
        """ Add an LM found by the system to the sentence.  Note that LM is added in-place.
        
        :param sent: sentence structure
        :type sent: dict
        :param cxn: name of construction that matched the LM
        :type cxn: str
        :param tmatch: target match structure
        :type tmatch: dict
        :param sidxlist: list of indices of the source expression words
        :type sidxlist: list
        :param slpos: source expression lempos
        :type slpos: str
        :param sframes: frames matched by the source expression
        :type sframes: list
        :param sframenames: names of the frames matched by the source expression
        :type sframenames: list
        :param allcms: list of CMs that were found supporting the LM
        :type allcms: list
        :param score: confidence rating of the LM
        :type score: float
        :param sourcemapmethod: how the source word was mapped to a frame
        :type sourcemapmethod: str
        :param scorecomments: comments on how the score was computed
        :type scorecomments: str
        """
        
        if smatch:
            source = smatch
            if smatch.get('frameuri'):
                source['frameuris'] = [smatch['frameuri']]
            if smatch.get('framename'):
                source['framenames'] = [smatch['framename']]
            source['linkmethod'] = 'input'
        else:
            source = {u'form':u' '.join([sent['word'][idx]['form'] for idx in sidxlist]),
                      u'lemma':u' '.join([sent['word'][idx][self.lfield] for idx in sidxlist]),
                      u'lpos':slpos,
                      u'start':sent['word'][sidxlist[0]]['start'],
                      u'end':sent['word'][sidxlist[-1]]['end'],
                      u'frameuris':sframes,
                      u'framenames':sframenames,
                      u'linkmethod':slinkmethod}
            if len(sidxlist)==1:
                source[u'pos'] = sent['word'][sidxlist[0]][self.pfield]
        if tmatch:
            target = tmatch
            if tmatch.get('frameuri'):
                target['frameuris'] = [tmatch['frameuri']]
            if tmatch.get('framename'):
                target['framenames'] = [tmatch['framename']]
            target['linkmethod'] = 'input'
        else:
            target = {u'form':u' '.join([sent['word'][idx]['form'] for idx in tidxlist]),
                      u'lemma':u' '.join([sent['word'][idx][self.lfield] for idx in tidxlist]),
                      u'lpos':tlpos,
                      u'start':sent['word'][tidxlist[0]]['start'],
                      u'end':sent['word'][tidxlist[-1]]['end'],
                      u'frameuris':tframes,
                      u'framenames':tframenames,
                      u'linkmethod':tlinkmethod}
            if len(tidxlist)==1:
                target[u'pos'] = sent['word'][tidxlist[0]][self.pfield]
        
        promrcs = []
        for tframe, sframe, metarc, cms in goodtups:
            promrcs.append({u'metarc':metarc,
                            u'target':self.mr.getNameString(tframe),
                            u'source':self.mr.getNameString(sframe),
                            u'cms':[self.mr.getNameString(cm) for cm in cms]})
        conmrcs = []
        for tframe, sframe, metarc in badtups:
            conmrcs.append({u'metarc':metarc,
                            u'target':self.mr.getNameString(tframe),
                            u'source':self.mr.getNameString(sframe)})
        
        lm = {u'name':u'%s %s'%(target['lemma'],source['lemma']),
              u'cxn':cxn,
              u'target':target,
              u'source':source,
              u'seed':u'None',
              u'cms':allcms,
              u'promrcs':promrcs,
              u'conmrcs':conmrcs,
              u'score':score,
              u'scorecom':scorecomments,
              u'extractor':'CMS'}
        if allcms:
            lm['cmnames'] = [self.mr.getNameString(cm) for cm in allcms]
        self.logger.debug(u'found LM "%s" (%s) with score %f' % (lm['name'],
                                                                lm['cxn'],
                                                                lm['score']))
        if self.lmlist is not None:
            lm['sent_id'] = sent['id']
            self.lmlist.append(lm)
        if 'lms' not in sent:
            sent['lms'] = []
        sent['lms'].append(lm)
    
    @staticmethod        
    def computePOS(lang, sentences, logger=logging, pfield='pos',lfield='lem'):
        """ A statis method for computing POS tags and adding them under a 'word'
        node in each sentence. The 'word' node is a list of dicts, where each
        describes a word in the sentence.  Uses TreeTagger for EN, ES, and RU
        and a custom HMM tagger for FA.
        
        :param sentences: list of sentences
        :type sentences: str
        :param logger: a python logger
        :type logger: logging.Logger
        :param pfield: field name for the POS tag
        :type pfield: str
        :param lfield: field name for the lemma
        :type lfield: str
        """
        logger.info('start POS tagging')
        if lang == 'fa':
            pt = PersianPOSTagger()
            for sent in sentences:
                sent['ctext'] = pt.cleanText(sent['text'])
                tags = pt.run_hmm_tagger(sent['ctext'])
                #print 'sentence %d: %s\n%s' % (sidx, sent['text'],pprint.pformat(tags))
                sent['word'] = pt.getWordList(sent['text'], sent['ctext'], tags,
                                              pfield, lfield)
        else:
            tt = mnjson.MNTreeTagger(lang)
            tt.cleanText(sentences)
            tt.run(sentences)
        logger.info('end POS tagging')
    
    @staticmethod
    def incorporateDeps(lang, in_sentences, parsed_sentences, redundancy=False):
        """ A statis method that incorporates dependencies from the 'word' field
        of parsed_sentences into the 'word' field of in_sentences, keeping
        alignment with existing tokenization, by POS tagger/lemmatizers.
        :param in_sentences: tagged input sentences 
        :type in_sentences: list
        :param parsed_sentences: output of dependency parser
        :type parsed_sentences: list
        :param redundancy: preserves redundant information for debugging
        :type redundancy: bool
        """
        for psent in parsed_sentences:
            # need to generate hash lookup because list is not in order
            # and can be missing words
            pwlookup = {}
            #sys.exit()
            for pw in psent['word']:
                pwlookup[pw['idx']] = pw
            # find corresponding original sentence
            isent = in_sentences[psent['idx']]
            #isent['psent'] = psent
            # go through each word in the parsed version and map to original
            p2imap = {}
            pn2inmap = {'0':'0'}
            current_iidx = 0
            # scan through parsed words in order
            for pidx, pw in sorted(pwlookup.items()):
                # create parse to initial word mapping
                for iidx in range(current_iidx,len(isent['word'])):
                    iw = isent['word'][iidx]
                    try:
                        if (pw['form']==iw['form']) or (pw['lem']==iw['lem']):
                            p2imap[pidx] = iidx
                            pn2inmap[pw['n']] = iw['n']
                            current_iidx = iidx+1
                            break
                        elif (lang=='es') and (pw['lem']==u'de') and (iw['lem']==u'del')\
                             and (iw['pos']==u'PDEL') and (pw['pos']==u'SPS00'):
                            p2imap[pidx] = iidx
                            pn2inmap[pw['n']] = iw['n']
                            current_iidx = iidx+1
                            break
                    except KeyError:
                        # not all words have 'lem' fields
                        continue
                    # before trying out the next iword, see if the next pword and the
                    # next iword are a match
                    try:
                        npidx = pidx + 1
                        npw = pwlookup[npidx]
                        niidx = iidx + 1
                        niw = isent['word'][niidx]
                        if (npw['form']==niw['form']) or (npw['lem']==niw['lem']):
                            # then consider the current iw and pw to be equivalent
                            p2imap[pidx] = iidx
                            pn2inmap[pw['n']] = iw['n']
                            current_iidx = iidx+1
                            break
                        # check if psent has an extra word (i.e. the next pword is the
                        # same as the currect iword)
                        if (npw['form']==iw['form']) or (npw['lem']==iw['lem']):
                            # if so, skip go to next pword without advancing
                            # current iword
                            break
                    except:
                        # if there is any error, forget it, go on to next iw
                        pass
                    
                if current_iidx >= len(isent['word']):
                    break
            isent['p2imap'] = p2imap
            isent['pn2inmap'] = pn2inmap
            isent['parseword'] = psent['word']
            if redundancy and ('dparse' in psent):
                isent['dparse'] = psent['dparse']
            # insert into iwords, the dep info in pwords
            
            for pw in psent['word']:
                if pw['idx'] in p2imap:
                    iidx = p2imap[pw['idx']]
                else:
                    continue
                iw = isent['word'][iidx]
                try:
                    iw['rpos'] = pw['pos']
                    iw['rlem'] = pw['lem']
                except KeyError:
                    # not all pw have these fields (e.g. PUNC)
                    pass
                if 'dep' in pw:
                    dep = pw['dep'].copy()
                else:
                    # usually bc the main verb has no deps defined on it
                    dep = {'type': 'ROOT',
                           'head': '0'}
                if ('head' in dep) and (dep['head'] in pn2inmap):
                    try:
                        dep['head'] = pn2inmap[dep['head']] # these should be ranks, not idx
                    except:
                        # usually because of difference in tokenization
                        pass
                    if lang in ['ru', 'fa']:
                        # translate russian malt gramrel names
                        try:
                            dep['otype'] = dep['type']
                            dep['type'] = ConstructionMatchingSystem.GRELMAP[lang][dep['type']]
                        except KeyError:
                            dep['type'] = 'dep'
                    # for RASP subtypes appear as type.subtype
                    if '.' in dep['type']:
                        (rtype,rsubtype) = dep['type'].split('.',1)
                        dep['type'] = rtype
                        dep['subtype'] = rsubtype
                    iw['dep'] = dep

    @staticmethod
    def parseDependencies(lang, in_sentences,logger=logging):
        """ A static method for running the dependency parser.
        :param in_sentences: input sentences (JSON structs)
        :type in_sentence: list
        :param logger: a python logging instance
        :type logger: logging.Logger
        """
        logger.info('start dependency parsing on %d sentences', len(in_sentences))
          
        # call to parser
        out_jdata = parse(lang, [s['ctext'] for s in in_sentences])
        #pprint.pprint(out_jdata)
        #self.logger.debug(u'post-parsed jdata:\n'+pprint.pformat(out_jdata))
        #pprint.pprint(out_jdata['sentences'][0][parsername]['word'])

        ConstructionMatchingSystem.incorporateDeps(lang, in_sentences, out_jdata['sentences'])

        logger.info('end dependency parsing')

    @staticmethod
    def translateDependencies(in_sentences):
        """
        incorporateDeps also translates while aligning the output of the parser
        with the word segmentation of the POS tagging.  this method is called only
        where a dep parse is already there in the input document directly under
        the sentence node but untranslated (as in the RUWAC json).
        :param in_sentences: list of sentences to process
        :type in_sentences: list
        """
        for sent in in_sentences:
            if 'word' not in sent:
                continue
            for w in sent['word']:
                if 'dep' not in w:
                    continue
                dep = w['dep']
                if 'otype' in dep:
                    #already translated
                    return
                try:
                    dep['otype'] = dep['type']
                    dep['type'] = ConstructionMatchingSystem.GRELMAP[self.lang][dep['type']]
                except KeyError:
                    dep['type'] = 'dep'
            if 'dparse' not in sent:
                continue
            for dep in sent['dparse']:
                if 'otype' in dep:
                    #already translated
                    return
                try:
                    dep['otype'] = dep['type']
                    dep['type'] = ConstructionMatchingSystem.GRELMAP[self.lang][dep['type']]
                except KeyError:
                    dep['type'] = 'dep'
    
    @staticmethod 
    def preProcess(lang, in_sentences, logger=logging, pfield='pos', lfield='lem'):
        """
        Statis method to do only the preprocessing step: POS tagging and dep parsing. Note that
        sentences are altered in-place.
        :param in_sentences: list of sentence JSON dicts
        :type in_sentences: list
        :param logger: a python logger
        :type logger: logging.Logger
        :param pfield: field name for the POS tag
        :type pfield: str
        :param lfield: field name for the lemma
        :type lfield: str
        """
        logger.info('tagging %d sentences',len(in_sentences))
        ConstructionMatchingSystem.computePOS(lang,in_sentences,logger,pfield,lfield)
        toolong = 0
        sentences = []
        for s in in_sentences:
            try:
                slen = len(s['word'])
            except KeyError:
                logger.info('skipping possibly empty sentence %s: %s',s['id'],s['text'])
                continue
            if slen > ConstructionMatchingSystem.MAX_WORDS_IN_SENTENCE:
                #self.logger.info(u'sent %s has length %s, skipping:\n%s',
                #                 s['id'], slen, s['text'])
                toolong += 1
            else:
                sentences.append(s)
        logger.info('skipped %d sentences that exceed length %d',
                         toolong,ConstructionMatchingSystem.MAX_WORDS_IN_SENTENCE)
        logger.info('dependency parsing %s sentences', len(sentences))
        ConstructionMatchingSystem.parseDependencies(lang,sentences,logger)
        
        
def runCMSInstance((cmdline, infname)):
    """ Method for running the CMS from the main function, for testing purposes.
    This is meant to be run via :py:mod:`multiprocessing`
        
    """
    famlist = [u'Poverty frames',u'Taxation frames',u'Wealth frames',u'The Rich frames']
    posf = 'pos'
    lemf = 'lem'
    
    outfname = 'Result_'+os.path.basename(infname)
    
    jdata = mnjson.loadfile(infname)
    CMS = ConstructionMatchingSystem(jdata['lang'],lemf,posf)
    if cmdline.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    if cmdline.sentidx==None:
        in_sentences = jdata['sentences']
    else:
        in_sentences = [jdata['sentences'][int(cmdline.sentidx)]]
                    
    # do LM search
    CMS.runSearch(famlist, in_sentences, cxnlist=cmdline.cxns, doallcxns=cmdline.allcxns)
    
    # write json back out
    jdata['sentences'] = in_sentences
    mnjson.writefile(outfname, jdata)

def main():
    """ Main method for testing purposes.
    """
    
    CHUNKSIZE = 1
    
    FORMAT = '%(asctime)-15s - %(message)s'
    DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
    logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="CMS extractor.")
    parser.add_argument("infiles", help="Input file(s) in JSON format",
                        metavar='infile',
                        type=str,
                        nargs='+')
    parser.add_argument("-v","--verbose",help="Display verbose messages",
                        action="store_true",dest="verbose")
    parser.add_argument("-c","--cxns",help="Run only these cxns (comma separated)")
    parser.add_argument("-a","--allcxns",
                        help="Run all cxns instead of IARPA-privileged cxns only.",
                        action="store_true")
    parser.add_argument("-s","--sentidx",help="Run only one this sentence.",
                        default=None)
    parser.add_argument("-p","--parallel",help="Run in parallel",
                        type=int,
                        default=1)
    
    cmdline = parser.parse_args()
    
    
    if cmdline.cxns:
        cmdline.cxns = cmdline.cxns.split(',')

    if cmdline.parallel > 1:
        poolitems = []
        for infilename in cmdline.infiles:
            poolitems.append((cmdline,infilename))
            # initialize 5 workers
        pool = Pool(cmdline.parallel)
        pool.map(runCMSInstance, poolitems, CHUNKSIZE)
    else:
        for infilename in cmdline.infiles:
            runCMSInstance((infilename,cmdline))
    return 0

if __name__ == '__main__':
    sys.exit(main())
