#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: fastdbimport
   :synopsis: module for generating the MetaNet LM database and the GMR more quickly
   
Contains a class for processing JSON output from the LM extractor and generating CSV
data files that can be loaded into the MetNet LM database and the GMR database.  This
is to speed up the creation of these databases.  The program currently assumes that
the databases are empty.  Each language as well as the case study data can be processed
in parallel, due to the primary key id numbers being partitioned into roughly equal
quadrants of the 2G integer space.

.. moduleauthor:: Jisup <jhong@icsi.berkeley.edu>
"""

from peewee import *
from playhouse.proxy import Proxy
import json, re, sys, logging, pprint, traceback, os, codecs, setproctitle, time, jdatetime, datetime
import MySQLdb
from metanetrdf import MetaNetRepository
from mnformats import mnjson
import argparse
from multiprocessing import Pool
from metanetdb import MetaNetLMDB
from gmrdb import GMRDBCase, GMRDBGeneral
from mnrepository.cnmapping import ConceptualNetworkMapper
from mnrepository.fnxml import FrameNet
from mnrepository.wiktionary import Wiktionary
from mnrepository.persianwordforms import PersianWordForms
from rdflib import URIRef
from collections import Counter
from bncdates import BNC_DATES
from mnformats.mnconfig import MetaNetConfigParser
import hashlib, tailer

# default configuration filename
DEFAULT_CONFIGFNAME = '/u/metanet/etc/mnsystem.conf'
CONFIG_ENV = 'MNSYSTEM_CONF'

class FastDBImport:
    """ Version of the database access class that accomplishes faster loading
    of data.  However, we lose the ability to recover from crashes in the middle
    of a file, since the class minimizes integrity checking.
    """
    # divide up the id space between the 4 languages, and the general vs case modes.
    # this to so that each can be processed independently
    idrange = {'general': {'en':{'start':0,
                                 'end':300000000},
                           'es':{'start':500000000,
                                 'end':800000000},
                           'ru':{'start':1000000000,
                                 'end':1300000000},
                           'fa':{'start':1500000000,
                                 'end':1800000000}},
               'case': {'en':{'start':300000000,
                                 'end':500000000},
                           'es':{'start':800000000,
                                 'end':1000000000},
                           'ru':{'start':1300000000,
                                 'end':1500000000},
                           'fa':{'start':1800000000,
                                 'end':2000000000}}
               }
    
    specificExclusions = {'en':['Main government leaders'],
                          'es':[],
                          'ru':[u'Все права защищены .',
                                u'© 2009 все права защищены .',
                                u'ru Все права защищены .',
                                u'Все права защищены и охраняются законом .'],
                          'fa':[]}
    
    # maximum number of duplicate sentences allowed
    maxDupes = 50
    
    # protagonist margin: by which the top progonist must proportionally outrank the second
    protagonistMargin = 0.1
    
    duplicateCounter = Counter()
    
    # note: the order of the tables below is important, the use of references works
    #       such that the tables on the right depend on those on the left
    mntables = ['document', 'sentence', 'LM', 'LM_instance']
    mnuniqtables = ['document', 'sentence', 'LM']
    gmrtables = None
#    gmrgeneraltables = ['lm_sentence', 'lm', 'lm_property', 'lm2cm_source', 'lm2cm_target_general',
#                 'cm','cm2cm_target_general', 'cm_property']
#    gmrcasetables = ['lm_sentence', 'lm', 'lm_property', 'lm2cm_source', 'lm2cm_target_case',
#                     'cm', 'cm2cm_target_case', 'cm_property']
    gmrgeneraltables = ['lm_sentence', 'lm', 'lm_property', 'lm2cm_source', 'lm2cm_target_general',
                 'cm_general', 'cm_general_property']
    gmrcasetables = ['lm_sentence', 'lm', 'lm_property', 'lm2cm_source', 'lm2cm_target_case',
                     'cm_case', 'cm_case_property']
    
    HIGH_METSCORE_MIN = 0.75
    LOW_METSCORE_MAX = 0.5
    HIGH_MAPPING_CONFIDENCE = 0.1
    
    DLS_SCORE_OVERRIDE = 0.5
    DEFAULT_LMS_SCORE = 0.45
    
    CONLOOKUPGROUP = {'POVERTY': 'ECONOMIC_INEQUALITY',
                      'THE_POOR': 'ECONOMIC_INEQUALITY',
                      'WEALTH': 'ECONOMIC_INEQUALITY',
                      'DEBT': 'ECONOMIC_INEQUALITY',
                      'TAXATION': 'ECONOMIC_INEQUALITY',
                      'DEMOCRACY': 'DEMOCRACY',
                      'ELECTIONS': 'DEMOCRACY',
                      'GOVERNMENT': 'GOVERNANCE',
                      'BUREAUCRACY': 'GOVERNANCE',
                      'POLITICS': 'GOVERNANCE',
                      'LEGISLATION': 'GOVERNANCE',
                      'GUNS': 'GUN_OVERSIGHT',
                      'CONTROL_OF_GUNS': 'GUN_OVERSIGHT',
                      'GUN_RIGHTS': 'GUN_OVERSIGHT',
                      'GUN_INDUSTRY': 'GUN_OVERSIGHT'}
    
    def __init__(self, lang, mndb, gmrdb, cnmapper, procdir, cname, docreffield='name',
                 sourceMappingLimit=2,defProtagonist='GENERAL',casemode='general',
                 scoret=0.0,minSecondaryScore=0.2,excludeExtractors=[]):
        """
        Initialization method.
        :param lang: language to process as a 2-letter abbreviation (en, es, etc.)
        :type lang: str
        :param mndb: instance of MetaNet LM database class
        :type mndb: :class:`MetaNetLMDB`
        :param gmrdb: instance of GMR database class
        :type gmrdb: :class:`GMRDB`
        :param cnmapper: instance of Conceptual network mapper class
        :type cnmapper: :class:`ConceptualNetworkMapper`
        :param procdir: directory to create output csv files into
        :type procdir: str
        :param cname: name to use to brand the output files, usu. a datestamp
        :type cname: str
        :param docreffield: field under the document node to use to retrieve unique references.
            This is usually either 'name' (default) or 'provenance'.
        :type docreffield: str
        :param sourceMappingLimit: max number of mappings to include
        :type sourceMappingLimit: int
        :param defProtagonist: default protagonist
        :type defProtagonist: str
        :param casemode: case or general mode
        :type casemode: str
        :param scoret: score threshold for LMs to make it into the GMR
        :type scoret: float
        :param minSecondaryScore: minumum mapping score needed for secondary mappings
        :type minSecondaryScore: float
        :param excludeExtractors: list of extractors to exclude from import
        :type excludeExtractors: list
        """
        self.logger = logging.getLogger(__name__)
        self.mndb = mndb
        self.gmrdb = gmrdb
        self.cnmapper = cnmapper
        self.procdir = procdir
        self.lang = lang
        self.scorethreshold = scoret
        self.logger.info('score threshold is %.4f',scoret)
        self.excludeExtractors = set(excludeExtractors)
        self.minSecondaryScore = minSecondaryScore
        self.gmrlang = lang.upper()
        self.docreffield = docreffield
        self.mndatafnames = {}
        self.mndatafiles = {}
        self.mnidnum = {}
        self.mnrefs = {}
        self.gmrdatafnames = {}
        self.gmrdatafiles = {}
        self.gmridnum = {}
        self.gmrrefs = {}
        self.sourceMappingLimit = sourceMappingLimit
        # ftemplate is prodcir/lang-cname(usually datestamp)-mn/gmr-case/general-tablename
        self.ftemplate = '%s/%s-%s-%s-%s-%s.txt' #name of table data files
        self.defProtagonist = defProtagonist
        self.defProtagonistId = gmrdb.getProtagonistId(defProtagonist)
        self.gmrmode = casemode
        self.gmrmodes = ['general','case']
        if casemode=='case':
            self.casemode=True
            self.gmrtables = self.gmrcasetables
        else:
            self.casemode=False
            self.gmrtables = self.gmrgeneraltables
        # set up filenames and index numbers
        # and ref tables which are used to avoid duplicates
        for table in self.mntables:
            self.mndatafnames[table] = self.ftemplate % (procdir,lang,cname,"mn",self.gmrmode,table)
            self.mnidnum[table] = self.idrange[self.gmrmode][lang]['start']
            self.mnrefs[table] = {}
        for table in self.gmrtables:
            self.gmrdatafnames[table] = self.ftemplate % (procdir,lang,cname,"gmr",self.gmrmode,table)
            self.gmridnum[table] = self.idrange[self.gmrmode][lang]['start']
            self.gmrrefs[table] = {}
        self.mnlmdatafnames = {}
        for table in self.mnuniqtables:
            self.mnlmdatafnames[table] = []
            for gmrmode in self.gmrmodes:
                self.mnlmdatafnames[table].append(self.ftemplate % (procdir,lang,cname,"mn",gmrmode,table))
        self.targetcache = {}
        self.lmcache = {}
        self.gmrdoctypebyid = {}
        self.gmrdocpubdatebyid = {}
        self.gmrdocprotbyid = {}
        self.cmsupportcounter = {}
        self.cmprotlist = {}
        self.protwc = {}
        self.POSre = re.compile(ur'\.([A-Za-z]|adj|adv|aa)$',flags=re.U)
        # pre-seed sentences to exclude as exceeding the dupe count threshhold
        # this is to avoid creating multiple lookups to check
        for exclsent in self.specificExclusions[self.lang]:
            # the minus -1 will allow 1 instance through
            self.duplicateCounter[hashlib.md5(exclsent.encode()).hexdigest()] = self.maxDupes - 1
        self.validconceptgroups = set(self.gmrdb.getConceptGroupNames())
        self.logger.info('Initialized in %s mode.  Valid concept groups: %s',
                         self.gmrmode, u','.join(self.validconceptgroups))
        
    def _addDocDefaults(self, docheader):
        """ Fill out a document header structure with None values as needed.
        :param docheader: document node in the JSON structure
        :type docheader: dict
        """
        if 'corpus' not in docheader:
            docheader['corpus'] = None
        if 'name' not in docheader:
            docheader['name'] = None
        if 'description' not in docheader:
            docheader['description'] = None
        if 'type' not in docheader:
            docheader['type'] = None
        if 'provenance' not in docheader:
            docheader['provenance'] = None
        if 'size' not in docheader:
            docheader['size'] = None
        return docheader
    
    def _getDocType(self, corpus, uri, dtype):
        """ Given corpus name, provenance uri, and document type.  Return
        document type categories as specified by IARPA.
        :param corpus: corpus name
        :type corpus: str
        :param uri: uri or provenance
        :type uri: str
        :param dtype: document type information
        :type dtype: str
        """
        if dtype.startswith('news'):
            return 'NEWSPAPER'
        elif corpus==u'BNC':
            if dtype.startswith(u'W news'):
                return 'NEWSPAPER'
            elif dtype.startswith(u'W ac'):
                return 'MAGAZINE'
            elif dtype.startswith(u'S'):
                return 'TRANSCRIPT'
            else:
                return 'OTHER'
        elif corpus==u'ESGW':
            if (dtype==u'story') or (dtype==u'multi'):
                return 'NEWSPAPER'
            else:
                return 'OTHER'
        elif corpus==u'RUWAC':
            if u'livejournal' in uri:
                return 'SOCIAL_MEDIA'
            else:
                return 'BLOG'
        elif corpus==u'BijanKhan':
            return 'NEWSPAPER'
        elif corpus==u'Hamshahri':
            return 'NEWSPAPER'
        elif corpus==u'ENGW':
            return 'NEWSPAPER'
        else:
            return 'OTHER'
        
    def create_lm_row(self, lmid, lmname, lm, lang):
        """
        Create a tuple representing an lm row in the metanetlm database.
        LMs are uniquely identified by lm['name'], which is shoould consist of
        a predictable amalgam of target, source, and cxn (see :func:`self.getname`).
        The nickname field is used to store a pretty name for display purposes.
        
        :param lmid: primary key id number in the LM table
        :type lmid: int
        :param lmname: unique name of the LM
        :type lmname: str
        :param lm: lm node from the JSON structure
        :type lm: dict
        :param lang: language the LM is from (en, es, etc.)
        :type lang: str
        """
        tframe, sframe, sframefamily = None, None, None
        tconcept, sconcept = None, None
        cxn, score, cms = None, None, None
        if lm['target'].get('framenames'):
            tframe = u','.join(lm['target']['framenames'])
        if lm['source'].get('framenames'):
            sframe = u','.join(lm['source']['framenames'])
        if lm['source'].get('framefamilies'):
            sframefamily = u','.join(lm['source']['framefamilies'])
        if lm['target'].get('concept'):
            tconcept = lm['target']['concept']
        if lm['source'].get('concept'):
            sconcept = lm['source']['concept']
        if lm.get('cxn'):
            cxn = lm['cxn']
        if lm.get('score'):
            score = lm['score']
        metpref = 'https://metaphor.icsi.berkeley.edu/en/MetaphorRepository.owl#Metaphor_'
        if lm.get('cms'):
            cms = u','.join([cm.replace(metpref,'') for cm in lm['cms'][0:2]])
        smappings = []    
        if 'mappings' in lm['source']:
            for mapping in lm['source']['mappings']:
                mstring = u'%s|%s|%s|%.5f|%s' % (mapping['framename'],mapping['family'],mapping['concept'],
                                                 mapping['coreness'],mapping['smapmethod'])
                smappings.append(mstring)
        if (not smappings) and ('allmappings' in lm['source']):
            for mapping in lm['source']['allmappings']:
                mstring = u'%s|%s|%s|%.5f|%s' % (mapping['framename'],mapping['family'],mapping['concept'],
                                                 0.0,mapping['smapmethod'])
                smappings.append(mstring)
        promrcs = []
        if 'promrcs' in lm:
            for promrc in lm['promrcs']:
                prostr = u'%s|%s|%s|%s' % (promrc[u'metarc'],promrc[u'target'],promrc[u'source'],
                                           u','.join(promrc[u'cms']))
                promrcs.append(prostr)
        conmrcs = []
        if 'conmrcs' in lm:
            for conmrc in lm['conmrcs']:
                constr = u'%s|%s|%s' % (conmrc[u'metarc'],conmrc[u'target'],conmrc[u'source'])
                conmrcs.append(constr)
        row = (lmid, lmname, lm['name'],
               lm['target']['lemma'],lm['source']['lemma'],
               tframe,sframe,sframefamily,
               tconcept,sconcept,u';'.join(smappings),
               cxn,cms,None,
               lang,score,u';'.join(promrcs),u';'.join(conmrcs))
        return row
    
    def rowtoline(self, row):
        """
        Converts rows, which are tuples, to a CSV line.  It handles the escaping of
        quotes and the conversion of numbers to strings.
        
        :param row: a row tuple
        :type row: tuple
        """
        rlist = []
        for elem in row:
            if elem == None:
                rlist.append('\\N')
                continue
            if (type(elem) is str) or (type(elem) is unicode):
                if elem:
                    rlist.append(u'"%s"'%(elem.replace(u'\\',u'\\\\').replace(u'"',ur'\"')))
                else:
                    rlist.append('\\N')
                continue
            if (type(elem) is int) or (type(elem) is float) or (type(elem) is long):
                rlist.append(str(elem))
                continue
            raise TypeError('row contains elem %s of type %s. row contains %s' %(pprint.pformat(elem), pprint.pformat(type(elem)), pprint.pformat(row)) )
        return u','.join(rlist)
    
    def generateTableFiles(self, fileIterator):
        """
        Process the JSON files and create the CSV datafiles for both databases.
        Assumes completely empty databases.
        
        :param fileIterator: iterator over JSON input filenames
        :type fileIterator: iterable
        """
        # load the tableid and uniq id fields of the document, sentence, and LM tables into refs dicts.
        # This applies for metanet db and is for all the gmrmodes regardless of which is being
        # processed right now.
        for table in self.mnuniqtables:
            for mnlmfname in self.mnlmdatafnames[table]:
                if os.path.exists(mnlmfname) and (os.path.getsize(mnlmfname) > 0):
                    try:
                        mnlmfile = codecs.open(mnlmfname,encoding='utf-8')
                        for line in mnlmfile:
                            (tableid, idstring) = line.split(u',')[0:2]
                            # need to strip of " marks from lmname
                            self.mnrefs[table][idstring[1:-1]] = int(tableid)
                        mnlmfile.close()
                    except:
                        self.logger.error('Error while reading %s tableid and uniqid from file: %s',table, mnlmfname)
                        raise

        for table in self.mntables:
            tablefname = self.mndatafnames[table]
            if os.path.exists(tablefname) and (os.path.getsize(tablefname) > 0):
                # retrieve last id number
                try:
                    lastline = tailer.tail(codecs.open(tablefname,'rb',encoding='utf-8'), 1)[0]
                    idnum = int(lastline.split(u',')[0])
                    if idnum > self.mnidnum[table]:
                        self.mnidnum[table] = idnum
                    self.mndatafiles[table] = codecs.open(tablefname,'ab',
                                                          encoding='utf-8')
                except:
                    self.logger.error('Error while determining last ID from file %s',tablefname)
                    raise
            else:
                self.mndatafiles[table] = codecs.open(tablefname,'wb',
                                                      encoding='utf-8')
                    
        for table in self.gmrtables:
            tablefname = self.gmrdatafnames[table]
            if os.path.exists(tablefname) and (os.path.getsize(tablefname) > 0):
                # retrieve last id number
                try:
                    lastline = tailer.tail(codecs.open(tablefname,'rb',encoding='utf-8'), 1)[0]
                    idnum = int(lastline.split(u',')[0])
                    if idnum > self.gmridnum[table]:
                        self.gmridnum[table] = idnum
                    self.gmrdatafiles[table] = codecs.open(tablefname,'ab',
                                                           encoding='utf-8')
                except:
                    self.logger.error('Error while determining last ID from file %s',tablefname)
                    raise
            else:
                self.gmrdatafiles[table] = codecs.open(tablefname,'wb',
                                                       encoding='utf-8')
        for jfile in fileIterator:
            fname = jfile.strip()
            self.logger.info('start importing %s', fname)
            try:
                jdata = mnjson.loadfile(fname)
            except:
                self.logger.error('error reading json file %s\n%s',fname,traceback.format_exc())
                continue
            try:
                self.processResultFile(jdata)
            except:
                self.logger.error('error processing result file %s\n%s',fname,traceback.format_exc())
        # create cm table files for GMR; cmtup is (targetid,sourceid)
        for cmtup in sorted(self.cmsupportcounter.keys(),
                            key=lambda x: self.cmsupportcounter[x]):
            if self.cmsupportcounter[cmtup] > 9:
                if self.casemode:
                    cmtable = 'cm_case'
                else:
                    cmtable = 'cm_general'
                self.gmridnum[cmtable] += 1
                cmid = self.gmridnum[cmtable]
                # for each cmtup, cmprotlist is a list of the prototype ids
                protcounter = Counter(self.cmprotlist[cmtup])
                protsum = 0.0
                self.logger.info('Determining protagonist for cm (%s, %s)',
                                 self.gmrdb.getTargetConceptName(cmtup[0]),
                                 self.gmrdb.getSourceConceptName(cmtup[1]))
                mcprotsUS = protcounter.most_common(2) # unscaled
                for protid in protcounter.iterkeys():
                    self.logger.info('scaling count for prot %d: %d / %d', protid, protcounter[protid],self.protwc[protid])
                    protcounter[protid] = protcounter[protid] / float(self.protwc[protid])
                    self.logger.info('scaled value = %f', protcounter[protid])
                    protsum += protcounter[protid]
                mcprots = protcounter.most_common(2) # returns [(protid,fraction),...]
                if mcprots[0][0] != mcprotsUS[0][0]:
                    self.logger.warn('Note: scaling has changed the prot ranking: #1 was %s, but now #1 is %s',
                                     self.gmrdb.getProtagonistName(mcprotsUS[0][0]),
                                     self.gmrdb.getProtagonistName(mcprots[0][0]))
                if len(mcprots) == 1:
                    mcprotid = mcprots[0][0]
                    self.logger.info('only 1 protagonist: %d', mcprotid)
                else:
                    # compare the fraction each occupies in protsum
                    oneprot_perc = mcprots[0][1] / protsum
                    twoprot_perc = mcprots[1][1] / protsum
                    self.logger.info('normalizing 1st prot %s freq %f by protsum %f to get %f',self.gmrdb.getProtagonistName(mcprots[0][0]),mcprots[0][1],protsum,oneprot_perc)
                    self.logger.info('normalizing 2nd prot %s freq %f by protsum %f to get %f',self.gmrdb.getProtagonistName(mcprots[1][0]),mcprots[1][1],protsum,twoprot_perc)
                    if oneprot_perc - twoprot_perc > self.protagonistMargin:
                        mcprotid = mcprots[0][0]
                        self.logger.info('prot %s has scaled freq %f, and beats prot %s with scaled freq %f by more than margin %f',
                                         self.gmrdb.getProtagonistName(mcprots[0][0]), oneprot_perc, self.gmrdb.getProtagonistName(mcprots[1][0]), twoprot_perc, self.protagonistMargin)
                    else:
                        self.logger.info('cm gets general protagonist because of small margin: %f vs %f',
                                         oneprot_perc, twoprot_perc)
                        mcprotid = 1
                #cmrow = (cmid, self.gmrlang, cmtup[1], mcprotid)
                cmrow = (cmid, self.gmrlang, cmtup[0], cmtup[1], mcprotid)
                print >> self.gmrdatafiles[cmtable], self.rowtoline(cmrow)
                #
                # SJD:  join tables deleted in v44 
                #if self.casemode:
                #    jointable = 'cm2cm_target_case'
                #else:
                #    jointable = 'cm2cm_target_general'
                #self.gmridnum[jointable] += 1
                #3cm2cm_target_row = (cmid, cmtup[0])
                #print >> self.gmrdatafiles[jointable], self.rowtoline(cm2cm_target_row)
                sconname = self.gmrdb.getSourceConceptName(cmtup[1])
                self.logger.info('adding cm (%s, %s) with freq %d',
                                 self.gmrdb.getTargetConceptName(cmtup[0]),
                                 sconname,
                                 self.cmsupportcounter[cmtup])
                # add linked frames as properties to the CMs
                # this can later be used to identify which LMs are likely the best
                # representatives of the 
                sframes = self.cnmapper.getSourceFramesFromConcept(sconname, minscore=0.1)
                if self.casemode:
                    propertytable = 'cm_case_property'
                else:
                    propertytable = 'cm_general_property'
                for framename, score in sframes:
                    self.gmridnum[propertytable] += 1
                    cmpropid = self.gmridnum[propertytable]
                    cmproprow = (cmpropid, cmid, 'mappedFrame',framename,score)
                    print >> self.gmrdatafiles[propertytable], self.rowtoline(cmproprow)
            else:
                self.logger.info('not adding cm (%s, %s) with freq %d',
                                 self.gmrdb.getTargetConceptName(cmtup[0]),
                                 self.gmrdb.getSourceConceptName(cmtup[1]),
                                 self.cmsupportcounter[cmtup])
                
    def getname(self, lm):
        """
        Given an LM item, generate a unique name. Should be case
        insensitive because that's now MySQL is.  The name is a
        predictable amalgam of target and source lemma, and the
        construction.
        
        :param lm: lm node from the JSON structure
        :type lm: dict
        """
        try:
            if ('target' not in lm) or ('source' not in lm):
                return None
            if ('lemma' not in lm['target']) or ('lemma' not in lm['source']):
                return None
            if 'cxn' in lm:
                name = u'%s:%s(T=%s,S=%s)' % (self.lang,
                                              lm['cxn'],
                                              lm['target']['lemma'],
                                              lm['source']['lemma'])
            elif ('rel' in lm['target']) and ('rel' in lm['source']):
                name = u'%s:%s-%s(T=%s,S=%s)' % (self.lang,
                                                 lm['target']['rel'],
                                                 lm['source']['rel'],
                                                 lm['target']['lemma'],
                                                 lm['source']['lemma'])
            else:
                name = u'%s:unknown(T=%s,S=%s)' % (self.lang,
                                                   lm['target']['lemma'],
                                                   lm['source']['lemma'])
        except:
            self.logger.error(u'Error generating name of LM')
            raise
        return name.lower()
    
    def getPubDate(self, sentidstr):
        """
        HACK: figure out date based on sentence id string
        BNC-- using a lookup
        ENGW, ENGW, Hamshahri-- parse out the date
        RUWAC, Bijankhan-- we don't know what the pubdate is.
        :param sentidstr: sentence id string
        :type sentidstr: str
        """
        global BNC_DATES
        try:
            if sentidstr.startswith('BNC'): # BNC:A00:2342
                _, docid, _ = sentidstr.split(':',2)
                datestr = None
                if docid in BNC_DATES:
                    datestr = BNC_DATES[docid]
                if datestr:
                    dateparts = datestr.split('-')
                    bmon = 1
                    bday = 1
                    if len(dateparts) == 1:
                        byear = int(dateparts[0])
                    elif len(dateparts) == 2:
                        byear = int(dateparts[0])
                        bmon = int(dateparts[1])
                    elif len(dateparts) == 3:
                        byear = int(dateparts[0])
                        bmon = int(dateparts[1])
                        bday = int(dateparts[2])
                    return datetime.date(year=byear,month=bmon,day=bday).strftime('%Y-%m-%d')
            elif sentidstr.startswith('ENGW'): # ENGW_afp_eng_201402:13432
                docid, sentn = sentidstr.split(':',1)
                _,_,_,dateglob = docid.split('_',3)
                return '%s-%s-01' % (dateglob[0:4],dateglob[4:6])
            elif sentidstr.startswith('ESGW'): # ESGW:XIN_SPA_20101228:34234
                corp, docid, sentn = sentidstr.split(':',2)
                _,_,dateglob = docid.split('_',2)
                return '%s-%s-%s' % (dateglob[0:4],dateglob[4:6],dateglob[6:8])
            elif sentidstr.startswith('HAM2'): # HAM2-801003-001:2344
                _,dateglob,_ = sentidstr.split('-',2)
                pyear = int(dateglob[0:2]) + 1300
                pmon = int(dateglob[2:4])
                pday = int(dateglob[4:6])
                return jdatetime.date(year=pyear,month=pmon,day=pday).strftime('%Y-%m-%d')
        except:
            self.logger.warning('Warning: sentence %s has unreadable date.\n%s',sentidstr,traceback.format_exc())
            return '9999-12-31'
        return '9999-12-31'
    
    def mergeLMs(self, lm1, lm2):
        """
        Takes two LMs that have the same spans as input and returns a single LM.
        :param lm1: first lm
        :type lm1: dict
        :param lm2: second lm
        :type lm2: dict
        """
        lm = {}
        lmfields = set(lm1.keys() + lm2.keys())
        prioritylm = lm1
        secondarylm = lm2
        if str(lm1.get('extractor')).startswith('LMS') or (lm2.get('score') > lm1.get('score')):
            prioritylm = lm2
            secondarylm = lm1
        self.logger.info(u'... LM %s from %s with score %.4f <==> LM %s from %s with score %.4f',
                         prioritylm['name'],prioritylm['extractor'],prioritylm['score'],
                         secondarylm['name'],secondarylm['extractor'],secondarylm['score'])
        for field in lmfields:
            if field in lm1 and (field not in lm2):
                lm[field] = lm1[field]
            elif field in lm2 and (field not in lm1):
                lm[field] = lm2[field]
            elif lm1[field] and (not lm2[field]):
                lm[field] = lm1[field]
            elif lm2[field] and (not lm1[field]):
                lm[field] = lm2[field]
            elif (not lm1[field]) and (not lm2[field]):
                lm[field] = prioritylm[field]
            elif field in ('scorecom','extractor','cxn','seed'):
                lm[field] = prioritylm[field] + u':' + secondarylm[field]
            elif field in ('cms'):
                lm[field] = list(set(lm1[field] + lm2[field]))
            elif field in ('target', 'source'):
                pts = prioritylm[field]
                sts = secondarylm[field]
                ts = {}
                tsfields = set(pts.keys() + sts.keys())
                for tsfield in tsfields:
                    if tsfield in pts and (tsfield not in sts):
                        ts[tsfield] = pts[tsfield]
                    elif tsfield in sts and (tsfield not in pts):
                        ts[tsfield] = sts[tsfield]
                    elif pts[tsfield] and (not sts[tsfield]):
                        ts[tsfield] = pts[tsfield]
                    elif sts[tsfield] and (not pts[tsfield]):
                        ts[tsfield] = sts[tsfield]
                    elif (not pts[tsfield]) and (not sts[tsfield]):
                        ts[tsfield] = pts[tsfield]
                    elif tsfield in ('framenames','frameuris','smapmethods','idxlist'):
                        ts[tsfield] = list(set(pts[tsfield] + sts[tsfield]))
                    elif tsfield in ('conceptraw'):
                        ts[tsfield] = u','.join(list(set((pts[tsfield] + u',' + sts[tsfield]).split(u'u'))))
                    elif tsfield in ('smapmethod'):
                        ts[tsfield] = pts[tsfield] + u':' + sts[tsfield]
                    elif tsfield in ('mappings','allmappings'):
                        mapdict = {}
                        for mapping in pts[tsfield]:
                            mkey = mapping['framename'] + mapping['concept']
                            mapdict[mkey] = mapping
                        for mapping in sts[tsfield]:
                            mkey = mapping['framename'] + mapping['concept']
                            if mkey not in mapdict:
                                mapdict[mkey] = mapping
                        ts[tsfield] = mapdict.values()
                    else:
                        ts[tsfield] = pts[tsfield]
                        if pts[tsfield] != sts[tsfield]:
                            self.logger.warning(u'Warning: LM merge components for %s differ on field %s: %s != %s',
                                                field,tsfield,str(pts[tsfield]),str(sts[tsfield]))
                lm[field] = ts
            elif field == 'score':
                lm[field] = prioritylm[field] + ((1 - prioritylm[field]) * secondarylm[field])
            else:
                lm[field] = prioritylm[field]
                if prioritylm[field] != secondarylm[field]:
                    self.logger.warning(u'Warning: LM merge components for field %s differ: %s != %s',
                                        field,str(prioritylm[field]),str(secondarylm[field]))
        return lm    
    
    def processResultFile(self, jdata):
        """
        Import LMs into the database from the JSON document structure
        using SELECT ... LOAD for performance.  This involves manually tracking
        ID numbers across the tables.
        
        :param jdata: JSON dict containing doc metadata and sentences
        :type jdata: dict
        """
        if 'document' in jdata:
            jdata['documents'] = [jdata['document']]

        # SJD: fix for unbound variable if document is already in DB
        protagonist = self.defProtagonist
        protagonistid = self.defProtagonistId

        # MN DOCUMENTS
        # if document isn't already in the database, plan to insert it by
        # appending to datafile.
        sentCounter = 0
        noLMSentCounter = 0
        if type(jdata['documents'])==dict:
            jdata['documents'] = [jdata['documents']]
        for docheader in jdata['documents']:
            if docheader[self.docreffield] in self.mnrefs['document']:
                continue
            self.mnidnum['document'] += 1
            docheader = self._addDocDefaults(docheader)
            doctype = self._getDocType(docheader['corpus'], docheader['provenance'], docheader['type'])
            self.gmrdoctypebyid[self.mnidnum['document']] = doctype
            pubdate = None
            if 'pubdate' in docheader:
                pubdate = docheader['pubdate']
            self.gmrdocpubdatebyid[self.mnidnum['document']] = pubdate
            if ('perspective' in docheader) and (docheader['perspective'] not in [None,u'',"unknown"]):
                protagonist = docheader['perspective'].upper().replace(u' ',u'_')
                protagonistid = self.gmrdb.getProtagonistId(protagonist)
            else:
                protagonist = self.defProtagonist
                protagonistid = self.defProtagonistId
            self.gmrdocprotbyid[self.mnidnum['document']] = protagonistid
            docrow = (self.mnidnum['document'],
                      docheader[self.docreffield],
                      docheader['corpus'],
                      docheader['name'],
                      docheader['description'],
                      docheader['type'],
                      protagonist,
                      docheader['provenance'],
                      self.lang,
                      docheader['size'])
            print >> self.mndatafiles['document'], self.rowtoline(docrow)
            self.mnrefs['document'][docheader[self.docreffield]] = self.mnidnum['document']
            if protagonistid not in self.protwc:
                self.protwc[protagonistid] = 0        
        
        for sent in jdata['sentences']:
            sentCounter += 1
            mnsentid = None
            gmrsentid = None
            # flags to use to import sentence only once (since multiple lms per sentence)
            sentenceImportedMN = False
            sentenceImportedGMR = False

            # skip sentence if no lms
            if (u'lms' not in sent) or (len(sent[u'lms'])==0):
                noLMSentCounter += 1
                continue

            # if no id, skip
            if not sent['id']:
                self.logger.warning('Skipping sentence because it has no "id":%s',sent[u'text'])
                continue
            
            # keep a count of all the words per protagonist.  This is to normalize
            # lm frequency per perspective
            if 'word' in sent:
                self.protwc[protagonistid] += len(sent['word'])
            elif 'text' in sent:
                self.protwc[protagonistid] += len(sent['text'].split())
                
            # skip duplicate sentences whose count is past the threshhold
            stexthash = hashlib.md5(sent[u'text'].encode()).hexdigest()
            #stexthash = sent[u'text']
            #self.logger.info(u'sentence %s has hash %s',sent[u'text'],stexthash)
            if self.duplicateCounter[stexthash] >= self.maxDupes:
                if self.duplicateCounter[stexthash] == self.maxDupes:
                    self.logger.warn(u'Sentence "%s" is duplicated more than %d times.',
                                     sent[u'text'],self.maxDupes)
                self.duplicateCounter[stexthash] += 1
                continue

            # pre-processing phase to merge LMs found by multiple systems
            lmicache = {}
            for lm in list(sent['lms']):
                # sanity check, if LM name is superlong, skip it
                if len(lm['name']) > 255:
                    self.logger.warn(u'Skipping lm because of name length: %s',lm['name'])
                    sent['lms'].remove(lm)
                    continue
                # this is the unique name for each LM
                lmname = self.getname(lm)
                if not lmname:
                    # no name? skip
                    self.logger.warn(u'Could not construct name for lm:\n%s',pprint.pformat(lm))
                    sent['lms'].remove(lm)
                    continue
                if str(lm.get('extractor'))[0:3] in self.excludeExtractors:
                    self.logger.warn(u'Skipping lm %s because it is from extractor %s',lmname,lm.get('extractor'))
                    sent['lms'].remove(lm)
                    continue
                self.logger.debug(u'pre-processing lm %s in sentence %s',lmname,sent['id'])
                try:
                    spans = '%d-%d' % (lm['source']['start'],lm['source']['end'])
                    spant = '%d-%d' % (lm['target']['start'],lm['target']['end'])
                    spankey = spans + spant
                except TypeError:
                    # skip that LM because it has invalid start/end values
                    self.logger.warn(u'Skipping lm %s because of invalid start/end',lmname)
                    sent['lms'].remove(lm)
                    continue
                if spankey in lmicache:
                    duplm = lmicache[spankey]
                    self.logger.info(u'merging LMs in sentence %s', sent['id'])
                    newlm = self.mergeLMs(duplm, lm)
                    sent['lms'].remove(lm)
                    sent['lms'].remove(duplm)
                    lm = newlm
                    sent['lms'].append(lm)
                    self.logger.info(u'... resulting LM %s from %s with score %.4f',
                                     lm['name'],lm['extractor'],lm['score'])
                    continue
                lmicache[spankey] = lm

            # used to skip duplicate LM instances
            lmicache = set()
            targetconcept = None
            sourceconcepts = []
            for lm in sent['lms']:
                try:
                    # this is the unique name for each LM
                    lmname = self.getname(lm)
                    if not lmname:
                        # no name? skip
                        self.logger.warn('Could not construct name for lm:\n%s',pprint.pformat(lm))
                        continue
                    self.logger.debug('processing lm %s in sentence %s',lmname,sent['id'])
                    try:
                        spans = '%d-%d' % (lm['source']['start'],lm['source']['end'])
                        spant = '%d-%d' % (lm['target']['start'],lm['target']['end'])
                        spankey = spans + spant
                    except TypeError:
                        # skip that LM because it has invalid start/end values
                        self.logger.warn(u'Skipping lm %s because of invalid start/end',lmname)
                        continue
                    if spankey in lmicache:
                        # the same span of the sentence already has an LM defined on it: skip
                        self.logger.warn(u'Skipping lm %s because the same span already has an LM defined',lmname)
                        continue
                    lmicache.add(spankey)
                    
                    # ============================================================================
                    # kludge: temporary, this is a copy of something already in CMS extractor
                    # ============================================================================
                    if (self.lang=='en') and 'cxn' in lm:
                        if lm['cxn'] in ['T-noun_mod_S-noun','T-noun_poss_S-noun',
                                         'T-noun_poss_S-noun.POSseq','S-noun_of_T-noun']:
                            if lm['target']['lemma'].lower() in ['government','state']:
                                if lm['source']['lemma'].lower() in ['building','troop','soldier','militia',
                                                                     'army','house','residence','bond']:
                                    self.logger.debug('downgraded lm %s',lmname)
                                    lm['score'] = 0.2
                                    if 'scorecom' in lm:
                                        lm['scorecom'] += ':pNNexcl'
                                    else:
                                        lm['scorecom'] = 'pNNexcl'
                        elif lm['cxn']=='S-adj_mod_T-noun':
                            if lm['target']['lemma'].lower() in ['gun','weapon','firearm',
                                                                 'pistol','handgun']:
                                if lm['source']['lemma'].lower() in ['illegal','dangerous','illicit',
                                                                     'lawful','legal']:
                                    self.logger.debug('downgraded lm %s',lmname)
                                    lm['score'] = 0.2
                                    if 'scorecom' in lm:
                                        lm['scorecom'] += ':pNNexcl'
                                    else:
                                        lm['scorecom'] = 'pNNexcl'
                            
                    # ==============================================================================
                    # DETERMINE TARGET CONCEPT
                    # ==============================================================================
                    # calculate and cache target and source concepts per lm
                    targetconcept = 'NULL'
                    conceptgroup = None
                    targetframename = None
                    targetconceptid = None
                    
                    if lmname in self.targetcache:
                        # check the cache
                        self.cnmapper.copyTargetConcept(lm['target'],self.targetcache[lmname])
                        # note: it's okay if conceptgroup is None in this case, because if the target concept
                        # is cached, it already exists in the DB
                    else:
                        # not in the cache--probably need to add to DB, this means we
                        # also need to cultural concept
                        self.cnmapper.runTargetMapping(lm)
                        self.targetcache[lmname] = lm['target']
                    if lm['target'].get('concept'):
                        targetconcept = lm['target']['concept']
                    if lm['target'].get('congroup'):
                        conceptgroup = lm['target']['congroup']
                    elif lm['target'].get('cultconcept'):
                        conceptgroup = lm['target']['cultconcept']
                    if lm['target'].get('framename'):
                        targetframename = lm['target']['framename']
                    
                    # ================================================================================
                    # DETERMINE SOURCE CONCEPT
                    # ================================================================================
                    sourceconcepts = []
                    sourceconceptids = []
                    sourceframenames = []

                    if lmname in self.lmcache:
                        self.cnmapper.copySourceConcepts(lm, self.lmcache[lmname])
                    else:
                        self.cnmapper.runSourceMapping(lm,sourceMappingLimit=self.sourceMappingLimit,
                                                       minSecondaryScore=self.minSecondaryScore)
                        self.lmcache[lmname] = lm
                    if lm['source'].get('concept'):
                        sourceconcepts = lm['source']['concept'].split(u',')
                    if lm['source'].get('framenames'):
                        sourceframenames = lm['source']['framenames']

                    # ========================================================================
                    # DETERMINE CONFIDENCE SCORES/VALUES
                    # ========================================================================
                    data = None
                    extractor = None
                    if 'extractor' in lm:
                        extractor = lm['extractor']
                        # if 'extractor' is set, it should have set 'score' itself
                    elif lm.get('seed') == 'NA':                        
                            # Persian LMS extractor is the only one that doesn't set 'extractor' OR score
                            extractor = 'LMS'
                            lm['extractor'] = 'LMS'
                            lm['score'] = self.DEFAULT_LMS_SCORE
                    
                    lmscore = 0.0
                    if 'score' in lm:
                        lmscore = float(lm['score'])
                    
                    # confidence based on LM probability 3.21 GMR
                    #confidence = 'MEDIUM'
                    #if 'score' in lm:
                    #    lmscore = float(lm['score'])
                    #    if lmscore < self.LOW_METSCORE_MAX:
                    #        confidence = 'LOW'
                    #    elif lmscore >= self.HIGH_METSCORE_MIN:
                    #        confidence = 'HIGH'
                    
                    # confidence based on mapping score (based on word overlap)
                    maxmappingscore = 0.0
                    maxmappingframe = ''
                    for scon in sourceconcepts:
                        sconname = scon.split(u':')[0]
                        scon_frames = self.cnmapper.getSourceFramesFromConcept(sconname, minscore=0.0)
                        for scon_framename, mappingscore in scon_frames:
                            if scon_framename in sourceframenames:
                                if mappingscore > maxmappingscore:
                                    maxmappingframe = scon_framename
                                    maxmappingscore = mappingscore
                    confidence = 'MED'
                    if maxmappingscore >= self.HIGH_MAPPING_CONFIDENCE:
                        confidence = 'HIGH'
                    else:
                        confidence = 'LOW'
                    
                    # ===========================================================================
                    # INSERT LM INTO METANETDB
                    # ===========================================================================
                    
                    # insert LM into DB if not already there; note: LM id is reset every time
                    lmid = None
                    if lmname in self.mnrefs['LM']:
                        lmid = self.mnrefs['LM'][lmname]
                    else:
                        self.mnidnum['LM'] += 1
                        lmid = self.mnidnum['LM']
                        self.mnrefs['LM'][lmname] = lmid
                        lmrow = self.create_lm_row(lmid, lmname, lm, self.lang)
                        print >> self.mndatafiles['LM'], self.rowtoline(lmrow)
                        
                    
                    # ============================================================================
                    # INSERT DOCUMENT, SENTENCE, AND LM_INSTANCE INTO METANETDB
                    # ============================================================================
                    docuref = self.mndb.getUrefFromSID(sent[u'id'])
                    try:
                        docid = self.mnrefs['document'][docuref]
                    except:
                        self.logger.error('Document with %s "%s" is not in mnrefs',self.docreffield,docuref)
                        self.logger.error('mnrefs["document"] contains %s',pprint.pformat(self.mnrefs['document']))
                        raise
                    protid = self.gmrdocprotbyid[docid]
                    if not sentenceImportedMN:
                        self.logger.debug('Importing sentence %s', sent['id'])
                        if sent[u'id'] in self.mnrefs['sentence']:
                            mnsentid = self.mnrefs['sentence'][sent[u'id']]
                        else:
                            self.logger.debug('... importing into mndb')
                            self.mnidnum['sentence'] += 1
                            mnsentid = self.mnidnum['sentence']
                            mnsentrow = (mnsentid, sent[u'id'], sent[u'text'], docid)
                            # write to our internal MR
                            print >> self.mndatafiles['sentence'], self.rowtoline(mnsentrow)
                            self.mnrefs['sentence'][sent[u'id']] = mnsentid
                        sentenceImportedMN = True
                    else:
                        self.logger.debug('... sentence %s was already imported into the MNDB',sent['id'])
                       
                    # insert LM_instance into metanetdb
                    self.mnidnum['LM_instance'] += 1
                    mnlmiid = self.mnidnum['LM_instance']
                    lmirow = (mnlmiid, lmid, mnsentid, None,
                              spant, spans, data, None,
                              None, None, extractor)
                    print >> self.mndatafiles['LM_instance'], self.rowtoline(lmirow)
                    
                    # =====================================================================================
                    # DETERMINE GMR CONCEPT IDs
                    # ======================================================================================
                    if targetconcept and (targetconcept != 'NULL'):
                        if not conceptgroup:
                            conceptgroup = self.CONLOOKUPGROUP.get(targetconcept.replace(' ','_'))
                        if conceptgroup and (conceptgroup.replace(' ','_') in self.validconceptgroups):
                            targetconceptid = self.gmrdb.getTargetConceptId(targetconcept,conceptgroup)
                        else:
                            self.logger.warning(u'Warning: concept group %s is not valid.  Skipping LM %s.',
                                                pprint.pformat(conceptgroup),lm[u'name'])
                            continue
                    sourceconceptids = []
                    for scon in sourceconcepts:
                        sconname = scon.split(u':')[0]
                        scondef = self.cnmapper.mr.getSourceConceptDef(sconname)
                        sourceconceptids.append(self.gmrdb.getSourceConceptId(sconname,scondef))
                        
                    # ===============================================================================
                    # INSERT SENTENCE AND LM INTO GMRDB
                    # ===============================================================================
                    if not sentenceImportedGMR:
                        if (targetconceptid and sourceconceptids and (lmscore > self.scorethreshold)):
                            # insert into GMR
                            self.gmridnum['lm_sentence'] += 1
                            gmrsentid =  self.gmridnum['lm_sentence']
                            self.logger.debug('... importing into gmrdb, id=%d',gmrsentid)
                            # HACK: figure out date based on sentence id string, if not in
                            # document header
                            if self.gmrdocpubdatebyid[docid]:
                                pubdate = self.gmrdocpubdatebyid[docid]
                            else:
                                pubdate = self.getPubDate(sent[u'id'])
                            gmrsentrow = (gmrsentid,self.gmrlang,sent[u'text'],sent[u'id'],self.gmrdoctypebyid[docid],pubdate)
                            print >> self.gmrdatafiles['lm_sentence'], self.rowtoline(gmrsentrow)
                            self.gmrrefs['lm_sentence'][sent[u'id']] = gmrsentid
                            sentenceImportedGMR = True
                            # store hash of the sentence text for duplicate checking
                            self.duplicateCounter[stexthash] += 1
                        else:
                            self.logger.debug('... skipping gmrdb import because targetconceptid=%s and sourceconceptid=%s',
                                              pprint.pformat(targetconceptid),pprint.pformat(sourceconceptids))
                    else:
                        self.logger.debug('... sentence %s was already imported into the GMR',sent['id'])
                        
                    # if Target/Source concept mappings are there, insert LM (gmr)
                    if ((gmrsentid != None) and targetconceptid and sourceconceptids and
                            (lmscore > self.scorethreshold)):
                        self.logger.debug('... adding lm %s to dbs',lmname)
                        self.gmridnum['lm'] += 1
                        gmrlmid = self.gmridnum['lm']
                        gmrlmrow = (gmrlmid,self.gmrlang,lm['target']['form'],lm['source']['form'],
                                    lm['source']['lemma'],gmrsentid, protid, mnlmiid)
                        print >> self.gmrdatafiles['lm'], self.rowtoline(gmrlmrow)
    
                        # write to lm2cm_target join table: these tables have no ID field
                        if self.casemode:
                            lm2cmtargettable = 'lm2cm_target_case'
                        else:
                            lm2cmtargettable = 'lm2cm_target_general'
                        self.gmridnum[lm2cmtargettable] += 1
                        lm2cmtargetrow = (gmrlmid,targetconceptid)
                        print >> self.gmrdatafiles[lm2cmtargettable], self.rowtoline(lm2cmtargetrow)
                                     
                        # insert properties for this lm
                        self.gmridnum['lm_property'] += 1
                        lmtproprow = (self.gmridnum['lm_property'],gmrlmid,
                                      'hasMetaScore',str(lmscore),lmscore)
                        print >> self.gmrdatafiles['lm_property'], self.rowtoline(lmtproprow)
                        if (maxmappingframe) and (maxmappingscore > 0.0):
                            self.gmridnum['lm_property'] += 1
                            lmtproprow = (self.gmridnum['lm_property'],gmrlmid,
                                          'hasMappingScore',maxmappingframe,maxmappingscore)
                            print >> self.gmrdatafiles['lm_property'], self.rowtoline(lmtproprow)
                        else:
                            self.logger.warn('LM %s has concept ids, but no mappingframe',lmname)
                            self.logger.debug('---start LM\n%s\n---end LM',pprint.pformat(lm))
                        
                        if targetframename:
                            if sourceframenames:
                                self.gmridnum['lm_property'] += 1
                                lmtproprow = (self.gmridnum['lm_property'],gmrlmid,
                                              'hasTargetFrame',targetframename[:45],None)
                                print >> self.gmrdatafiles['lm_property'], self.rowtoline(lmtproprow)
                                for sourceframename in sourceframenames:
                                    self.gmridnum['lm_property'] += 1
                                    lmsproprow = (self.gmridnum['lm_property'],gmrlmid,
                                                  'hasSourceFrame',sourceframename[:45],None)
                                    print >> self.gmrdatafiles['lm_property'], self.rowtoline(lmsproprow)
                            else:
                                if lm['source'].get('smapmethod') != 'DLS':
                                    self.logger.warn('lm[source] has concept but no frames:\n%s',pprint.pformat(lm['source']))
                        else:
                            self.logger.warn('lm[target] has concept but no frame:\n%s',pprint.pformat(lm['target']))
                        for sconid in sourceconceptids:
                            lmcmrow = (gmrlmid, sconid, confidence)
                            print >> self.gmrdatafiles['lm2cm_source'], self.rowtoline(lmcmrow)
                            # count up the number of LMs
                            if (targetconceptid, sconid) in self.cmsupportcounter:
                                self.cmsupportcounter[(targetconceptid,sconid)] += 1
                            else:
                                self.cmsupportcounter[(targetconceptid,sconid)] = 1
                            if (targetconceptid, sconid) in self.cmprotlist:
                                self.cmprotlist[(targetconceptid, sconid)].append(protid)
                            else:
                                self.cmprotlist[(targetconceptid, sconid)] = [protid]
                    else:
                        self.logger.debug('... skipping lm %s, which has score %s',lmname,str(lmscore))
                        if lmscore > self.scorethreshold:
                            self.logger.debug('... ... gmrsentid=%s',pprint.pformat(gmrsentid))
                            self.logger.debug('... ... targetconceptid=%s',pprint.pformat(targetconceptid))
                            self.logger.debug('... ... sourceconceptids=%s',pprint.pformat(sourceconceptids))
                            self.logger.debug('--- start LM')
                            self.logger.debug(pprint.pformat(lm))
                            self.logger.debug('--- end LM')
                except TypeError:
                    if isinstance(lm['target']['form'], list):
                        self.logger.error('Error: target and/or source form is a list for LM: %s',lm['name'])
                    else:
                        raise
                except:
                    raise
        self.logger.info('... processed %d sentences.  %d had no LMs',sentCounter,noLMSentCounter)
        
    def importTableFiles(self,doDelete=False,gmronly=False,mnonly=False):
        """
        Read the CSV files and import them into the MetaNet LM and GMR databases
        using LOAD DATA INTO queries on a per-table basis.  An option is provided
        allowing for the deletion of just the portion of the tables pertaining to
        the current language being processed.  Note, however, that deleting from
        the tables is extremely slow, and is likely not worth doing, ever.
        
        :param doDelete: specifies whether the tables should first be deleted (the portion
            pertaining to the language being processed)
        :type doDelete: bool
        :param gmronly: flag to import only the gmr table files
        :type gmronly: bool
        :param mnonly: flag to import only the mn table files
        :type mnonly: bool
        """
        if doDelete:
            if not gmronly:
                for table in reversed(self.mntables):
                    self.logger.info('deleting %s part of %s table ...',self.lang,table)
                    self.mndb.deleteData(table,
                                         self.idrange[self.lang]['start']+1,self.idrange[self.lang]['end'])
            if not mnonly:
                for table in reversed(self.gmrtables):
                    self.logger.info('deleting %s part of %s table ...',self.lang,table)
                    self.gmrdb.deleteData(table,
                                          self.idrange[self.lang]['start']+1,self.idrange[self.lang]['end'])
        if not gmronly:
            for table in self.mntables:
                os.chmod(self.mndatafnames[table], 0664)            
                self.logger.info('importing %s', self.mndatafnames[table])
                self.mndb.loadData(self.mndatafnames[table],table)
        if not mnonly:
            for table in self.gmrtables:
                os.chmod(self.gmrdatafnames[table], 0664)
                self.logger.info('importing %s', self.gmrdatafnames[table])
                self.gmrdb.loadData(self.gmrdatafnames[table],table)
     
def main():
    """ Main method to instantiate classes, connect to the databases,
    and run the conversions and imports.  Run the following to see the command
    line options:
    
    fastdbimport -h
    """
    datestring = time.strftime("%Y%m%d")
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Import JSON files containing extracted LMs into MetaNet LM database")
    parser.add_argument('filenamelist',
                        help="Text file containing JSON file(s) to import")
    parser.add_argument('-l','--lang', help="Language of input files.",
                        required=True)
    parser.add_argument('--mdb-user',dest='mdbuser',default='mdbuser',
                        help='MetaNet LM database username')
    parser.add_argument('--mdb-pw',dest='mdbpw',default=None,required=True,
                        help='MetaNet LM database password')
    parser.add_argument('--mdb-name',dest='mdbname',default='metanetlm_'+datestring,
                        help='Metanet LM database name.')
    parser.add_argument('--gdb-user',dest='gdbuser',default='gmruser',
                        help='GMR database username')
    parser.add_argument('--gdb-pw',dest='gdbpw',default=None,required=True,
                        help='GMR database password')
    parser.add_argument('--gdb-name',dest='gdbname',default='icsi_'+datestring,
                        help='GMR database name')
    parser.add_argument('-v','--verbose',action='store_true',
                        help='Display more status messages')
    parser.add_argument('-d','--doc-uref',dest='docreffield',default='name',
                        help='Reference documents by given field.')
    parser.add_argument('-n', '--name', help='Name for this import set.',
                        default=datestring)
    parser.add_argument('--use-se',dest="useSE",default=None,
                        help='SPARQL endpoint for conceptual graph searches')
    parser.add_argument('--proc-dir',dest='procdir',default=os.getcwd(),
                        help='Directory to generate table files in.  Must be'\
                        'a full path.')
    parser.add_argument('--gen-only',action='store_true',dest='genonly',
                        help='Generate table files but don\'t import them.')
    parser.add_argument('--import-only',action='store_true',dest='importonly',
                        help='Import already generated table files. Does not '\
                        'process the input files.')
    parser.add_argument('--delete',help='Delete before importing.',
                        action='store_true')
    parser.add_argument("--disable-fn", dest="disablefn", action="store_true",
                        help="Disable FN extension for frame search (English).")
    parser.add_argument("--source-mapping-limit",dest="mappinglimit",
                        type=int, default=2,
                        help="Max number of frame to concept mappings to "\
                        "insert into database.")
    parser.add_argument("--min-secondary-score",dest="minsecondaryscore",type=float,default=0.2,
                        help="Min score for a secondary concept to be included")
    parser.add_argument('--protagonist',dest="protagonist",
                        help="Default protagonist in cases where protagonist is not"\
                        " specified in the JSON document",
                        default="GENERAL")
    parser.add_argument('--case-mode',dest='casemode',action='store_true',
                        help='Run import in Case Study mode')
    parser.add_argument('-t','--score-threshold',dest='scoret',type=float,
                        help='Score cut-off for LMs')
    parser.add_argument('--gmr-only',dest='gmronly',action='store_true',
                        help='Import GMR table files only.')
    parser.add_argument('--mn-only',dest='mnonly',action='store_true',
                        help='Import MetaNet db table files only.')
    parser.add_argument('--debug',dest='debug',action='store_true',
                        help='Display debug level log info')
    parser.add_argument("--config", dest="configfname",
                        help="Configuration filename to override the default "\
                        " which can also be overridden by environment variable"\
                        " %s (default=%s)" % (CONFIG_ENV,DEFAULT_CONFIGFNAME))
    parser.add_argument("--mode", dest="configmode",
                        help="Used to activate a mode defined in the config file.")
    cmdline = parser.parse_args()

    # this routine has to write its own files
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if cmdline.verbose:
        deflevel = logging.INFO
    else:
        deflevel = logging.WARN
    if cmdline.debug:
        deflevel = logging.DEBUG
    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)

    cfname = None
    if cmdline.configfname:
        cfname = cmdline.configfname
    else:
        cfname = os.environ.get(CONFIG_ENV)
        if not cfname:
            cfname = "./"+os.path.basename(DEFAULT_CONFIGFNAME)
            if not os.path.exists(cfname):
                cfname = DEFAULT_CONFIGFNAME
    logging.info('reading configuration from %s',cfname)
    config = MetaNetConfigParser(cfname,"fastdbimport",cmdline.configmode)
    
    # proc title manipulation to hide PW
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(--gdb-pw|--mdb-pw)(=|\s+)(\S+)',ur'\1\2XXXX',pstr)
    setproctitle.setproctitle(pstr)
        
    mndb = MetaNetLMDB(socket='/tmp/mysql.sock',
                       user=cmdline.mdbuser,
                       passwd=cmdline.mdbpw,
                       dbname=cmdline.mdbname)

    if cmdline.casemode:
        gmrdb = GMRDBCase(socket='/tmp/mysql.sock',
                             user=cmdline.gdbuser,
                             passwd=cmdline.gdbpw,
                             dbname=cmdline.gdbname)
    else:    
        gmrdb = GMRDBGeneral(socket='/tmp/mysql.sock',
                             user=cmdline.gdbuser,
                             passwd=cmdline.gdbpw,
                             dbname=cmdline.gdbname)

    # retrieve priority target concepts, those owned by GOV
    tconlist = config.getListFromComp('cnms','targetconceptranking', lang=cmdline.lang)
    mappinglimit = config.getIntFromComp('cnms','sourcelimit', cmdline.lang,
                                         override=cmdline.mappinglimit,default=2)
    secondaryminscore = config.getFloatFromComp('cnms','secondaryminscore', lang=cmdline.lang,
                                                override=cmdline.mappinglimit,default=0.2)
    scoret = config.getFloat('scorethreshold',lang=cmdline.lang,default=0.4)
    if cmdline.scoret:
        scoret = cmdline.scoret
    excludeExtractors = config.getList('excludeextractors',lang=cmdline.lang)
    casemode = config.getValue('casemode',default='general',lang=cmdline.lang)
    expansionTypes = config.getListFromComp('cnms','expansiontypes',lang=cmdline.lang)
    expansionScoreScale = config.getFloatFromComp('cnms','expansionscorescale',lang=cmdline.lang,
                                                  default=1.0)
    if cmdline.casemode:
        casemode='case'

    mrdatadir = config.getValue('mrdatadir',lang=cmdline.lang)
    disableclosestframe = config.getFlagFromComp('cnms','disableclosestframe',lang=cmdline.lang,
                                                 default=cmdline.disablefn)
    fndatadir = config.getValue('framenetdatadir',lang=cmdline.lang)
    wikdatadir = config.getValue('wiktionarydatadir',lang=cmdline.lang)
    pwfdatadir = config.getValue('persianwordformsdatadir')
        
    fndata = None
    wikdata = None
    pwforms = None
    if cmdline.lang=='en':
        if ('fn' in expansionTypes) or (not disableclosestframe):
            if not fndatadir:
                logging.error('FN expansion requires "framenetdatadir" parameter')
            else:
                fndata = FrameNet(cachedir=fndatadir)
        if ('wik' in expansionTypes):
            if not wikdatadir:
                logging.error('Wiktionary expansion requires "wiktionarydatadir" parameter')
            else:
                wikdata = Wiktionary(dbdir=wikdatadir)
    if cmdline.lang=='fa':
        if not pwfdatadir:
            logging.warn('Persian extraction/mapping not using precomputed word forms.'\
                         ' Set "persianwordformsdatadir" to enable.')
        pwforms = PersianWordForms(pwfdir=pwfdatadir)

    # configure and initialize MetaNet Repository
    metanetrep = MetaNetRepository(cmdline.lang, useSE=cmdline.useSE, mrbasedir=mrdatadir,
                                   fndata=fndata, wikdata=wikdata, pwforms=pwforms)
    metanetrep.initLookups()
    cnmapper = ConceptualNetworkMapper(cmdline.lang, useSE=cmdline.useSE,
                                       targetConceptRank=tconlist,
                                       disableFN=disableclosestframe,
                                       expansionTypes=expansionTypes,
                                       expansionScoreScale=expansionScoreScale,
                                       metanetrep=metanetrep,
                                       conceptMode=casemode)
    
    fdbi = FastDBImport(cmdline.lang, mndb, gmrdb, cnmapper,
                        cmdline.procdir, cmdline.name, cmdline.docreffield,
                        sourceMappingLimit=mappinglimit,
                        defProtagonist=cmdline.protagonist,
                        casemode=casemode,
                        scoret=scoret,
                        minSecondaryScore=secondaryminscore,
                        excludeExtractors=excludeExtractors)
        
    flist = codecs.open(cmdline.filenamelist,encoding='utf-8')
    if not cmdline.importonly:
        fdbi.generateTableFiles(flist)
    if not cmdline.genonly:
        fdbi.importTableFiles(doDelete=cmdline.delete,gmronly=cmdline.gmronly,mnonly=cmdline.mnonly)
    
    
if __name__ == "__main__":
    status = main()
    sys.exit(status)

