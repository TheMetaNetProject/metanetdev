#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: m4detect
   :platform: Unix
   :synopsis: Detects Linguistic Metaphors (LMs) from sentences provided in IARPA XML or MetaNet JSON formats.

Detects Linguistic Metaphors (LMs) from sentences provided in IARPA XML or MetaNet JSON formats for
English, Spanish, Persian, and Russian. It uses the Construction Matching System (CMS, :py:mod:`cmsextractor`)
for all four languages, as well as the Seed-Based System (SBS, :py:mod:`depparsing`) for English, Spanish,
and Russian, and the Language Model System v.2 (LMS2, :py:mod:`lmsextractor2`) for Persian.  The LMS v.1 system
(LMS, :py:mod:`lmsextractor`) can also be run but it deprecated.  The extractor can
be configured to run all or some subset of these systems.  The behavior of the extractor with respect to the
target concepts to search for, as well as the subsystems to use, score thresholds, etc. is specified via 
a configuration file.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
import sys, os, codecs, subprocess, logging, pprint, codecs, traceback
import iarpaxml as ix
from mnpipeline.affectlookup import AffectLookup
from cmsextractor.postextraction import SimpleConstructionMatchingSystem
from mnformats import mnjson
from cmsextractor.cms import ConstructionMatchingSystem
from lmsextractor import externalExtr as externalExtr_v1
from lmsextractor2 import externalExtr as externalExtr_v2
from mnrepository.cnmapping import ConceptualNetworkMapper
from mnrepository.metanetrdf import MetaNetRepository
from mnrepository.fnxml import FrameNet
from mnrepository.wiktionary import Wiktionary
from mnrepository.persianwordforms import PersianWordForms
from multiprocessing import Pool
from source.subdims_matcher import subdim_match
from string import capwords
from depparsing import parsemet
from datetime import datetime
from dateutil.tz import tzlocal

# TODO: perhaps remove this
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

# for parallel processing
CHUNKSIZE = 1

    
def clearLMs(sentences):
    """ Clear existing LMs from the input file.  This is used when running the extractor on
    the output of a previous run.
    """
    for sent in sentences:
        if 'lms' in sent:
            del sent['lms']

def runLMS(cmdline, jdata):
    """Run the (Persian) Language Model System (LMS) extractor.  This is now deprecated.
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:mod:argparse)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :returns: JSON dict with LMs added
    
    """
    pme = externalExtr_v1.PersianMetaphorExtractor()
    pme.parse(jdata)
    return pme.find_LMs(jdata)

def runLMS2(cmdline, jdata):
    """Run the (Persian) Language Model System (LMS) Version 2 extractor.
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:mod:argparse)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :returns: JSON dict with LMs added
    
    """
    pme = externalExtr_v2.PersianMetaphorExtractor()
    return pme.find_LMs(jdata)

def runSCMS(cmdline, jdata, logger):
    """Run the Simple Construction Matching System (SCMS) extractor.  Now deprecated.
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:mod:argparse)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :param logger: instance of IARPA logger class
    :type logger: :class:IARPALogger
    :returns: JSON dict with LMs added
    
    """
    # run Simple CMS
    cms = SimpleConstructionMatchingSystem(cmdline.extdir, verbose=cmdline.verbose)
    cms.post_process(jdata, logger)
    return jdata

def runCMSGenWCacheOnly(cmdline, jdata, metanetrep, cnmapper,
                        tfamlist=[], tsnamelist=[], tconlist=[], tcongrouplist=[],
                        sfamlist=[], ssnamelist=[], sconlist=[]):
    """Run the search word retrieval for Construction Matching System (CMS)
    extractor, create a cache file, and then quit. This is used to pre-process
    search word caching prior to parallelized extraction runs.
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:py:mod:`argparse`)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :param famlist: target frame families to extract LMs for
    :type famlist: list 
    """
    lang = jdata['lang']
    cms = ConstructionMatchingSystem(lang, posfield=cmdline.pos, lemfield=cmdline.lem,
                                     useSE=cmdline.useSE, metanetrep=metanetrep,
                                     forcecache=cmdline.forcecache, cnmapper=cnmapper,
                                     engine=cmdline.engine, nodepcheck=cmdline.nodepcheck)
    cms.setWCacheOnlyRun(True)        
    cms.runCMS(jdata['sentences'],
               tfamlist,
               tsnamelist,
               tconlist,
               tcongrouplist,               
               sfamlist,
               ssnamelist,
               sconlist,
               cxnlist=cmdline.cxns,
               doallcxns=cmdline.allcxns,
               forcePOScomp=cmdline.forcepos,
               translateEn=cmdline.translateEn)

