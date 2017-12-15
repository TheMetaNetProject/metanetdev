#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: metanetrdf
   :platform: Unix
   :synopsis: Python lib for accessing MetaNet conceptual network repository in RDF.

Python library for accessing the MetaNet conceptual network repository in RDF via
:py:mod:`rdflib` or via a standalone RDF triplestore server with a Sparql Endpoint.
Also creates lookup dictionaries to speed up frequent operations.

Example::

    from mnrepository.metanetrdf import MetaNetRepository
    mr = MetaNetRepository()
    # iterates though all frames and prints the resulting URIRef for each
    # frame
    for row in mr.getFrames():
        print row.frame

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF,RDFS,OWL,XSD
import logging, os, re, sys, argparse, pprint, traceback, random, operator, codecs, time, pprint
from bunch import Bunch as edict
from rdflib.plugins.sparql import prepareQuery
import cPickle as pickle
from fnxml import FrameNet
from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper, JSON
from mnrepository.wiktionary import Wiktionary
from persianwordforms import PersianWordForms

class MetaNetRepository:
    """ Class for accessing MetaNet conceptual network repository.  By default
    :mod:rdflib is used to access rdf files.  Alternatively, a SPARQL endpoint
    can be given at initialization time.  The latter is significantly faster
    for complex queries.
    
    The environment variable MNRDFPATH can be used to set where RDF files are
    loaded from by default.  By default, the rdf files are named mr_LANG.owl.
    
    """
    mrbaseurl = 'http://%s:8080/openrdf-sesame/repositories/mr_%s'
    mrbasepath = '/u/metanet/repository/rdf'
    mrfile = {'en':'mr_en.owl',
              'es':'mr_es.owl',
              'ru':'mr_ru.owl',
              'fa':'mr_fa.owl'}
    
    prefixes = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "doc":"https://metaphor.icsi.berkeley.edu/metaphor/DocumentOntology.owl#",
                "dr":"https://metaphor.icsi.berkeley.edu/metaphor/DocumentRepository.owl#",
                "xsd":"http://www.w3.org/2001/XMLSchema#",
                "mo":"https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#",
                "mren":"https://metaphor.icsi.berkeley.edu/en/MetaphorRepository.owl#",
                "mres":"https://metaphor.icsi.berkeley.edu/es/MetaphorRepository.owl#",
                "mrfa":"https://metaphor.icsi.berkeley.edu/fa/MetaphorRepository.owl#",
                "mrru":"https://metaphor.icsi.berkeley.edu/ru/MetaphorRepository.owl#"}
    
    POSmap = {'n': 'N[^=]*',
              'v': 'V[^=]*',
              'a': '(?:J|ADJ)[^=]*',
              'aa': 'R[^=]*',
              'adj': '(?:J|ADJ)[^=]*',
              'adv': 'R[^=]*',
              'prep': '(?:I.|TO|PREP)[^=]*',
              'p': '(?:I.|TO|PREP)[^=]*'}
    
    qstrings = {
    'getlusfromframefamily': """SELECT ?lemma ?frame ?framename WHERE {
        ?frame mo:hasLexicalUnit ?lu .
        ?lu rdf:type mo:LexicalUnit .
        ?lu mo:hasLemma ?lemma .
        ?frame rdf:type mo:Frame .
        ?family rdf:type mo:FrameFamily .
        ?family mo:hasName ?familyname .
        ?frame mo:hasName ?framename .
        {
          ?frame mo:isInFrameFamily ?family .
        } UNION {
          ?subfam rdf:type mo:FrameFamily .
          ?frame mo:isInFrameFamily ?subfam .
          ?subfam mo:isFrameSubfamilyOf+ ?family .
        }
        }""",
    'getlusfromframehierarchy': """SELECT ?lemma ?framename WHERE {
        ?lu rdf:type mo:LexicalUnit .
        ?lu mo:hasLemma ?lemma .
        ?frame rdf:type mo:Frame .
        ?frame mo:hasName ?framename .
        {
          ?frame mo:hasLexicalUnit ?lu .
          ?frame mo:isInFrameFamily ?family .
        } UNION {
          ?subframe rdf:type mo:Frame .
          ?subframe mo:isSubcaseOfFrame+ ?frame .
          ?subframe mo:hasLexicalUnit ?lu .
        }
        }""",
    'getlusfromtargetconcept': """SELECT ?lemma ?frame ?framename ?concepttype WHERE {
        ?lu rdf:type mo:LexicalUnit .
        ?lu mo:hasLemma ?lemma .
        ?frame rdf:type mo:Frame .
        ?frame mo:hasName ?framename .
        ?frame mo:hasLexicalUnit ?lu .
        ?concept rdf:type mo:IARPATargetConcept .
        ?concept mo:hasName ?conceptname .
        ?concept mo:isLinkedToFromFrame ?frame .
        ?concept mo:hasConceptType ?concepttype .
        }""",
    'getlusfromtargetconceptgroup': """SELECT ?lemma ?frame ?framename ?conceptname ?concepttype WHERE {
        ?lu rdf:type mo:LexicalUnit .
        ?lu mo:hasLemma ?lemma .
        ?frame rdf:type mo:Frame .
        ?frame mo:hasName ?framename .
        ?frame mo:hasLexicalUnit ?lu .
        ?concept rdf:type mo:IARPATargetConcept .
        ?concept mo:hasName ?conceptname .
        ?concept mo:isLinkedToFromFrame ?frame .
        ?concept mo:hasConceptGroup ?conceptgroup .
        ?concept mo:hasConceptType ?concepttype .
        }""",
    'getwhitelistlusfromtargetconcept': """SELECT ?lpos ?conceptname ?conceptgroup ?concepttype WHERE {
        ?concept rdf:type mo:IARPATargetConcept .
        ?concept mo:hasWhitelistTargetLU ?lpos .
        ?concept mo:hasName ?conceptname .
        ?concept mo:hasConceptGroup ?conceptgroup .
        ?concept mo:hasConceptType ?concepttype .
        }""",
    'getblacklistlusfromtargetconcept': """SELECT ?lpos ?conceptname ?conceptgroup ?concepttype WHERE {
        ?concept rdf:type mo:IARPATargetConcept .
        ?concept mo:hasBlacklistTargetLU ?lpos .
        ?concept mo:hasName ?conceptname .
        ?concept mo:hasConceptGroup ?conceptgroup .
        ?concept mo:hasConceptType ?concepttype .
        }""",
    'getblacklistsourceframesfromtargetconcept': """SELECT ?frame ?conceptname ?conceptgroup ?concepttype WHERE {
        ?concept rdf:type mo:IARPATargetConcept .
        {
            ?concept mo:hasBlacklistSourceFrame ?frame .
        } UNION {
            ?concept mo:hasBlacklistSourceFrameFamily ?family .
            ?famframe mo:isInFrameFamily ?family .
            ?frame mo:isSubcaseofFrame* ?famframe .
        }
        ?concept mo:hasName ?conceptname .
        ?concept mo:hasConceptGroup ?conceptgroup .
        ?concept mo:hasConceptType ?concepttype .
        }""",
    'getblacklistsourceLUsfromtargetconcept': """SELECT ?lpos ?conceptname ?conceptgroup ?concepttype WHERE {
        ?concept rdf:type mo:IARPATargetConcept .
        ?concept mo:hasBlacklistSourceLU ?lpos .
        ?concept mo:hasName ?conceptname .
        ?concept mo:hasConceptGroup ?conceptgroup .
        ?concept mo:hasConceptType ?concepttype .
    }""",
    'getframesfromlemma':"""SELECT ?frame WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:hasLexicalUnit ?lu .
        ?lu mo:hasLemma ?lemma }""",
    'getdirectcmfromframes':"""SELECT DISTINCT ?cm WHERE {
        ?tframe rdf:type mo:Frame .
        ?sframe rdf:type mo:Frame .
        ?cm mo:hasTargetFrame ?tframe .
        ?cm mo:hasSourceFrame ?sframe .
        }""",
    'getcmsfromsubcase':"""SELECT DISTINCT ?cm WHERE {
        ?tframe rdf:type mo:Frame .
        ?sframe rdf:type mo:Frame .
        ?cm mo:hasTargetFrame ?itframe .
        ?cm mo:hasSourceFrame ?isframe .
        ?tframe mo:isSubCaseOfFrame* ?itframe .
        ?sframe mo:isSubCaseOfFrame* ?isframe .
        }""",
    'getcmsfromframeslocal':"""SELECT DISTINCT ?cm WHERE {
        ?tframe rdf:type mo:Frame .
        ?sframe rdf:type mo:Frame .
        ?cm mo:hasTargetFrame ?tgframe .
        ?cm mo:hasSourceFrame ?isframe .
        ?itframe mo:makesUseOfFrame ?tframe .
        ?itframe mo:isSubcaseOfFrame* ?tgframe .
        ?sframe mo:isSubcaseOfFrame* ?isframe
        }""",
    'getcmsfromframesmed':"""SELECT DISTINCT ?cm WHERE {
        ?tframe rdf:type mo:Frame .
        ?sframe rdf:type mo:Frame .
        ?cm mo:hasTargetFrame ?tgframe .
        ?cm mo:hasSourceFrame ?isframe .
        ?itframe mo:makesUseOfFrame ?iitframe .
        ?tframe mo:isSubcaseOfFrame* ?iitframe .
        ?itframe mo:isSubcaseOfFrame* ?tgframe .
        ?sframe mo:isSubcaseOfFrame* ?isframe
        }""",
    'getcmsfromframeslong':"""SELECT DISTINCT ?cm WHERE {
        ?tframe rdf:type mo:Frame .
        ?sframe rdf:type mo:Frame .
        ?cm mo:hasTargetFrame ?tgframe .
        ?cm mo:hasSourceFrame ?isframe .
        ?itframe mo:makesUseOfFrame ?iitframe .
        ?tframe mo:isSubcaseOfFrame* ?iitframe .
        ?itframe mo:isSubcaseOfFrame* ?tgframe .
        {
            ?sframe mo:isSubcaseOfFrame* ?isframe
        } UNION {
            ?iisframe mo:makesUseOfFrame ?sframe .
            ?iisframe mo:isSubcaseOfFrame* ?isframe .
        }
        }""",
    'getusedcms':"""SELECT DISTINCT ?cm WHERE {
        ?tframe rdf:type mo:Frame .
        ?sframe rdf:type mo:Frame .
        ?cm mo:hasTargetFrame ?tgframe .
        ?cm mo:hasSourceFrame ?isframe .
        ?tframe mo:makesUseOfFrame ?tgframe .
        ?sframe mo:makesUseOfFrame ?isframe .
    }""",
    'getusedcmslocal':"""SELECT DISTINCT ?cm WHERE {
        ?tframe rdf:type mo:Frame .
        ?sframe rdf:type mo:Frame .
        ?cm mo:hasTargetFrame ?tgframe .
        ?cm mo:hasSourceFrame ?isframe .
        ?tframe mo:makesUseOfFrame ?itgframe .
        ?sframe mo:makesUseOfFrame ?iisframe .
        ?itgframe mo:isSubcaseOfFrame* ?tgframe .
        ?iisframe mo:isSubcaseOfFrame* ?isframe .
    }""",
    'getlms':"""SELECT ?lm ?t ?s ?cm WHERE {
        ?lm rdf:type mo:LinguisticMetaphor .
        OPTIONAL { ?lm mo:hasLinguisticTarget ?t } .
        OPTIONAL { ?lm mo:hasLinguisticSource ?s } .
        OPTIONAL { ?lm mo:isInstanceOfMetaphor ?cm } .
        }""",
    'getsentencelms':"""SELECT ?lm ?t ?s ?cm ?sent ?prov WHERE {
        ?lm rdf:type mo:LinguisticMetaphor .
        OPTIONAL { ?lm mo:hasLinguisticTarget ?t } .
        OPTIONAL { ?lm mo:hasLinguisticSource ?s } .
        OPTIONAL { ?lm mo:isInstanceOfMetaphor ?cm } .
        ?lm mo:hasExample ?ex .
        ?ex rdf:type mo:Example .
        ?ex mo:hasSentence ?sent .
        ?ex mo:hasProvenance ?prov .
        }""",
    'getsentences':"""SELECT ?sent ?prov WHERE {
        ?lm mo:hasExample ?ex .
        ?ex rdf:type mo:Example .
        ?ex mo:hasSentence ?sent .
        ?ex mo:hasProvenance ?prov .
        }""",
    'getnumsents':"""SELECT (COUNT(?ex) AS ?count) WHERE {
        ?frame mo:hasExample ?ex .
        ?ex rdf:type mo:Example .
        }""",
    'getframesbylu':"""SELECT ?frame WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:hasLexicalUnit ?lu .
        ?lu rdf:type mo:LexicalUnit .
        ?lu mo:hasLemma ?lustr .
        FILTER regex(?lustr, ?lusearchstr) .
        }""",
    'getlusofframe':"""SELECT ?lemma WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:hasLexicalUnit ?lu .
        ?lu rdf:type mo:LexicalUnit .
        ?lu mo:hasLemma ?lemma .
        }""",
    'getallframes':"""SELECT ?frame WHERE {
        ?frame rdf:type mo:Frame .
        }""",
    'getallsourceconcepts':"""SELECT ?concept ?name ?definition ?owner ?lus WHERE {
        ?concept rdf:type mo:IARPASourceConcept .
        ?concept mo:hasName ?name .
        OPTIONAL { ?concept mo:hasConceptDefinition ?definition . }
        ?concept mo:hasConceptLUs ?lus .
        ?concept mo:hasConceptOwner ?owner .
        }""",
    'getclosestfnframe':"""SELECT ?fnframe WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:correspondsToFrameNet $fnframe .
        }""",
    'getenframename':"""SELECT ?enframename WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:hasEnglishCorrespondent ?enframename .
    }""",
    'getfamiliesofframe':"""SELECT ?family ?name WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:isInFrameFamily ?family .
        ?family rdf:type mo:FrameFamily .
        ?family mo:hasName ?name .
        }""",
    'getallfamiliesofframe':"""SELECT ?family WHERE {
        ?frame rdf:type mo:Frame .
        ?family rdf:type mo:FrameFamily .
        {
          ?frame mo:isInFrameFamily ?family .
        } UNION {
          ?subfam rdf:type mo:FrameFamily .
          ?frame mo:isInFrameFamily ?subfam .
          ?subfam mo:isFrameSubfamilyOf+ ?family .
        }
        }""",
    'getfamilybyenglish':"""SELECT ?family ?name WHERE {
        ?family rdf:type mo:FrameFamily .
        ?family mo:hasName ?name .
        ?family mo:hasEnglishCorrespondent ?enname .
        }""",
    'getenfamilyname':"""SELECT ?enfamilyname WHERE {
        ?family rdf:type mo:FrameFamily .
        ?family mo:hasEnglishCorrespondent ?enfamilyname .
    }""",
    'getifframe1usesframe2':"""SELECT ?frame1 ?frame2 WHERE {
        {
        ?frame1 (mo:makesUseOfFrame|mo:isSubcaseOfFrame) ?frame2 .
        } UNION {
        ?frame1 (mo:makesUseOfFrame|mo:isSubcaseOfFrame)/(mo:makesUseOfFrame|mo:isSubcaseOfFrame) ?frame2 .
        }
        }""",
    'getifframe1usesframe2long':"""SELECT ?frame1 ?frame2 WHERE {
        {
        ?frame1 (mo:makesUseOfFrame|mo:isSubcaseOfFrame)/(mo:makesUseOfFrame|mo:isSubcaseOfFrame)/(mo:makesUseOfFrame|mo:isSubcaseOfFrame) ?frame2 .
        } UNION {
        ?frame1 (mo:makesUseOfFrame|mo:isSubcaseOfFrame)/(mo:makesUseOfFrame|mo:isSubcaseOfFrame)/(mo:makesUseOfFrame|mo:isSubcaseOfFrame)/(mo:makesUseOfFrame|mo:isSubcaseOfFrame) ?frame2 .
        }
        }""",
    'getifimmediateuse':"""SELECT ?frame1 ?frame2 ?otherframe ?othername WHERE {
        ?otherframe mo:makesUseOfFrame ?frame1 .
        ?otherframe mo:makesUseOfFrame ?frame2 .
        ?otherframe mo:hasName ?othername .
    }""",
    'getifcommonsubcase':"""SELECT ?frame1 ?frame2 ?otherframe ?othername WHERE {
        ?otherframe (mo:isSubcaseOfFrame|mo:isSubcaseOfFrame/mo:isSubcaseOfFrame) ?frame1 .
        ?otherframe (mo:isSubcaseOfFrame|mo:isSubcaseOfFrame/mo:isSubcaseOfFrame) ?frame2 .
        ?otherframe mo:hasName ?othername .
    }""",
    'getifframe1roleinframe2':"""SELECT ?frame1 ?frame2 WHERE {
        {
        ?frame2 mo:incorporatesFrameAsRole ?frame1 .
        } UNION {
        ?frame2 mo:isSubcaseOfFrame* ?iframe2 .
        ?iframe2 mo:incorporatesFrameAsRole ?iframe1 .
        ?frame1 mo:isSubcaseOfFrame* ?iframe1 .
        }
    }""",
    'getframesinfamily':"""SELECT ?frame WHERE {
        ?frame mo:isInFrameFamily ?family .
        ?family mo:hasName ?familyname .
        }""",
    'getfamilybyname':"""SELECT ?family WHERE {
        ?family rdf:type mo:FrameFamily .
        ?family mo:hasName ?famname .
    }""",
    'getframebyname':"""SELECT ?frame WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:hasName ?name .
    }""",
    'getframebyenname':"""SELECT ?frame WHERE {
        ?frame rdf:type mo:Frame .
        ?frame mo:hasEnglishCorrespondent ?name .
    }""",
    'gettargetconceptfromframe':"""SELECT ?concept ?conceptname ?framename ?conceptgroup WHERE {
        ?concept rdf:type mo:IARPATargetConcept .
        ?concept mo:isLinkedToFromFrame ?frame .
        ?concept mo:hasName ?conceptname .
        ?frame mo:hasName ?framename .
        ?concept mo:hasConceptGroup ?conceptgroup .
        ?concept mo:hasConceptType ?concepttype .
    }""",
    'gettargetconceptfromwhitelistlu':"""SELECT ?concept ?conceptname ?conceptgroup WHERE {
        ?concept rdf:type mo:IARPATargetConcept .
        ?concept mo:hasName ?conceptname .
        ?concept mo:hasConceptGroup ?conceptgroup .
        ?concept mo:hasConceptType ?concepttype .
        ?concept mo:hasWhitelistTargetLU ?lpos .
    }""",
    'gettaggedframefamily':"""SELECT ?familyname ?family WHERE {
        ?family rdf:type mo:FrameFamily .
        ?frame rdf:type mo:Frame .
        ?frame mo:isInFrameFamily ?family .
        ?family mo:hasName ?familyname .
        ?family mo:hasTag ?tag .
    }""",
    'getcxnpatterns':"""SELECT ?name ?group ?type ?description ?comment ?query WHERE {
        ?cxnpattern rdf:type mo:CxnPattern .
        OPTIONAL { ?cxnpattern rdfs:comment ?comment } .
        ?cxnpattern mo:hasName ?name .
        OPTIONAL { ?cxnpattern mo:isInCxnPGroup ?group } .
        ?cxnpattern mo:hasCxnPType ?type .
        ?cxnpattern mo:hasDescription ?description .
        ?cxnpattern mo:hasQueryCode ?query .
    }""",
    'getmetarcs':"""SELECT ?name ?group ?score ?description ?comment ?query WHERE {
        ?metarc rdf:type mo:RelationalConfiguration .
        OPTIONAL { ?metarc rdfs:comment ?comment } .
        ?metarc mo:hasName ?name .
        OPTIONAL { ?metarc mo:isInRCGroup ?group } .
        ?metarc mo:hasMetaphoricityScore ?score .
        ?metarc mo:hasDescription ?description .
        ?metarc mo:hasQueryCode ?query .
    }"""
    }
    posre = re.compile(ur'\.(a|v|n|p|prep|r|verb|nn|adj|adv|aa)$',flags=re.U|re.I)

    def __init__(self,lang='en',rdffname=None,mrbasedir=None,cachedir=None,
                 verbose=False,force=False,useSE=None,
                 govOnly=False, fndata=None, wikdata=None, pwforms=None):
        """ Initialization method.
        :param lang: language
        :type lang: str
        :param rdffname: path to RDF file
        :type rdffname: str
        :param cachedir: path to directory to create and read cache files from
        :type cachedir: str
        :param verbose: flag to switch on verbose messaging
        :type verbose: bool
        :param force: flag to force regeneration of the cache
        :type force: bool
        :param useSE: domain name or IP address of SPARQL Endpoint
        :type useSE: str
        
        """
        # force will cause cache to regenerate
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing MetaNet Repository instance...')
        self.forcecache = force
        self.lang = lang
        self.govOnly = govOnly
        if 'MNRDFPATH' in os.environ:
            self.mrbasepath = os.environ['MNRDFPATH']
        elif mrbasedir:
            self.mrbasepath = mrbasedir
        if cachedir:
            self.cachedir = cachedir
        else:
            self.cachedir = self.mrbasepath + '/cache'
        self.verbose = verbose
        self.g = Graph()
        self.mo = Namespace("https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#")
        self.mr = Namespace("https://metaphor.icsi.berkeley.edu/%s/MetaphorRepository.owl#"%(lang))
        self.cachef = '%s/cache.metanetrdf-%s' % (self.cachedir,self.lang)
        
        if rdffname is None:
            self.rdffname = '%s/%s'%(self.mrbasepath,self.mrfile[lang])
        else:
            self.rdffname = rdffname
        # Use cache if it exists: speeds up lookups significantly       
        if os.path.exists(self.cachef) and (not self.forcecache):
            self.loadcache()
        else:
            self.logger.info("Loading %s ...",self.rdffname)
            self.g.load(self.rdffname) # this operation is slow
            if not os.path.exists(self.cachedir):
                os.mkdir(self.cachedir)
            self.cacheme()
        self.pre = 'mr'+lang
        self.pref = self.pre + ':'
        self.uriPref = self.prefixes[self.pre]
        if useSE:
            self.tstore = SPARQLWrapper(self.mrbaseurl % (useSE,lang))
            self.tstore.setReturnFormat(JSON)
            self.tstore.setMethod('POST')
            self.regprefs = ['rdf','xsd','mo', self.pre]
            self.heading = u"\n".join([u"PREFIX %s: <%s>"%(pref,self.prefixes[pref]) for pref in self.regprefs])
            self.runNamedSelectQuery = self.runNamedSelectQuerySE
            self.runSelectQuery = self.runSelectQuerySE
            self.getLit = self.getLitSE
        else:
            self.nsdict={"rdf":RDF,"mo":self.mo }
            self.queries = {}
            for q in self.qstrings:
                self.queries[q] = prepareQuery(self.qstrings[q],initNs=self.nsdict)
            self.runNamedSelectQuery = self.runNamedSelectQueryPy
            self.runSelectQuery = self.runSelectQueryPy
            self.getLit = self.getLitPy
        self.fndata = fndata
        self.wikdata = wikdata
        self.pwf = pwforms
    
    def initLookups(self):
        """ Initialize lookup tables which are cached.
        """
        self.lookupscachef = '%s/cache.luframelk-%s' % (self.cachedir,self.lang)
        self.pwf = None
        if os.path.exists(self.lookupscachef) and (not self.forcecache):
            self.loadlooksupscache()
        else:
            self.createLookups()
            if not os.path.exists(self.cachedir):
                os.mkdir(self.cachedir)
            self.cachelookups()
        self.cxnpfname = u'%s/cxn_patterns_%s.txt' % (self.cachedir,self.lang)
        self.metarcfname = u'%s/metarcs_%s.txt' % (self.cachedir,self.lang)
        if ((not os.path.exists(self.cxnpfname)) or
            (os.path.getmtime(self.cxnpfname) < os.path.getmtime(self.rdffname))):
            self.saveCxnPatternsFile()
        else:
            self.logger.info('existing cxn pattern file is newer than rdf')
        if ((not os.path.exists(self.metarcfname)) or
            (os.path.getmtime(self.metarcfname) < os.path.getmtime(self.rdffname))):
            self.saveMetaRCFile()
        else:
            self.logger.info('existing metarc pattern file is newer than rdf')
    
    def getPOS(self,shortpos):
        return self.POSmap[shortpos]
    
    def getLemposRegexp(self,lempos):
        """ if the lempos has no POS, we treat it as a word-form rather than
        as a lemma. """
        if self.posre.search(lempos):
            (lemma,shortpos) = lempos.rsplit(u'.',1)
            form = ur'[\w]+'
            try:
                pos = self.getPOS(shortpos)
            except:
                self.logger.error(u'Error looking up POS on %s',lempos)
                raise
        else:
            form = lempos
            lemma = ur'[\w.-]+'
            pos = ur'[\w&$-]+'
        # parens around the word index for easier retrieval
        return ur'\b%s=%s=%s=(\d+)\b'%(form,lemma,pos)

    def getMWELemposRegexp(self, lempos):
        if u' ' in lempos:
            # if its a MWE, convert each piece separately
            lempospieces = lempos.split()
            npieces = len(lempospieces)
            searchregexp = ur'\s+'.join([self.getLemposRegexp(piece) for piece in lempospieces])
        else:
            searchregexp = self.getLemposRegexp(lempos)
            npieces = 1
        return npieces, searchregexp

    def getLemPos(self, lem, pos):
        """ static method that returns a lempos
        in metanet/framenet format. Note: it doesn't
        handle MWEs
        """
        if pos.startswith(u'N'):
            ext = u'n'
        elif pos.startswith(u'V'):
            ext = u'v'
        elif pos.startswith(u'R') or pos.startswith(u'Adv'):
            ext = u'adv'
        elif pos.startswith(u'A') or pos.startswith(u'J'):
            ext = u'a'
        else:
            ext = u'x'
        return u'%s.%s' % (lem, ext)
    
    def getLemmaFromLemPos(self, lpos):
        parts = lpos.split(u'.')
        if (len(parts) > 1) and (parts[-1] in ('n','a','v','adv','p','x')):
            return u'.'.join(parts[0:-1])
        else:
            return lpos
    
    def fixSourcePOS(self, cxn, pos1, pos2=''):
        """ return best POS tag given two tagger outputs and the cxn """
        if u'S-verb' in cxn:
            if pos1.startswith(u'V'):
                return pos1
            elif pos2.startswith(u'V'):
                return pos2
            else:
                return u'VFX'
        elif u'S-noun' in cxn:
            if pos1.startswith(u'N'):
                return pos1
            elif pos2.startswith(u'N'):
                return pos2
            else:
                return u'NFX'
        else:
            return pos1
        
    def createLookups(self):
        """ lu <> frame lookups
        lu's include lpos as it appears in wiki, and a version with any pos
        extensions stripped.  So 'hold.v back' will be added as is, and also
        as hold back
        """
        self.framelu = {}
        self.framelemma = {} # only has lemmas (and no lpos)
        self.luframe = {}
        # lpos and wordform to MWE lookups
        self.lpos2mwe = {}
        self.wf2mwe = {}
        self.mwere = {}
        # FN only lookups
        self.fn_framelu = {}
        self.fn_luframe = {}

        # concept <> lemmas
        self.sconlemma = {}
        self.sconowner = {}
        self.scondef = {}
        self.lemscon = {}
        # frame > concept and reverse
        self.frameconcept = {}
        self.conceptframe = {}

        self.logger.info("creating concept <> word lookups...")
        sconOwner = None
        if self.govOnly:
            sconOwner = 'GOV'
        for row in self.getSourceConcepts(owner=sconOwner):
            scon = str(row.name)
            self.sconlemma[scon] = set()
            self.sconowner[scon] = str(row.owner)
            try:
                self.scondef[scon] = unicode(row.definition)
            except AttributeError:
                self.logger.warning(u'Source concept %s has no definition',scon)
                
            self.logger.info("processing concept %s, %s",scon,self.sconowner[scon])
            self.logger.info(u"-- has LUs: %s",unicode(row.lus))
            if not row.lus:
                self.logger.info("-- skipping because no lus")
                continue
            for lemma in unicode(row.lus).split(u','):
                lemma = lemma.strip().lower()
                if lemma not in self.lemscon:
                    self.lemscon[lemma] = set()
                self.lemscon[lemma].add(scon)
                self.logger.info("-- added %s -> %s",lemma,scon)
                self.sconlemma[scon].add(lemma)
        
        self.logger.info("creating frame <> LU lookups...")
        
        for row in self.getFrames():
            frame = row.frame
            self.logger.info('processing frame %s',frame)
            #
            # For each frame, get its LUs and create a lookup
            #
            lus = self.getLUsFromFrame(frame)
            self.framelu[frame] = set()
            self.framelemma[frame] = set()
            possible_concepts = set()
            
            for lu in lus:
                # add both the lempos (run.v) and the lemma (run)
                # to the lookup.  Normalise to lower case
                lempos = lu.lemma.toPython().lower()
                self.logger.info("processing lpos %s",lempos)
                if u' ' in lempos:  # its a mwe
                    parts = lempos.split()
                    lemparts = []
                    for part in parts:
                        if self.posre.search(part): # lpos to mwe map
                            if part not in self.lpos2mwe:
                                self.lpos2mwe[part] = set()
                            self.lpos2mwe[part].add(lempos)
                        else:   # wf to mwe map
                            if part not in self.wf2mwe:
                                self.wf2mwe[part] = set()
                            self.wf2mwe[part].add(lempos)
                        # cache the regexp
                        self.mwere[lempos] = self.getMWELemposRegexp(lempos)
                        lempart = self.posre.sub(u'',part)
                        lemparts.append(lempart)
                    lemma = u' '.join(lemparts)
                else:
                    lemma = self.posre.sub(u'',lempos)
                if lempos not in self.luframe:
                    self.luframe[lempos] = set()
                self.luframe[lempos].add(frame)
                self.framelu[frame].add(lempos)
                self.framelemma[frame].add(lemma)
                if lemma != lempos:
                    if lemma not in self.luframe:
                        self.luframe[lemma] = set()
                    self.luframe[lemma].add(frame)
                    self.framelu[frame].add(lemma)
                # check if lemma matches a concept, if so, then collect
                self.logger.info("checking if %s is in self.lemscon",pprint.pformat(lemma))
                if lemma in self.lemscon:
                    self.logger.info('based on lemma %s, adding to pcons: %s',
                                     lemma, pprint.pformat(self.lemscon[lemma]))
                    possible_concepts.update(self.lemscon[lemma])
            
            # evaluate possible concepts to determine mapping
            slemmas = self.framelemma[frame]
            frameConcepts = {}
            for pcon in possible_concepts:
                conlemmas = self.sconlemma[pcon]
                common = conlemmas.intersection(slemmas)
                total = conlemmas.union(slemmas)
                score = float(len(common)) / float(len(total))
                frameConcepts[pcon] = score
                if pcon not in self.conceptframe:
                    self.conceptframe[pcon] = []
                self.conceptframe[pcon].append((self.getNameString(frame),score))
            # list of pcon, score
            self.frameconcept[frame] = sorted(frameConcepts.iteritems(),
                                                key=operator.itemgetter(1),
                                                reverse=True)
            self.logger.info('adding concepts to frame %s:%s',pprint.pformat(frame),
                             pprint.pformat(self.frameconcept[frame]))
        # for concept > frame lookup, do sorting.
        for pcon in self.conceptframe:
            self.conceptframe[pcon].sort(key=operator.itemgetter(1),reverse=True)
                
        #
        # Get the LUs of corresponding FN frames: for FN lu
        #
        if self.fndata:
            for row in self.getFrames():
                frame = row.frame
                self.fn_framelu[frame] = set()
                for fnrow in self.getFNFramesForFrame(frame):
                    fnframe = fnrow.fnframe
                    # add fn lu lemmas to set for frame and to luframe lookup
                    # note that getLUs already returns both lemmas and lempos
                    lemposs = self.fndata.getLUs(fnframe.toPython())
                    self.fn_framelu[frame].update(lemposs)
                    for lpos in lemposs:
                        lem = self.posre.sub(u'',lpos)
                        self.fn_framelu[frame].add(lem)                     
                        if lpos not in self.fn_luframe:
                            self.fn_luframe[lpos] = set()
                        self.fn_luframe[lpos].add(frame)
                        if lem != lpos:
                            if lem not in self.fn_luframe:
                                self.fn_luframe[lem] = set()
                            self.fn_luframe[lem].add(frame)
    
    def lookupFramesFromLU(self,lu):
        """ Given an LU which can be a lemma or a lempos, return the set of possible
        frames that define that LU.  Normalize to lc, and if match is not found,
        try removing pos.
        """
        lempos = lu.lower()
        try:
            return self.luframe[lempos]
        except:
            if u' ' in lempos: #handle MWEs
                lem = u' '.join([self.posre.sub(u'',piece) for piece in lempos.split()])
            else:
                lem = self.posre.sub(u'',lempos)
            if lem == lempos:
                return set()
            try:
                return self.luframe[lem]
            except:
                return set()
        return set()

    def lookupFramesFromFNLU(self,lu):
        """ Lookup frames via the closest FN frame property. Allow for lu being a lempos.
        Normalize to lc, and if match is not found, try removing pos.  Returns a set
        of frames.
        """
        lempos = lu.lower()
        if lempos in self.fn_luframe:
            return self.fn_luframe[lempos]
        else:
            if u' ' in lempos: #handle MWEs
                lem = u' '.join([self.posre.sub(u'',piece) for piece in lempos.split()])
            else:
                lem = self.posre.sub(u'',lempos)
            if (lem != lempos) and (lem in self.fn_luframe):
                return self.fn_luframe[lem]
            return set()

    def lookupLUsFromFrame(self,frame):
        """ Given a frame, return the set of LUs in that frame.
        """
        if frame in self.framelu:
            return self.framelu[frame]
        else:
            return set()
    
    def lookupFNLUsFromFrame(self,frame):
        """ Given a frame, return the set of LUs in the corresponding FrameNet frames.
        """
        if frame in self.fn_framelu:
            return self.fn_framelu[frame]
        else:
            return set()
        
    def cacheme(self):
        f = open(self.cachef,'wb')
        if self.verbose:
            self.logger.info("Caching rdf graph...")
        pickle.dump(self.g,f,2)
        f.close()
        
    def cachelookups(self):
        f2 = open(self.lookupscachef,'wb')
        cachecontent = (self.luframe,
                        self.framelu,
                        self.fn_luframe,
                        self.fn_framelu,
                        self.lpos2mwe,
                        self.wf2mwe,
                        self.mwere,
                        self.framelemma,
                        self.sconlemma,
                        self.lemscon,
                        self.frameconcept,
                        self.conceptframe,
                        self.sconowner,
                        self.scondef)
        pickle.dump(cachecontent,f2,2)
        f2.close()
        
        # sanity check, write out in txt format--if debug logging mode
        if (self.logger.getEffectiveLevel()==logging.DEBUG):
            cacheprint = [{'luframe':self.luframe},
                          {'framelu':self.framelu},
                          {'fn_luframe':self.fn_luframe},
                          {'fn_framelu':self.fn_framelu},
                          {'lpos2mwe':self.lpos2mwe},
                          {'wf2mwe':self.wf2mwe},
                          {'mwere':self.mwere},
                          {'framelemma':self.framelemma},
                          {'sconlemma':self.sconlemma},
                          {'lemscon':self.lemscon},
                          {'frameconcept':self.frameconcept},
                          {'conceptframe':self.conceptframe},
                          {'sconowner':self.sconowner},
                          {'scondef':self.scondef}]
            pfile = codecs.open(self.lookupscachef+'.txt','w',encoding='utf-8')
            pprint.pprint(cacheprint, pfile)
            pfile.close()

    def saveCxnPatternsFile(self):
        fb = []
        self.logger.info(u'Saving cxn patterns to %s', self.cxnpfname)
        for row in self.runNamedSelectQuery('getcxnpatterns'):
            fb.append(u'# =======================================================')
            fb.append(u'# %s (group: %s)' %(row.name, row.group))
            if row.get(u'description'):
                fb.append(u'# '+row.description.replace('\n','\n# '))
            if row.get(u'comment'):
                fb.append(u'# '+row.comment.replace('\n','\n# '))
            fb.append(u'#')
            fb.append(u'START CXN: '+row.name)
            if self.deLitPy(row.type) == 'regexp':
                fb.append(u'REGEXP: '+row.query)
            else:
                fb.append(row.query)
            fb.append(u'END CXN')
            fb.append(u'')
        fh = codecs.open(self.cxnpfname, 'w', encoding='utf-8')
        print >> fh, u'\n'.join(fb)
        fh.close()
    
    def saveMetaRCFile(self):
        fb = []
        self.logger.info(u'Saving meta relational configs to %s', self.metarcfname)
        for row in self.runNamedSelectQuery('getmetarcs'):
            self.logger.info(u'saving metarc with name %s and score %s',row.name,row.score)
            fb.append(u'# =======================================================')
            fb.append(u'# %s (group: %s)' % (row.name, row.group))
            if row.get(u'description'):
                fb.append(u'# '+row.description.replace('\n','\n# '))
            if row.get(u'comment'):
                fb.append(u'# '+row.comment.replace('\n','\n# '))
            fb.append(u'#')
            fb.append(u'START METARC: '+row.name)
            fb.append(u'METAPHORICITY SCORE: '+row.score)
            fb.append(row.query)
            fb.append(u'END METARC')
            fb.append(u'')
        fh = codecs.open(self.metarcfname, 'w', encoding='utf-8')
        print >> fh, u'\n'.join(fb)
        fh.close()
    
    def loadcache(self):
        f = open(self.cachef,'rb')
        self.logger.info("Loading cached rdf graph...")
        self.g = pickle.load(f)
        f.close()
    
    def loadlooksupscache(self):
        f2 = open(self.lookupscachef,'rb')
        self.logger.info("Loading cached LU lookups ...")
        (self.luframe,
         self.framelu,
         self.fn_luframe,
         self.fn_framelu,
         self.lpos2mwe,
         self.wf2mwe,
         self.mwere,
         self.framelemma,
         self.sconlemma,
         self.lemscon,
         self.frameconcept,
         self.conceptframe,
         self.sconowner,
         self.scondef) = pickle.load(f2)
        f2.close()
    
    def getSourceConceptDef(self, scon):
        if scon in self.scondef:
            return self.scondef[scon]
        else:
            self.logger.error(u'Source concept %s has no definition', scon)
            return ""
    
    def getFrames(self):
        """ Returns all frames """
        return self.runNamedSelectQuery('getallframes')
    
    def getSourceConcepts(self,owner=None):
        """ Returns all source concepts: conceptURI, name, lus """
        if owner:
            return self.runNamedSelectQuery('getallsourceconcepts',
                                       bindings={'owner':owner})
        else:
            return self.runNamedSelectQuery('getallsourceconcepts')
    
    def getLUsFromFrame(self,frame):
        """ Returns a list of lemmas given a frame URI """
        return self.runNamedSelectQuery('getlusofframe',bindings={'frame':frame})
    
    def getTargetConceptFromFrame(self, frame, contype):
        """ Returns a list of target concepts (concept, conceptname, framename) from a given frame URI """
        return self.runNamedSelectQuery('gettargetconceptfromframe',bindings={'frame':frame,
                                                                          'concepttype':contype})
    
    def getFNFramesForFrame(self,frame):
        """ Returns a list of framenet frames given a frame URI """
        return self.runNamedSelectQuery('getclosestfnframe',bindings={'frame':frame})
    
    def getFrameFamilies(self,frame):
        """ Returns a list of families for the given frame """
        flist = []
        for family in self.runNamedSelectQuery('getfamiliesofframe',
                                               bindings={'frame':frame}):
            flist.append(self.deLitPy(family.name))
        return flist
        
    def getFrameFamiliesByName(self, famname):
        """ Returns all frame families with the given name """
        return self.runNamedSelectQuery('getfamilybyname',
                                    bindings={'famname':famname})
        
    def getAllFrameFamilies(self,frame):
        """ Returns a list of all families and ancester families for the given frame """
        return self.runNamedSelectQuery('getallfamiliesofframe',
                                   bindings={'frame':frame})
    
    def getNumSentences(self,frame):
        for row in self.runNamedSelectQuery('getnumsents',bindings={'frame':frame}):
            return int(row.count)
        
    def getFramesFromFamily(self,famname):
        slist = []
        for row in self.runNamedSelectQuery('getframesinfamily',
                                       bindings={'familyname':famname}):
            slist.append(row.frame)
        return slist
    
    def getTaggedFrameFamily(self, frame, tag):
        for row in self.runNamedSelectQuery('gettaggedframefamily',
                                       bindings={'frame':frame,
                                                 'tag':tag}):
            return self.deLitPy(row.familyname)
        return ''
    
    def getLUsFromFrameFamily(self,familyname):
        """
        Takes a frame family name and returns a list
        of (lemma(str),frame,framename(str),familyname) tuples.
        """
        lulist = []
        for row in self.runNamedSelectQuery('getlusfromframefamily',bindings={'familyname':familyname}):
            lulist.append((self.deLitPy(row.lemma), row.frame, self.deLitPy(row.framename),
                          familyname,None,None,None))
        return lulist
    
    def getLUsFromFrameHierarchy(self,frame):
        """
        Takes a frame (URIRef) and returns a list
        of (lemma(str),frame,framename(str),None) tuples. (None for familyname)
        """
        lulist = []
        for row in self.runNamedSelectQuery('getlusfromframehierarchy',bindings={'frame':frame}):
            lulist.append((self.deLitPy(row.lemma), frame, self.deLitPy(row.framename),None,
                          None,None,None))
        return lulist
    
    def getLUsFromTargetConceptGroup(self,conceptgroupname):
        """
        Takes a target concept group name and returns a list
        of (lemma(str),frame,framename(str),None,conceptname,concepttype,conceptgroup) tuples.
        """
        lulist = []
        blacklistlus = set()
        for row in self.runNamedSelectQuery('getblacklistlusfromtargetconcept',
                                       bindings={'conceptgroup':conceptgroupname}):
            blacklistlus.add(self.deLitPy(row.lpos))
        for row in self.runNamedSelectQuery('getlusfromtargetconceptgroup',
                                       bindings={'conceptgroup':conceptgroupname}):
            lpos = self.deLitPy(row.lemma)
            if lpos in blacklistlus:
                continue
            lulist.append((lpos, row.frame, self.deLitPy(row.framename),None,
                          self.deLitPy(row.conceptname),self.deLitPy(row.concepttype),
                          conceptgroupname))
        for row in self.runNamedSelectQuery('getwhitelistlusfromtargetconcept',
                                       bindings={'conceptgroup':conceptgroupname}):
            lulist.append((self.deLitPy(row.lpos), None, None, None,
                          self.deLitPy(row.conceptname),self.deLitPy(row.concepttype),
                          conceptgroupname))
        return lulist
    
    def getLUsFromSourceConcept(self,conceptname, maxSecondaryRank=2, minSecondaryScore=0.1):
        """
        Retrieves the words that are directly specified on Source Concepts,
        and LUs that are listed on frames that map to that concept, based
        on the frame to concept mapping system employed by the CNMS.
        """
        luset = set()
        if conceptname in self.conceptframe:
            framelist = []
            framerank = 0
            for frame, mscore in self.conceptframe[conceptname].iteritems():
                framerank += 1
                if framerank == 1:
                    framelist.append(frame)
                    continue
                if framerank > maxSecondaryRank:
                    break
                if mscore < minSecondaryScore:
                    break
                framelist.append(frame)
            for frame in framelist:
                luset.append(self.lookupLUsFromFrame(frame))
        if conceptname in self.sconlemma:
            luset.update(self.sconlemma[conceptname])
        return list(luset)
        
    def getLUsFromTargetConcept(self,conceptname):
        """
        Takes a target concept group name and returns a list
        of (lemma(str),frame,framename(str)) tuples.
        """
        lulist = []
        blacklistlus = set()
        for row in self.runNamedSelectQuery('getblacklistlusfromtargetconcept',
                                       bindings={'conceptname':conceptname}):
            blacklistlus.add(self.deLitPy(row.lpos))
        for row in self.runNamedSelectQuery('getlusfromtargetconcept',
                                       bindings={'conceptname':conceptname}):
            lpos = self.deLitPy(row.lemma)
            if lpos in blacklistlus:
                continue
            lulist.append((lpos, row.frame, self.deLitPy(row.framename),None,
                          conceptname,self.deLitPy(row.concepttype),None))
        for row in self.runNamedSelectQuery('getwhitelistlusfromtargetconcept',
                                       bindings={'conceptname':conceptname}):
            lulist.append((self.deLitPy(row.lpos), None, None, None,
                          conceptname,self.deLitPy(row.concepttype),None))
        return lulist
    
    def getBlacklistSourceFramesFromTargetConcept(self, conceptname=None, conceptgroup=None):
        framelist = []
        vbindings= {}
        if conceptname:
            vbindings['conceptname'] = conceptname
        if conceptgroup:
            vbindings['conceptgroup'] = conceptgroup
        for row in self.runNamedSelectQuery('getblacklistsourceframesfromtargetconcept',
                                       bindings=vbindings):
            framelist.append((row.frame, row.conceptname))
        return framelist
    
    def getBlacklistSourceLUsFromTargetConcept(self, conceptname=None, conceptgroup=None):
        lposlist = []
        vbindings = {}
        if conceptname:
            vbindings['conceptname'] = conceptname
        if conceptgroup:
            vbindings['conceptgroup'] = conceptgroup
        for row in self.runNamedSelectQuery('getblacklistsourceLUsfromtargetconcept',
                                       bindings=vbindings):
            lposlist.append((self.deLitPy(row.lpos), row.conceptname))
        return lposlist
    
    def getTargetConceptFromWhitelistLU(self,lpos):
        for row in self.runNamedSelectQuery('gettargetconceptfromwhitelistlu',
                                       bindings={'lpos':lpos}):
            return self.deLitPy(row.conceptname), self.deLitPy(row.conceptgroup)
        return None, None
    
    def getFramesFromLemma(self,lemma):
        """
        Given a lemma, return a list of frames that have that LU
        """
        #lem = Literal(lemma,datatype=XSD.string)
        #framelist = []
        #for row in self.g.query(self.queries['getframesfromlemma'],initBindings={'lemma':lem}):
        #    framelist.append(row.frame)
        try:
            return list(self.luframe[lemma])
        except:
            return []
    
    def getFramesFromFNLemma(self,lemma):
        """ Given a framenet lempos or lemma, return a list of (metanet) frames
        note that this uses the closestFNFrame relation """
        try:
            return list(self.fn_luframe[lemma])
        except:
            return []
    
    def getCMsFromFrameNames(self, queryname, tframename, sframename):
        tframe = self.getFrameFromName(tframename)
        sframe = self.getFrameFromName(sframename)
        return self.getCMs(queryname, tframe, sframe)
    
    def getCMs(self, queryname, tframe, sframe):
        """
        Given a target frame and a source frame, return CMs
        """
        cmlist = []
        for row in self.runNamedSelectQuery(queryname,bindings={'tframe':tframe,
                                                           'sframe':sframe}):
            cmlist.append(row.cm)
        return cmlist
    
    def getQueryResultList(self, querystr, bindings, resultvars):
        """ Executes the given query with the given bindings and returns the
        results as a list of dicts.  The resultvars list specifies the
        retrieval variables to use as fields for the dict (? should not be included).
        """
        resultlist = []
        for row in self.runSelectQuery(querystr,bindings):
            item = {}
            for field in resultvars:
                item[field] = getattr(row, field)
            resultlist.append(item)
        return resultlist
    
    def getCMs_exp(self,tframe,sframe):
        """
        Given a target frame and a source frame, return CMs
        """
        tframe = str(tframe).replace(self.prefixes[self.pre],self.pref)
        sframe = str(sframe).replace(self.prefixes[self.pre],self.pref)
        qbase = u'%s\n%s BINDINGS ?tframe ?sframe { ( %s %s ) }'
        self.tstore.setQuery(qbase % (self.heading,
                                      'getcmsfromframes',
                                      tframe,
                                      sframe))
        results = self.tstore.query().convert()
        cmlist = []
        for row in results['results']['bindings']:
            cmlist.append(URIRef(row['cm']['value']))
        return cmlist
    
    def getFrameFromName(self,name):
        """ Retrieve a frame with the given name """
        for row in self.runNamedSelectQuery('getframebyname',
                                       bindings={'name':name}):
            return row.frame
        return None

    def getFrameFromEnName(self,name):
        """ Retrieve a frame with the given English corresponding name """
        for row in self.runNamedSelectQuery('getframebyenname',
                                       bindings={'name':name}):
            return row.frame
        return None
    
    def getFromName(self,name):
        """ Retrieve a subject which has a mo:hasName property """
        sname = Literal(name,datatype=XSD.string)
        for s in self.g.subjects(self.mo.hasName,sname):
            return s
        
    def getNameString(self,subj):
        """ Given a subject with a mo:hasName property, return the name
        as a string """
        try:
            return self.getNameLiteral(subj).toPython()
        except:
            self.logger.error(u'subj: %s and nameliteralof %s',pprint.pformat(subj),pprint.pformat(self.getNameLiteral(subj)))
            self.logger.error(traceback.format_exc())
            raise
            
    def getNameLiteral(self,subj):
        """ Given a subject with a mo:hasName property, return the name
        as a Literal """
        for o in self.g.objects(subj,self.mo.hasName):
            return o
    
    def uriStringsToRefs(self,uristrlist):
        """ Given a list of URI strings, return a list of URIRef objects
        based on those strings """
        urilist = []
        for uristr in uristrlist:
            uri = self.uriStringToRef(uristr)
            if uri:
                urilist.append(uri)
        return urilist
    
    def uriStringToRef(self,uristr):
        if isinstance(uristr, URIRef):
            # in some cases it might already be a URIRef
            return uristr
        elif uristr.startswith('http'):
            return URIRef(uristr.strip())
        elif uristr.startswith('*'):
            return None
        self.logger.warn('skipping uri to ref conversion because %s does not start with http.',uristr)
        return None
    
    def getFrameFamiliesFromENC(self,enname):
        """ Given an English frame family name, retrieve the corresponding
        frame family from the repository (of the current language).
        """
        nlist = []
        for row in self.runNamedSelectQuery('getfamilybyenglish',
                                       bindings={'enname':enname}):
            nlist.append(self.deLitPy(row.name))
        return nlist
    
    def getENFrameName(self,frame):
        """ Given a (presumably) non-English frame, retrieve the name of the
        corresponding English wiki frame.  Returns a string.
        :param frame: frame URIRef
        :param type: URIRef
        """
        for row in self.runNamedSelectQuery('getenframename',
                                       bindings={'frame':frame}):
            return self.deLitPy(row.enframename)
        return ''

    def getENFamilyName(self,family):
        """ Given a (presumably) non-English frame family, retrieve the name of the
        corresponding English wiki frame family.  Returns a string.
        :param family: frame family URIRef
        :type family: URIRef
        """
        for row in self.runNamedSelectQuery('getenfamilyname',
                                       bindings={'family':family}):
            return self.deLitPy(row.enfamilyname)
        return ''
        
    def prefixizeURIs(self, uriList):
        return [uri.strip().replace(self.uriPref,self.pref) for uri in uriList]
    
    def urizePref(self, pElem):
        return URIRef(pElem.strip().replace(self.pref,self.uriPref))
    
    def getLitPy(self, raw, rdflibtype=None):
        """ Given a raw value, return a python rdflib Literal of the
        appropriate type
        """
        if rdflibtype:
            return Literal(raw,datatype=rdflibtype)
        else:
            if (type(raw) is str) or (type(raw) is unicode):
                return Literal(raw,datatype=XSD.string)
            if type(raw) is int:
                return Literal(raw,datatype=XSD.integer)
            if type(raw) is bool:
                return Literal(raw,datatype=XSD.boolean)
            if type(raw) is float:
                return Literal(raw,datatype=XSD.float)
        return raw

    def getLitSE(self, raw):
        """ Given a raw value, return a Sparql literal string of the
        appropriate type. """
        if (type(raw) is str) or (type(raw) is unicode):
            return u'"%s"^^xsd:string'%(raw.replace('\\','\\\\').replace('"',ur'\"'))
        if type(raw) is int:
            return u'"%d"^^xsd:integer'%(raw)
        if type(raw) is bool:
            return u'"%s"^^xsd:boolean'%(str(raw).lower())
        if type(raw) is float:
            return u'"%f"^^xsd:float'%(raw)
        return raw
    
    def deLitPy(self, lit):
        """ Convert a rdflib Literal to a python value.  Passes through
        non-Literal inputs. """
        if type(lit)==Literal:
            return lit.toPython()
        else:
            return lit
    
    def deLitSE(self, val, xsdtype=None):
        """ Given a sparql literal string, return the value in the
        appropriate python type."""
        if xsdtype=='xsd:string':
            return val
        if xsdtype=='uri':
            return URIRef(val)
        if xsdtype=='xsd:integer':
            return int(val)
        if xsdtype=='xsd:float':
            return float(val)
        if xsdtype=='xsd:boolean':
            return bool(val)
        return val
    
    def runNamedSelectQueryPy(self,qname,bindings={}):
        """ Run a select sparql query using python rdflib.
        :param qname: name of the query
        :type qname: str
        :param bindings: binding values
        :type bindings: dict
        :returns: results of the query as a row iterator
        """
        # query validation happens here, since within runSelectQueryPy
        # we don't have access to the query string      
        self.validateSelectQuery(self.qstrings[qname])
        return self.runSelectQueryPy(self.queries[qname], bindings)
    
    def runNamedSelectQuerySE(self,qname,bindings={}):
        """ Run a select sparql query using the sparql endpoint
        :param qname: name of the query
        :type qname: str
        :param bindings: binding values
        :type bindings: dict
        :returns: results of the query as a list of rows
        """
        return self.runSelectQuerySE(self.qstrings[qname],bindings)

    def validateSelectQuery(self, qstr):
        if not qstr.lower().startswith('select'):
            raise ValueError(u'Invalid select query: %s' % (qstr))
    
    def runSelectQueryPy(self,querystr,bindings={}):
        """ Run a select sparql query using python rdflib.
        :param querystr: the prepared query object
        :type querystr: query
        :param bindings: binding values
        :type bindings: dict
        :returns: results of the query as a row iterator
        """
        if bindings:
            for key in bindings.keys():
                if type(bindings[key]) not in [URIRef, Literal]:
                    bindings[key] = self.getLitPy(bindings[key])
        return self.g.query(querystr, initBindings=bindings)
    
    def runSelectQuerySE(self,querystr,bindings={}):
        """ Run a select sparql query using the sparql endpoint
        :param querystr: query string
        :type querystr: str
        :param bindings: binding values
        :type bindings: dict
        :returns: results of the query as a list of rows
        """
        self.validateSelectQuery(querystr)
        keylist = []
        vallist = []
        for key, value in bindings.items():
            if type(value)==URIRef:
                value = str(value).replace(self.prefixes[self.pre], self.pref)
            else:
                value = self.getLitSE(value)
            keylist.append(u'?'+key)
            vallist.append(value)
        bindingStr = u'BINDINGS %s { ( %s ) }' % (u' '.join(keylist), u' '.join(vallist))
        qStr = u'%s\n%s %s\n' % (self.heading, querystr, bindingStr)
        self.logger.debug(u'final query=%s',qStr);
        self.tstore.setQuery(qStr)
        try:
            results = self.tstore.query().convert()
        except:
            self.logger.error(u'Error executing query:\n%s\n%s',
                              qStr,traceback.format_exc())
            raise
        self.logger.debug(u'results=%s',pprint.pformat(results))
        rlist = []
        for row in results['results']['bindings']:
            rdata = edict()
            for key, val in row.items():
                rdata[key] = self.deLitSE(val['value'], val['type'])
            rlist.append(rdata)
        return rlist


    
    def doesFrame1UseFrame2(self, frame1, frame2):
        """ given 2 frames, return True is frame 1 is either a subcase of frame 2 or if
        frame 1 makes use of frame 2, where either of those relations may be
        arbitrarily chained up to 1 or 2 links """
        for row in self.runNamedSelectQuery('getifframe1usesframe2',
                                       bindings={'frame1':frame1,
                                                 'frame2':frame2}):
            return True
        return False
    
    def doesFrame1FillRoleInFrame2(self, frame1, frame2):
        """ given 2 frames, return True is frame 1 is incorporated into frame 2
        as a role, or if a ancestor if frame 1 is incorporated into a role of
        an ancestor of frame 2 """
        for row in self.runNamedSelectQuery('getifframe1roleinframe2',
                                       bindings={'frame1':frame1,
                                                 'frame2':frame2}):
            return True
        return False
    
    def doesFrame1UseFrame2long(self, frame1, frame2):
        """ given 2 frames, return True is frame 1 is either a subcase of frame 2 or if
        frame 1 makes use of frame 2, where either of those relations may be
        arbitrarily chained at 3 or 4 links"""
        for row in self.runNamedSelectQuery('getifframe1usesframe2long',
                                       bindings={'frame1':frame1,
                                                 'frame2':frame2}):
            return True
        return False
    
    def frameThatUsesBoth(self, frame1, frame2):
        """ given 2 frames, return True if there is a frame that makes use of
        frame 1 and frame 2."""
        otherframes = []
        for row in self.runNamedSelectQuery('getifimmediateuse',
                                       bindings={'frame1':frame1,
                                                 'frame2':frame2}):
            otherframes.append((row.otherframe, self.deLitPy(row.othername)))
        return otherframes
    
    def frameThatBothAreSubcasesOf(self, frame1, frame2):
        """ given 2 frames, return True if there is a frame that 
        frame 1 and frame 2 are both subcases of with edge distance of 1 or 2."""
        otherframes = []
        for row in self.runNamedSelectQuery('getifcommonsubcase',
                                       bindings={'frame1':frame1,
                                                 'frame2':frame2}):
            otherframes.append((row.otherframe, self.deLitPy(row.othername)))
        return otherframes
    
       
    def getFirstFrameFromLemmas(self, lemmas, pos):
        """ takes a list of lemmas, and a pos, and returns the first
        frame matched as list is iterated in order.  If there
        is a match, it returns the lpos, and the frames that match
        else if no match then returns None, []. """
        for lemma in lemmas:
            if pos:
                lpos = self.getLemPos(lemma.name(),pos)
            else:
                lpos = lemma.name()
            self.logger.debug(u'... searching frames for wn lemma %s', lpos)
            frames = list(self.lookupFramesFromLU(lpos))
            if frames:
                self.logger.debug(u'... found frames %s',pprint.pformat(frames))
                return lpos, frames
        return None,[]

    def _getFNRelScore(self, fnreltype):
        if fnreltype=='lemmas':
            return 0.9
        elif fnreltype=='Inheritance.Parent':
            return 0.8
        elif fnreltype=='Inheritance.Child':
            return 0.7
        elif fnreltype=='sisters':
            return 0.6
        else:
            return 0.25
        
    def getFramesViaFN(self, lemma, pos, reltype="lemmas", depth=1000000):
        """ attempts to use Frames as proxy-- not limited to closest FN frames
        like getFramesFromFNLemma """
        frameHash = {}
        wordscore = {}
        if self.lang != 'en':
            return frameHash, wordscore
        lpos = self.getLemPos(lemma, pos)
        startFrames = self.fndata.getFramesFromLPOS(lpos)
        if reltype=="lemmas":
            frames = startFrames
        elif reltype in ["Inheritance.Child","Inheritance.Parent"]:
            frames = set()
            for fr in startFrames:
                frames.update(self.fndata.getRelatedFrames(fr, reltype))
        elif reltype=="sisters":
            parentframes = set()
            for fr in startFrames:
                parentframes.update(self.fndata.getRelatedFrames(fr, "Inheritance.Child"))
            frames = set()
            for pfr in parentframes:
                siblingFrames = self.fndata.getRelatedFrames(pfr, "Inheritance.Child")
                for sfr in siblingFrames:
                    if sfr not in startFrames:
                        frames.add(sfr)
            
        if not frames:
            return frameHash, wordscore
        flist = list(frames)
        for i in range(min(depth,len(flist))):
            fname = flist[i]
            self.logger.debug('searching for lemmas in frame %s',fname)
            lposlist = self.fndata.getLUsFromFrame(fname)
            for flpos in lposlist:
                if flpos == lpos:
                    continue
                frames = self.getFramesFromLemma(flpos)
                if frames:
                    self.logger.debug('  ... found %s for flpos %s', pprint.pformat(frames), flpos)
                    if flpos not in frameHash:
                        frameHash[flpos] = set(frames)
                    else:
                        frameHash[flpos].update(frames)
                    wordscore[flpos] = self._getFNRelScore(reltype)
        return frameHash, wordscore
    
    def _getWNPOS(self, pos):
        wnpos = None
        if pos.startswith('N'):
            wnpos = wn.NOUN
        elif pos.startswith('V'):
            wnpos = wn.VERB
        elif pos.startswith('J'):
            wnpos = wn.ADJ
        elif pos.startswith('ADJ'):
            wnpos = wn.ADJ
        elif pos.startswith('R'):
            wnpos = wn.ADV
        elif pos.startswith('ADV'):
            wnpos = wn.ADV
        return wnpos
    
    def _getWikPOS(self, pos):
        wpos = None
        if pos.startswith('N'):
            wpos = 'Noun'
        elif pos.startswith('V'):
            wpos = 'Verb'
        elif pos.startswith('J'):
            wpos = 'Adjective'
        elif pos.startswith('ADJ'):
            wpos = 'Adjective'
        elif pos.startswith('R'):
            wpos = 'Adverb'
        elif pos.startswith('ADV'):
            wpos = 'Adverb'
        return wpos
    
    def _getWNRelScore(self, wnreltype):
        if wnreltype=='hypernyms':
            return 0.8
        elif wnreltype=='hyponyms':
            return 0.7
        elif wnreltype=='meronyms':
            return 0.6
        elif wnreltype=='holonyms':
            return 0.6
        elif wnreltype=='sisters':
            return 0.6
        elif wnreltype=='lemmas':
            return 0.9
        
    def getFramesViaWN(self, lemma, pos, wnreltype="lemmas", depth=1000000):
        """ attempts to use WN as a proxy to expand lexical coverage of
        metanet's conceptual network.  Uses synonyms, hypernyms,
        holonyms, meronyms, hyponyms.
        """
        frameHash = {}
        wordscore = {}
        if self.lang != 'en':
            return frameHash, wordscore
        wnpos = self._getWNPOS(pos)
        
        self.logger.debug('looking up wn synsets for %s with pos %s',lemma,pos)
        ssets = wn.synsets(lemma, pos=wnpos)
        self.logger.debug('... synsets found: %s', pprint.pformat(ssets))
        if not ssets:
            return frameHash, wordscore
        
        # check all lemmas of all the synsets
        if wnreltype:
            self.logger.debug('... checking wn %s relations', wnreltype)
        else:
            self.logger.debug('... checking all lemmas')
        for i in range(min(depth,len(ssets))):
            sset = ssets[i]
            wnlemmas = set()
            if wnreltype=='hypernyms':
                for nym in sset.hypernyms():
                    wnlemmas.update(nym.lemmas())
            elif wnreltype=='hyponyms':
                for nym in sset.hyponyms():
                    wnlemmas.update(nym.lemmas())
            elif wnreltype=='meronyms':
                for nym in sset.member_meronyms():
                    wnlemmas.update(nym.lemmas())
            elif wnreltype=='holonyms':
                for nym in sset.member_holonyms():
                    wnlemmas.update(nym.lemmas())
            elif wnreltype=='sisters':
                for nym in sset.hypernyms():
                    for hypon in nym.hyponyms():
                        wnlemmas.update(hypon.lemmas())
            elif wnreltype=='lemmas':
                wnlemmas.update(sset.lemmas())
            else:
                self.logger.error(u'Error: %s is an invalid wn relation type', wnreltype)
                return frameHash, wordscore
            
            self.logger.debug('... ... lemmas retrieved: %s',pprint.pformat(wnlemmas))
            for wnlemma in wnlemmas:
                if wnlemma.name() == lemma:
                    continue
                lpos = self.getLemPos(wnlemma.name(), pos)
                frames = self.getFramesFromLemma(lpos)
                if frames:
                    self.logger.debug('  ... found %s for lemma %s', pprint.pformat(frames), lpos)
                    if lpos not in frameHash:
                        frameHash[lpos] = set(frames)
                    else:
                        frameHash[lpos].update(frames)
                    wordscore[lpos] = self._getWNRelScore(wnreltype)
        return frameHash, wordscore
    
    def _getWikContextScore(self, wcontext):
        if not wcontext:
            return 0.9
        elif wcontext=='obsolete':
            return 0.2
        elif wcontext=='archaic':
            return 0.2
        elif wcontext=='figuratively':
            return 0.2
        elif wcontext=='engineering':
            return 0.5
        elif wcontext=='by extension':
            return 0.6
        else:
            return 0.8
        
    def getFramesViaWik(self, lemma, pos):
        """ attempts to use WN as a proxy to expand lexical coverage of
        metanet's conceptual network.  Uses synonyms, hypernyms,
        holonyms, meronyms, hyponyms.
        """
        frameHash = {}
        wordscore = {}
        if self.lang != 'en':
            return frameHash, wordscore
        wpos = self._getWikPOS(pos)
        self.logger.debug('looking up wiktionary defns for %s with pos %s',lemma,pos)
        wiklemmapos = self.wikdata.getDefWords(lemma, wpos)
        defOrder = -1
        for wiklemma, wikpos, wcontext in wiklemmapos:
            defOrder += 1
            if wiklemma == lemma:
                continue
            lpos = self.getLemPos(wiklemma, wikpos)
            frames = self.getFramesFromLemma(lpos)
            if frames:
                self.logger.debug('  ... found %s for lemma %s', pprint.pformat(frames), lpos)
                if lpos not in frameHash:
                    frameHash[lpos] = set(frames)
                else:
                    frameHash[lpos].update(frames)
                wordscore[lpos] = self._getWikContextScore(wcontext) * (0.9 ** defOrder)
        if not frameHash:
            for wiklemma, wikpos, wcontext in wiklemmapos:
                frames = self.getFramesFromLemma(wiklemma)
                if frames:
                    self.logger.debug('  ... found %s for lemma %s', pprint.pformat(frames), wiklemma)
                    if wiklemma not in frameHash:
                        frameHash[wiklemma] = set(frames)
                    else:
                        frameHash[wiklemma].update(frames)
                    wordscore[wiklemma] = self._getWikContextScore(wcontext)
        return frameHash, wordscore
    
