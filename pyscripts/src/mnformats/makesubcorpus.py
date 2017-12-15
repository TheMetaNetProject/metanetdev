#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: makesubcorpus
   :platform: Unix
   :synopsis: Uses the CMS's filtering system to create a subcorpus from a set of JSON files.

This module is used to create a subcorpus containing sentences that contain
words matching those in the specified target or source frames, families, or
concepts.  It's main use is to extract a smaller subcorpus on a particular
domain from a much larger corpus.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
import sys, os, codecs, subprocess, logging, pprint, codecs, traceback, argparse
from mnpipeline.affectlookup import AffectLookup
from mnformats import mnjson
from cmsextractor.cms import ConstructionMatchingSystem
from mnrepository.cnmapping import ConceptualNetworkMapper
from mnrepository.metanetrdf import MetaNetRepository
from mnrepository.fnxml import FrameNet
from mnrepository.wiktionary import Wiktionary
from mnrepository.persianwordforms import PersianWordForms
from datetime import datetime
from dateutil.tz import tzlocal
from mnconfig import MetaNetConfigParser

# TODO: perhaps remove this
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

# default configuration filename
DEFAULT_CONFIGFNAME = '/u/metanet/etc/mnsystem.conf'
CONFIG_ENV = 'MNSYSTEM_CONF'