def runCMS(cmdline, config, jdata, metanetrep, cnmapper,
           tfamlist=[], tsnamelist=[], tconlist=[], tcongrouplist=[],
           sfamlist=[], ssnamelist=[], sconlist=[], paramrec={}):
    """Run the Construction Matching System (CMS) extractor.
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:py:mod:`argparse`)
    :param config: configuration file parameters
    :type config: instance of (:py:mod:`mnformats.mnconfig.MetaNetConfigParser`)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :param metanetrep: MetaNet repository instance
    :type metanetrep: :py:class:`mnrepository.metanetrdf.MetaNetRepository`
    :param cnmapper: Conceptual Network Mapper instance
    :type cnmapper: :py:class:`mnrepository.cnmapping.ConceptualNetworkMapper`
    :param tfamlist: target frame families to extract LMs for
    :type tfamlist: list 
    :param tsnamelist: target frame list
    :type tsnamelist: list
    :param tcongrouplist: list of target concept groups
    :type tcongrouplist: list
    :param tconlist: list of target concepts
    :type tconlist: list
    :returns: JSON dict with LMs added
    
    """
    lang = jdata['lang']
    excludedfamilies = config.getListFromComp('cms','excludedfamilies', lang)
    metarcfname = config.getValueFromComp('cms','metarcfile',lang)
    
    cms = ConstructionMatchingSystem(lang, posfield=cmdline.pos, lemfield=cmdline.lem,
                                     useSE=cmdline.useSE,
                                     forcecache=cmdline.forcecache,
                                     engine=cmdline.engine, nodepcheck=cmdline.nodepcheck,
                                     excludedFamilies=excludedfamilies,
                                     metanetrep=metanetrep,cnmapper=cnmapper,
                                     metarcfname=metarcfname)
 
    maxsentlength = config.getValueFromComp('cms','maxsentlength', lang)
    if maxsentlength:
        cms.setMaxSentenceLength(int(maxsentlength))
    minsentlength = config.getValueFromComp('cms','minsentlength', lang)
    if minsentlength:
        cms.setMinSentenceLength(int(minsentlength))
    disablewcache = config.getValueFromComp('cms','disablewcaching', lang)
    if disablewcache and (disablewcache.lower() == 'true'):
        cms.setSearchWordCaching(False)
    cxnpatternfname = config.getValueFromComp('cms','cxnpatternfile',lang)
    cmsparams = {}
    cmsparams['excludedfamilies'] = excludedfamilies
    cmsparams['metarcfile'] = metarcfname
    cmsparams['maxsentlength'] = maxsentlength
    cmsparams['disablewcaching'] = disablewcache
    cmsparams['cxnpatternfile'] = cxnpatternfname
    paramrec['cms'] = cmsparams
    
    # output mode is either 'all' or 'onlylms'.  In the latter mode, the output
    # JSON does not contain sentences.
    outputmode = config.getValue('outputmode',default='all')
    paramrec['outputmode'] = outputmode
    
    if outputmode=='onlylms':
        if 'lmlist' not in jdata:
            jdata['lmlist'] = []
        cms.setAggregateLMs(jdata['lmlist'])
    
    cms.runCMS(jdata['sentences'],
               tfamlist,
               tsnamelist,
               tconlist,
               tcongrouplist,
               sfamlist,
               ssnamelist,
               sconlist,
               cxnlist=cmdline.cxns,
               cxnfname=cxnpatternfname,
               doallcxns=cmdline.allcxns,
               forcePOScomp=cmdline.forcepos,
               translateEn=cmdline.translateEn)
    return jdata