# ======================================================================
# For Testing
# ======================================================================
def main():
    """
    The main method is used for generating the cache as an independent process,
    e.g. to run overnight so as to save on live processing.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate Cache files for MetaNet RDF library",
        epilog="Note: Any existing cache will be overwritten. Note that this will"\
                "also generate a framenet xml cache.")
    parser.add_argument("-l", "--lang",
                        default=None,
                        required=True,
                        help="Language to generate cache for.")
    parser.add_argument("-i", "--inputrdffile",
                        default=None,
                        help="RDF file to use, instead of default")
    parser.add_argument("-c", "--cachedir",
                        default=None,
                        help="Directory to generate cache files (instead of default)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose messages")
    parser.add_argument("-w", "--wordlists", dest="wordlistbase",
                        help="Also generate wordlists of the source concepts. In the format "\
                        "concept word1 word2 ... per line, where concept is a lowercase "\
                        "version of the concept name. This option requires a filename base "\
                        "to be supplied.  Files generated are then suffixed with _lang and"\
                        "created in the cache directory.")
    parser.add_argument("-g","--govonly",action="store_true",
                        help="Retrieve only GOV owned source concepts.")
    cmdline = parser.parse_args()

    # this routine has to write its own files
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if cmdline.verbose:
        deflevel = logging.INFO
    else:
        deflevel = logging.WARN
    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)
    
    mr = MetaNetRepository(cmdline.lang, cmdline.inputrdffile, cachedir=cmdline.cachedir,
                           verbose=True, force=True, govOnly=cmdline.govonly)
    mr.initLookups()
    #
    # Code to write out text files for Katia's mapping system
    #
    if cmdline.wordlistbase:
        fname = u'%s/%s_%s' % (cmdline.cachedir,cmdline.wordlistbase,cmdline.lang)
        if os.path.exists(fname):
            os.rename(fname,fname+'.bak.'+time.strftime("%Y%m%d_%H%M"))
        with codecs.open(fname, 'w', encoding='utf-8') as f:
            for concept, wordset in mr.sconlemma.iteritems():
                line = concept.lower() + u' ' + u' '.join(sorted(list(wordset)))
                print >> f, line
            

if __name__ == '__main__':
    status = main()
    sys.exit(status)
    