def main():
    """
    Runs subcorpus generation.
    """
    # ------------------------------------------------------------------- #
    # INITIALIZATION
    
    # add some custom cmdline parameters
    aparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Script for generating a subcorpus from a set of JSON files "\
        "usually from a large corpus.  It uses the CMS's target and source word "\
        "matching system.")
    aparser.add_argument("filelistfile",help="File containing list of corpus files "\
                         "in JSON format.")
    aparser.add_argument("outputfile",help="Name of resulting subcorpus file")
    aparser.add_argument("-l","--lang",help="Language",required=True)
    aparser.add_argument("--doc",help="Unique name to give to the subcorpus")
    aparser.add_argument("--corpus",help="Unique name of corpus")
    aparser.add_argument("--desc",help="Description of subcorpus")
    aparser.add_argument("-e", "--engine", help="Querying engine (CMS).  Options are"\
                         " (rdflib, redland, sesame)."\
                         " Use of sesame must be suffixed with the server ip or dns "\
                         " demarked with a colon, e,g, seseame:servername.",
                         default='sesame:localhost')
    aparser.add_argument("--force-pos-tag", dest="forcepos", action="store_true",
                         help="Force POS tagging in CMS. Overwrite existing tags")
    aparser.add_argument("--force-cache", dest="forcecache", action="store_true",
                         help="Force cache regeneration (CMS)")
    aparser.add_argument("--lem", help="Override default lemma field name ('lem')",
                         default="lem")
    aparser.add_argument("--pos", help="Override default POS field name ('pos')",
                         default="pos")
    aparser.add_argument("--trans-en",dest="translateEn",action="store_true",
                         help="For non-English languages, this option allows frame and "\
                         "frame families names to be given in English.  Translation is "\
                         "accomplished via Interwiki links.")
    aparser.add_argument("--config", dest="configfname",
                         help="Configuration filename to override the default "\
                         " which can also be overridden by environment variable"\
                         " %s (default=%s)" % (CONFIG_ENV,DEFAULT_CONFIGFNAME))
    aparser.add_argument("--mode", dest="configmode",
                         help="Used to activate a mode defined in the config file.")
    aparser.add_argument("--cache-dir", dest="cachedir", default=None,
                         help="To override default cache directories")
    aparser.add_argument("--use-se", dest="useSE", default='localhost',
                         help="Use Sparql endpoint at the specified server address.")


    cmdline = aparser.parse_args()
    
    # for logging / error messages
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    logging.basicConfig(format=msgformat, datefmt=dateformat,
                        level=logging.INFO)

    # parse the config file
    cfname = None
    if cmdline.configfname:
        cfname = self.cmdline.configfname
    else:
        cfname = os.environ.get(CONFIG_ENV)
        if not cfname:
            cfname = DEFAULT_CONFIGFNAME
    config = MetaNetConfigParser(cfname,"makesubcorpus",cmdline.configmode)

    startproctime = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S %z")

    docheader = mnjson.getJSONDocumentHeader(name=cmdline.doc,
                                             corp=cmdline.corpus,
                                             desc=cmdline.desc,
                                             prov=cmdline.doc,
                                             type='subcorpus',
                                             lang=cmdline.lang,
                                             pubdate=startproctime)
    jdata = mnjson.getJSONRoot(lang='en',docs=docheader)
    
    # start up metanetrep, cnmapper, cms
    jdata[u'start_processing_time'] = startproctime
    lang = cmdline.lang
    
    paramrec = {}
    
    tfamlist = config.getList('targetfamilies', lang)
    tsnamelist = config.getList('targetframes', lang)
    tconlist = config.getList('targetconcepts', lang)
    tcongrouplist = config.getList('targetconceptgroups', lang)
    sfamlist = config.getList('sourcefamilies', lang)
    ssnamelist = config.getList('sourceframes', lang)
    sconlist = config.getList('sourceconcepts', lang)
    
    filterparams = {}
    filterparams[u'targetfamilies'] = tfamlist
    filterparams[u'targetframes'] = tsnamelist
    filterparams[u'targetconcepts'] = tconlist
    filterparams[u'targetconceptgroups'] = tcongrouplist
    filterparams[u'sourcefamilies'] = sfamlist
    filterparams[u'sourceframes'] = ssnamelist
    filterparams[u'sourceconcepts'] = sconlist
    paramrec[u'filterparams'] = filterparams

    
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
    mrdatadir = config.getValue('mrdatadir',lang=lang)
    
    cnmsparams = {}
    cnmsparams[u'targetconceptranking'] = tconranking
    cnmsparams[u'secondaryminscore'] = secondaryminscore
    cnmsparams[u'sourcelimit'] = mappinglimit
    cnmsparams[u'expansiontypes'] = expansionTypes
    cnmsparams[u'expansionscorescale'] = expansionScoreScale
    cnmsparams[u'disableclosestframe'] = disableclosestframe
    paramrec[u'cnms'] = cnmsparams
    paramrec[u'casemode'] = conceptmode
    paramrec[u'framenetdatadir'] = fndatadir
    paramrec[u'wiktionarydatadir'] = wikdatadir
    paramrec[u'persianwordformsdatadir'] = pwfdatadir
    paramrec[u'mrdatadir'] = mrdatadir
    
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
    metanetrep = MetaNetRepository(lang, useSE=cmdline.useSE,
                                   mrbasedir=mrdatadir,
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
    
    excludedfamilies = config.getListFromComp('cms','excludedfamilies', lang)
    metarcfname = config.getValueFromComp('cms','metarcfile',lang)    

    cms = ConstructionMatchingSystem(lang, posfield=cmdline.pos, lemfield=cmdline.lem,
                                     useSE=cmdline.useSE,
                                     forcecache=cmdline.forcecache,
                                     engine=cmdline.engine, nodepcheck=True,
                                     excludedFamilies=excludedfamilies,
                                     metanetrep=metanetrep,cnmapper=cnmapper,
                                     metarcfname=metarcfname)
    
    maxsentlength = config.getValueFromComp('cms','maxsentlength', lang)
    if maxsentlength:
        cms.setMaxSentenceLength(int(maxsentlength))
    disablewcache = config.getValueFromComp('cms','disablewcaching', lang)
    if disablewcache and (disablewcache.lower() == 'true'):
        cms.setSearchWordCaching(False)
    cxnpatternfname = config.getValueFromComp('cms','cxnpatternfile',lang)
    cmsparams = {}
    cmsparams[u'excludedfamilies'] = excludedfamilies
    cmsparams[u'metarcfile'] = metarcfname
    cmsparams[u'maxsentlength'] = maxsentlength
    cmsparams[u'disablewcaching'] = disablewcache
    cmsparams[u'cxnpatternfile'] = cxnpatternfname
    paramrec[u'cms'] = cmsparams
    
    cms.prepSearchWords(tfamlist,tsnamelist,tconlist,tcongrouplist,
                        sfamlist,ssnamelist,sconlist,
                        translateEn=cmdline.translateEn)
    
    sentence_counter = 0
    subcorpus = []
    with codecs.open(cmdline.filelistfile, encoding='utf-8') as flist:
        for line in flist:
            infilename = line.strip()
            if not infilename:
                continue
            in_jdata = mnjson.loadfile(infilename)
            sc_sents = cms.getSubcorpus(in_jdata[u'sentences'],
                                        forcePOScomp=cmdline.forcepos)
            for sent in sc_sents:
                sent[u'cfile'] = infilename
                sent[u'cid'] = sent[u'id']
                sent[u'cidx'] = sent[u'idx']
                sent[u'id'] = u'%s:%s' % (cmdline.doc,sentence_counter+1)
                sent[u'idx'] = sentence_counter
                subcorpus.append(sent)
            logging.info("added %d sentences from %s",len(sc_sents),infilename)
                
    # ------------------------------------------------------------------- #
    # OUTPUT FILE GENERATION
    jdata[u'parameters'] = paramrec
    jdata[u'end_processing_time'] = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S %z")
    jdata[u'sentences'] = subcorpus
    logging.info(u'writing %s with %d sentences',cmdline.outputfile, len(subcorpus))
    mnjson.writefile(cmdline.outputfile, jdata)
        
if __name__ == "__main__":
    status = main()
    sys.exit(status)