class DepParseFound(Exception):
    def __init__(self, value=''):
        self.value = value
    def __str__(self):
        return repr(self.value)

def runSBS(cmdline, config, jdata, paramrec={}):

    lang = jdata[u'lang']
    options = config.getComponentOptions('sbs')
    seed_fn = config.getValueFromComp('sbs','seed_fn',lang,required=True)
    sbsparams={}
    sbsparams['seed_fn'] = seed_fn
    # delete seed_fn entries in options
    for optkey in options.keys():
        if (optkey == 'seed_fn') or (optkey.startswith('seed_fn.')):
            del options[optkey]
        else:
            sbsparams[optkey] = options[optkey]
    paramrec['sbs'] = sbsparams
    
    # run CMS dep parser if needed
    if cmdline.nodepcheck:
        runParser = False
    else:
        runParser = True
        if u'invoke_parser' in options:
            runParser = config.getFlagFromComp('sbs','invoke_parser',lang,required=True)
        else:
            try:
                sentLimit = min(3,len(jdata[u'sentences']))
                for sent in jdata[u'sentences'][0:sentLimit]:
                    if u'word' not in sent:
                        continue
                    wLimit = min(5,len(jdata[u'sentences'][0][u'word']))
                    for w in jdata[u'sentences'][0][u'word'][0:wLimit]:
                        if u'dep' in w:
                            raise DepParseFound()
            except DepParseFound:
                runParser = False
            except:
                logging.error('Error while determining whether to invoke dep parser')
                raise
        
    if runParser:
        ConstructionMatchingSystem.preProcess(lang, jdata['sentences'],
                                              pfield=cmdline.pos,lfield=cmdline.lem)
    
    # never have the SBS run dep parsing directly    
    options[u'invoke_parser'] = False
    json_out = parsemet.m4detect(lang, jdata, seed_fn,
                                 **options)
    # sentence post processing: mark which extractor and set a score
    # since SBS itself does not give us a score
    for sent in json_out['sentences']:
        if 'lms' in sent:
            for lm in sent['lms']:
                # set extractor field
                if 'extractor' not in lm:
                    lm['extractor'] = 'SBS'
                elif lm['extractor'] != 'SBS':
                    # so that we don't touch LMs that were found by other systems
                    continue
                seedN, seedV = lm['seed'].split(u' ',1)
                if (lm['target']['lpos']==seedN) and (lm['source']['lpos']==seedV):
                    # its an exact seed match
                    lm['score'] = 1.0
                    lm['seedmatch'] = 1
                elif 'score' not in lm:
                    # Default to Shutova 2010's estimate for precision
                    lm['score'] = 0.79
            if cmdline.noseedmatches:
                newlms = []
                for lm in sent['lms']:
                    if 'seedmatch' in lm:
                        continue
                    newlms.append(lm)
                sent['lms'] = newlms
                
                
    return json_out                    

def runPRE(cmdline, jdata):
    """Run the preprocessing steps of the Construction Matching System (CMS) extractor
    (separately from the extractor).
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:py:mod:`argparse`)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :returns: JSON dict with LMs added
    
    """
    lang = jdata['lang']
    ConstructionMatchingSystem.preProcess(lang, jdata['sentences'],
                                          pfield=cmdline.pos,lfield=cmdline.lem)
    logging.info('preprocessing returned %d sentences', len(jdata['sentences']))
    return jdata

def runCNMS(cmdline, config, jdata, cnmapper):
    """Run the Conceptual Network Mapping System (CNMS), which maps LMs to
        IARPA target and source concepts and dimentions.
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:mod:argparse)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :returns: JSON dict with concepts specified
    
    """
    # conceptual network mapping system 
    logging.info('Starting mapping to concepts ...')
    lang = jdata['lang']
        
    for sent in jdata['sentences']:
        if 'lms' not in sent:
            continue
        for lm in sent['lms']:
            applyCNMS = False
            try:
                if cnmapper.runTargetMapping(lm):
                    applyCNMS = True
            except:
                logging.warn('Failed to find concept for lm target: %s',
                             pprint.pformat(lm['target'].get('lemma')))
                logging.error('Error: %s', traceback.format_exc())
            try:
                if cnmapper.runSourceMapping(lm):
                    applyCNMS = True
            except:
                logging.warn('Failed to find concept for lm source: %s', pprint.pformat(lm['source'].get('lemma')))
                logging.error('Error: %s', traceback.format_exc())
            if applyCNMS:
                lm['extractor'] += ':CNMS'
    logging.info('Done mapping')
    return jdata

def runDIS(cmdline, jdata):
    """Run the Dimension Identification System (DIS), which when given
    an LM with target and source concepts, identifies the source
    dimension.
    
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:mod:argparse)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :returns: JSON dict with source dimensions specified
    
    """
    # Dario's source-dimension finder: Dimension Identification System
    _lang = {'en': 'english', 'ru': 'russian', 'es': 'spanish'}
    if jdata['lang'] in _lang:
        lang = _lang[jdata['lang']]
    else:
        return jdata
    logging.info('Starting dimension identification ...')
    for sent in jdata['sentences']:
        if 'lms' not in sent:
            continue
        for lm in sent['lms']:
            try:
                source = lm['source']
                if ('concept' not in source) or (source['concept'] == 'NULL'):
                    continue
                ((_, dim, sdim), confident) = subdim_match(lang,
                                                           source['lemma'],
                                                           lm['target']['lemma'],
                                                           source['concept'].lower()) 
                sd_pair = u'%s.%s' % (dim.upper(), capwords(sdim, '_'))
                if confident:
                    source['dimension.bak'] = source['dimension']
                    source['dimension'] = sd_pair
                    lm['extractor'] += ':DIS'
            except KeyError:
                pass
            except:
                logging.error('Error: %s', traceback.format_exc())
                pass
    logging.info('Done dimension identification')
    return jdata

def runLMDetectionInstance((infilename, outfilename, cmdline, config)):
    """Run single instance of LM detection on one input JSON file.
    This method takes a single tuple argument and is intended to be
    run via :py:mod:`multiprocessing`.
    
    :param infilename: input file name
    :type infilename: str
    :param outfilename: output file name
    :type outfilename: str
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:py:mod:`argparse`)
    
    """
    if os.path.exists(outfilename) and (not cmdline.force):
        logging.info("Skipping %s because result file exists.", infilename)
        return

    # read input file and prep settings
    logging.info('start LM detection on %s', infilename)

    if cmdline.verbose:
        msgformat = u'%(asctime)-15s - '+os.path.basename(infilename)+' - %(message)s'
        dateformat = u'%Y-%m-%dT%H:%M:%SZ'
        lfmt = logging.Formatter(msgformat, dateformat)
        
        # root logger: remove and re-add handlers
        rlogger = logging.getLogger()
        for h in list(rlogger.handlers):
            rlogger.removeHandler(h)
        
        # info handler: screen (stderr)
        infohand = logging.StreamHandler()
        infohand.setFormatter(lfmt)

        infohand.setLevel(logging.INFO)
        rlogger.setLevel(logging.INFO)
        
        # debug handler: to file
        if cmdline.debug:
            dbglogfname = os.path.basename(infilename) + '.debug.log'
            debughand = logging.FileHandler(dbglogfname,
                                            mode='w',
                                            encoding='utf-8')
            debughand.setLevel(logging.DEBUG)
            debughand.setFormatter(lfmt)    
            rlogger.addHandler(debughand)
            rlogger.setLevel(logging.DEBUG)
        rlogger.addHandler(infohand)
    
    jdata = mnjson.loadfile(infilename)
    
    logger = None
    jdata = runLMDetection(jdata, cmdline, config, logger)
    if not jdata:
        logging.error('LMDetection returned empty {}')
        raise
    
    # write output file
    mnjson.writefile(outfilename, jdata)
    logging.info('done LM detection')

def runLMDetection(jdata, cmdline, config, logger):
    jdata['start_processing_time'] = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S %z")
    lang = jdata['lang']
    
    if cmdline.clearLMs:
        logging.info('clearing out existing lms ...')
        clearLMs(jdata['sentences'])
    
    paramrec = {}
    
    lmd_pipeline = config.getList('extractionphases', lang, required=True)
    lmd_mapping = config.getList('mappingphases', lang)
    
    paramrec['extractionphases'] = lmd_pipeline
    paramrec['mappingphases'] = lmd_mapping
    
    if not cmdline.nogmrmapping:
        lmd_pipeline += lmd_mapping
    
    tfamlist = config.getList('targetfamilies', lang)
    tsnamelist = config.getList('targetframes', lang)
    tconlist = config.getList('targetconcepts', lang)
    tcongrouplist = config.getList('targetconceptgroups', lang)
    sfamlist = config.getList('sourcefamilies', lang)
    ssnamelist = config.getList('sourceframes', lang)
    sconlist = config.getList('sourceconcepts', lang)
    mrdatadir = config.getValue('mrdatadir',lang=lang)

    filterparams = {}
    filterparams['targetfamilies'] = tfamlist
    filterparams['targetframes'] = tsnamelist
    filterparams['targetconcepts'] = tconlist
    filterparams['targetconceptgroups'] = tcongrouplist
    filterparams['sourcefamilies'] = sfamlist
    filterparams['sourceframes'] = ssnamelist
    filterparams['sourceconcepts'] = sconlist
    paramrec['filterparams'] = filterparams
    paramrec['mrdatadir'] = mrdatadir

    if ('CNMS' in lmd_pipeline) or ('CMS' in lmd_pipeline):
        # configure and initialize Conceptual Network Mapper
        tconranking = config.getListFromComp('cnms','targetconceptranking', lang)
        secondaryminscore = config.getFloatFromComp('cnms','secondaryminscore', lang)
        mappinglimit = config.getIntFromComp('cnms','sourcelimit', lang)
        conceptmode = config.getValue('casemode',default='general')
        expansionTypes = config.getListFromComp('cnms','expansiontypes',lang=lang)
        expansionScoreScale = config.getFloatFromComp('cnms','expansionscorescale',lang=lang,
                                                      default=1.0)
        disableclosestframe = config.getFlagFromComp('cnms','disableclosestframe',lang=lang)
        fndatadir = config.getValue('framenetdatadir',lang=lang)
        wikdatadir = config.getValue('wiktionarydatadir',lang=lang)
        pwfdatadir = config.getValue('persianwordformsdatadir')
        
        cnmsparams = {}
        cnmsparams['targetconceptranking'] = tconranking
        cnmsparams['secondaryminscore'] = secondaryminscore
        cnmsparams['sourcelimit'] = mappinglimit
        cnmsparams['expansiontypes'] = expansionTypes
        cnmsparams['expansionscorescale'] = expansionScoreScale
        cnmsparams['disableclosestframe'] = disableclosestframe
        paramrec['cnms'] = cnmsparams
        paramrec['casemode'] = conceptmode
        paramrec['framenetdatadir'] = fndatadir
        paramrec['wiktionarydatadir'] = wikdatadir
        paramrec['persianwordformsdatadir'] = pwfdatadir
        
        fndata = None
        wikdata = None
        pwforms = None
        if lang=='en':
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
        if lang=='fa':
            if not pwfdatadir:
                logging.warn('Persian extraction/mapping not using precomputed word forms.'\
                             ' Set "persianwordformsdatadir" to enable.')
            pwforms = PersianWordForms(pwfdir=pwfdatadir)

        # configure and initialize MetaNet Repository
        metanetrep = MetaNetRepository(lang, useSE=cmdline.useSE,mrbasedir=mrdatadir,
                                       fndata=fndata,wikdata=wikdata,pwforms=pwforms)
        metanetrep.initLookups()
        
        cnmapper = ConceptualNetworkMapper(lang, cmdline.cachedir,
                                           targetConceptRank=tconranking,
                                           disableFN=disableclosestframe,
                                           expansionTypes=expansionTypes,
                                           expansionScoreScale=expansionScoreScale,
                                           sourceMappingLimit=mappinglimit, 
                                           minSecondaryScore=secondaryminscore,
                                           metanetrep=metanetrep,
                                           conceptMode=conceptmode)
        
        if cmdline.cmsgenwcacheonly:
            runCMSGenWCacheOnly(cmdline, jdata, metanetrep, cnmapper,
                                tfamlist, tsnamelist, tconlist, tcongrouplist,
                                sfamlist, ssnamelist, sconlist)
            return {}
    
    
    logging.info('running LM pipeline: %s', u', '.join(lmd_pipeline))
    # run the systems    
    for phase in lmd_pipeline:
        try:
            if phase == 'LMS':
                logging.info('starting LMS phase...')
                jdata = runLMS(cmdline, jdata)
            elif phase == 'LMS2':
                logging.info('starting LMS2 phase...')
                jdata = runLMS2(cmdline, jdata)
            elif phase == 'SCMS':
                logging.info('starting SCMS phase ...')
                jdata = runSCMS(cmdline, jdata, logger)
            elif phase == 'CMS':
                logging.info('starting CMS phase ...')
                jdata = runCMS(cmdline, config, jdata, metanetrep, cnmapper, 
                               tfamlist, tsnamelist, tconlist, tcongrouplist,
                               sfamlist, ssnamelist, sconlist)
            elif phase == 'CNMS':
                logging.info('starting CNMS phase ...')
                jdata = runCNMS(cmdline, config, jdata, cnmapper)
            elif phase == 'DIS':
                logging.info('start DIS phase ...')
                jdata = runDIS(cmdline, jdata)
            elif phase == 'PRE':
                logging.info('start PRE phase ...')
                jdata = runPRE(cmdline, jdata)
            elif phase == 'SBS':
                logging.info('start SBS phase ...')
                jdata = runSBS(cmdline, config, jdata)
        except:
            logging.error("Error running phase %s:\n%s", phase,
                          traceback.format_exc())    
    
    if tconlist:
        # if a tconlist is specified, then severely penalize any LM with a target concept
        # outside of that list
        tconset = set(tconlist)
        for sent in jdata['sentences']:
            if 'lms' in sent:
                for lm in sent['lms']:
                    target = lm['target']
                    tcon = target.get('concept')
                    if tcon not in tconset:
                        lm['score'] = 0.0
                        if lm.get('scorecom'):
                            lm['scorecom'] += ':badtcon'
                        else:
                            lm['scorecom'] = 'badtcon'
    jdata['parameters'] = paramrec
    jdata['end_processing_time'] = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S %z")
    return jdata
    
def main():
    """
    Runs linguistic metaphor detection.
    """
    global CHUNKSIZE
    # ------------------------------------------------------------------- #
    # INITIALIZATION
    
    m4test = ix.IARPATestCommand('metad',
                                 'Linguistic Metaphor Detection System.  Finds LMs in IARPA XML TestItems, '\
                                 'or sentences given in MetaNet\'s JSON format.')

    # add some custom cmdline parameters
    aparser = m4test.getArgParser()
    aparser.add_argument("-c", "--cxns", help="Run only these cxns (comma separated)")
    aparser.add_argument("-e", "--engine", help="Querying engine (CMS).  Options are"\
                         " (rdflib, redland, sesame)."\
                         " Use of sesame must be suffixed with the server ip or dns "\
                         " demarked with a colon, e,g, seseame:servername.",
                         default='sesame:localhost')

    aparser.add_argument("-k", "--score-cutoff", dest="scoret",
                         help="Cut off score for m4detect.")
    aparser.add_argument("-s", "--sentidx", default=None, help="Run only the sentences"\
                         " provided (comma separated, single process mode only).")
    aparser.add_argument("--clear-lms", dest="clearLMs", action="store_true",
                         help="Clear out existing LMs from input file before extraction.")
    aparser.add_argument("--disable-dep-check", dest="nodepcheck", action="store_true",
                         help="When set to true, the SBS/CMS will not check for dependency"\
                         " parses, but assume them to be there.")
    aparser.add_argument("--force", help="Force overwriting of existing output files."\
                         "Default behavior is to run the detector only if the "\
                         "output file isn't already there. This applies only in "\
                         "parallel mode.", action="store_true")
    aparser.add_argument("--force-pos-tag", dest="forcepos", action="store_true",
                         help="Force POS tagging in CMS. Overwrite existing tags")
    aparser.add_argument("--force-cache", dest="forcecache", action="store_true",
                         help="Force cache regeneration (CMS)")
    aparser.add_argument("--lem", help="Override default lemma field name ('lem')",
                         default="lem")
    aparser.add_argument("--parallel", type=int, default=0,
                         help="Run detection jobs in parallel."\
                         "Note that in this mode, the input file is interpreted"\
                         " as containing a list of JSON input files to process.")
    aparser.add_argument("--pos", help="Override default POS field name ('pos')",
                         default="pos")
    aparser.add_argument("--disable-gmr-mapping", dest="nogmrmapping", action="store_true",
                         help="Do not run mapping phase which is runs by default with -g.")
    aparser.add_argument("--cms-genwcache-only", dest="cmsgenwcacheonly", action="store_true",
                         help="Run CMS search word cache generation and then exit. (CMS only)")
    aparser.add_argument("--no-seed-matches",dest='noseedmatches',action='store_true',
                         help="For SBS, remove LMs that are exact seed matches.")
    aparser.add_argument("--trans-en",dest="translateEn",action="store_true",
                         help="For non-English languages, this option allows frame and "\
                         "frame families names to be given in English.  Translation is "\
                         "accomplished via Interwiki links.")
    
    cmdline, config = m4test.parseCmdLineConfig('m4detect')
    cmdline.allcxns = True
    
    # --------------------------------------------------------------------- #
    # PARALLEL-MODE: Note - this is JSON only
    
    if cmdline.parallel:
        if cmdline.cmsgenwcacheonly:
            logging.error('Options --parallel and --cms-genwcache-only are not compatible')
            raise
        cmdline.json = True
        # PARALLEL MODE
        poolitems = []
        with codecs.open(cmdline.infilename, encoding='utf-8') as flist:
            for line in flist:
                infilename = line.strip()
                if not infilename:
                    continue
                outfilename = m4test.getDefaultOutFileName(infilename)
                if os.path.exists(outfilename) and (not cmdline.force):
                    logging.info("Skipping %s because result file exists.", infilename)
                    continue
                poolitems.append((infilename, outfilename, cmdline, config))
        pool = Pool(cmdline.parallel)
        pool.map(runLMDetectionInstance, poolitems, CHUNKSIZE)
        return
    
    # -------------------------------------------------------------------- #
    # SINGLE-PROCESS MODE: NOT PARALLEL
    jdata = m4test.getJSON()
    lang = jdata['lang']
    
    # ------------------------------------------------------------------- #
    # PARAMETER AND OPTIONS PROCESSING
    
    if cmdline.sentidx:
        jdata['sentences'] = [jdata['sentences'][int(sidx)] for sidx in cmdline.sentidx.split()]
        
    if cmdline.json:
        logger = None
    else:
        logger = m4test.getLogger()  # this is IARPA log (not python log)
          
    # adjust scoring threshhold, either parameter or environment variable
    if cmdline.scoret:
        m4test.setmetadScoreT(float(cmdline.scoret))
    else:
        score_ev = 'M4DETECT_%s_SCORET' % (lang.upper())
        if score_ev in os.environ:
            m4test.setmetadScoreT(float(os.environ[score_ev]))
        else:
            if not cmdline.configmode:
                scorerequired = True
            else:
                scorerequired = False
            scoret = config.getFloat('scorethreshold', lang, required=scorerequired)
            m4test.setmetadScoreT(scoret)
    
    # ------------------------------------------------------------------- #
    # MAIN APPLICATION 
    
    jdata = runLMDetection(jdata, cmdline, config, logger)
    if not jdata:
        if cmdline.cmsgenwcacheonly:
            return
        else:
            logger.error('LM detection returned empty data structure')
            raise
    
    # ------------------------------------------------------------------- #
    # OUTPUT FILE GENERATION
    m4test.writeOutput(jdata)
        
if __name__ == "__main__":
    status = main()
    sys.exit(status)
