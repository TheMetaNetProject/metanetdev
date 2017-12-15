"""
.. module:: iarpaxml
    :platform: Unix
    :synopsis: Utilities for converting from and to IARPAs m4detect XML formats

Utilities for converting from and to IARPA's m4detect et. al XML formats, including
input, result, and logging formats.  Also provides a standard set of command line
parameters for all of the scripts, and for configuring the scripts using a
configuration file specified via an environment variable (MNSYSTEM_CONF) for via
a command line parameter.  The configuration file's format is similar to that of
Microsoft Windows INI files and is parsed using `mnformats.mnconfig.MetaNetConfigParser`.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
import sys, os, codecs, logging, re, pprint, shutil
from mnformats.mnconfig import MetaNetConfigParser
import time
from xml import sax
import xml.etree.ElementTree as et
from mnformats import mnjson
import argparse, subprocess, random
from collections import Counter

# IARPA XML schemas for validation
SCHEMAS = {'metad':'http://www.iarpa.gov/Metaphor/DetectSchema m4detectSchema_22.xsd',
           'metam':'http://www.iarpa.gov/Metaphor/MappingSchema m4mappingSchema_20.xsd',
           'metas':'http://www.iarpa.gov/Metaphor/SourceSchema m4sourceSchema_11.xsd',
           'metaa':'http://www.iarpa.gov/Metaphor/AffectSchema m4affectSchema_11.xsd'}

NAMESPACES = {'metad':'http://www.iarpa.gov/Metaphor/DetectSchema',
              'metam':'http://www.iarpa.gov/Metaphor/MappingSchema',
              'metas':'http://www.iarpa.gov/Metaphor/SourceSchema',
              'metaa':'http://www.iarpa.gov/Metaphor/AffectSchema',
              'xsi':'http://www.w3.org/2001/XMLSchema-instance'}

# Target domain side mapping from IARPA concepts to MetaNet Schema Families
TARGET_CONCEPT_SCHEMAS = \
    {u'POVERTY':u'Poverty',
     u'TAXATION':u'Taxation',
     u'WEALTH':u'Wealth',
     u'GOVERNMENT':u'Government',
     u'BUREAUCRACY':u'Bureaucracy',
     u'DEMOCRACY':u'Democracy',
     u'ELECTIONS':u'Election'}

CULTURAL_CONCEPT_FAMILIES = \
    {u'ECONOMIC_INEQUALITY':u'Economic Inequality schemas',
     u'GOVERNANCE':u'Governance schemas',
     u'DEMOCRACY':u'Democracy schemas'}

# default configuration filename
DEFAULT_CONFIGFNAME = '/u/metanet/etc/mnsystem.conf'
CONFIG_ENV = 'MNSYSTEM_CONF'

# this is what we are supposed to report in the case that no concept
# of dimension was found, in the mapping and source tasks
DEFAULT_GOV_ID = "999"

class IARPATestCommand:
    """
    Class that takes care of most of the overhead in running the IARPA test
    commands like the required XML conversions, logging, and common command
    line parameters.  Initialize with one of the test types (metaa, metad,
    metam, metas), and a description of the command.
    
    """
    def __init__(self, testType, description):
        """ Initialize IARPATestCommand
        
        :param testType: test type (metaa, metad, metam, metas)
        :type testType: str
        :param description: prose description of the test
        :type description: str
        
        """
        self.testType = testType
        self.logger = None
        self.pylogger = logging.getLogger(__name__)
        self._initArgParser(description)
        self.lmscoret = -9999.0
        self.secondaryMappingThreshold = 0.0
    
    def _initArgParser(self, desc):
        """ Defines the common set of command line parameters accepted by
        all of the m4 commands.  The parser can then be externally
        extended by each m4 command.
        
        """
        parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=desc,
        epilog="")
    
        # required (positional) args
        parser.add_argument("infilename", help="input file", nargs='?')
        parser.add_argument("outfilename", help="results file", nargs='?')
        parser.add_argument("logfilename", help="log file", nargs='?')
        
        # optional arguments
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                            help="To print more status messages")
        parser.add_argument("-d", "--debug", action="store_true",
                            help="Enable debugging features")
        parser.add_argument("-j", "--json", action="store_true",
                            help="Read and write json instead of XML.")
        # these arguments do not have short versions, to keep the NS clear
        parser.add_argument("--team", dest="teamname", default='ICSI',
                            help="Set team name specified in the output files.")
        parser.add_argument("--intermediate-files-dir", dest="intdirprefix",
                            help="Set prefix on dir name for intermediate files.")
        parser.add_argument("--resource-dir", dest="extdir", default=None,
                            help="To override directory to find resources")
        parser.add_argument("--cache-dir", dest="cachedir", default=None,
                            help="To override default cache directories")
        parser.add_argument("--use-se", dest="useSE", default='localhost',
                            help="Use Sparql endpoint at the specified server address.")
        parser.add_argument("--config", dest="configfname",
                            help="Configuration filename to override the default "\
                            " which can also be overridden by environment variable"\
                            " %s (default=%s). If a file named %s is present in"\
                            " the working directory, it will override the"\
                            " default." % (CONFIG_ENV,DEFAULT_CONFIGFNAME,
                                           os.path.basename(DEFAULT_CONFIGFNAME)))
        parser.add_argument("-g", "--gmr-settings", action="store_true", dest="gmr",
                            help="Equivalent to --mode gmr.general")
        parser.add_argument("--mode", dest="configmode",
                            help="Used to activate a mode defined in the config file.")
        parser.add_argument("--output-prefix",dest="outputprefix",
                            help="Change the default result file prefix.")
        parser.add_argument("--create-local-config",dest="createlocalconfig",action="store_true",
                            help="Create a local configuration file in the working directory to"\
                                " override the system-wide one, and then exit.")

        self.argparser = parser
        
    def getArgParser(self):
        """ Accessor method to retrieve the argument parser.  This enables argument
        parsing to be extended.
        :returns: instance of :py:class:`argparse.ArgumentParser`
        
        """
        return self.argparser
    
    def getDefaultOutFileName(self, infilename):
        """ Return the default output filename for a given input filename, which
        is **Result_** prepended to the input filename.
        
        :param infilename: input file name
        :type infilename: str
        :returns: default output file name
        
        """
        outpref = self.config.getValue("defaultresultprefix", default='Result_',
                                       override=self.cmdline.outputprefix)
        return '%s%s' % (outpref,os.path.basename(infilename))
    
    def parseCmdLineConfig(self, configSectionName, skipLogSetup=False):
        """Run cmdline the parser: this is done separately so that
        the cmdline parser can be custom extended: also sets up
        python (not to be confused with IARPA) logging, unless disabled.
        
        :param skipLogSetup: flag to disable logging setup
        :type skipLogSetup: boolean
        :returns: parsed cmdline structure (:py:mod:`argparse`)

        """
        # parse the command line
        self.cmdline = self.argparser.parse_args()

        if not skipLogSetup:
            self.setupPyLogging()

        if self.cmdline.gmr:
            if not self.cmdline.configmode:
                self.cmdline.configmode = 'gmr.general'
        
        if self.cmdline.createlocalconfig:
            self.pylogger.info("Making local copy of %s for customization",DEFAULT_CONFIGFNAME)
            shutil.copy(DEFAULT_CONFIGFNAME,".")
            sys.exit()
        else:
            if not self.cmdline.infilename:
                self.pylogger.error("No input file name specified")
                sys.exit()
                
        # parse the config file
        cfname = None
        if self.cmdline.configfname:
            cfname = self.cmdline.configfname
        else:
            cfname = os.environ.get(CONFIG_ENV)
            if not cfname:
                cfname = "./"+os.path.basename(DEFAULT_CONFIGFNAME)
                if not os.path.exists(cfname):
                    cfname = DEFAULT_CONFIGFNAME
        self.pylogger.info('reading configuration from %s',cfname)
        self.config = MetaNetConfigParser(cfname,configSectionName,self.cmdline.configmode)

        # set default parameters
        if not self.cmdline.outfilename:
            self.cmdline.outfilename = self.getDefaultOutFileName(self.cmdline.infilename)
        if not self.cmdline.logfilename:
            if not self.cmdline.json:
                self.cmdline.logfilename = 'Log_%s' % (os.path.basename(self.cmdline.infilename))
        return self.cmdline, self.config

    
    def getJSON(self):
        """ Parse testset XML format and retrieve JSON, and testId.
        If the input file was JSON, then just returns the JSON content.
        
        :returns: JSON data as a dict
        
        """
        if self.cmdline.json:
            jdata = mnjson.loadfile(self.cmdline.infilename)
            return jdata
        # otherwise read XML
        self.testsetxml = TestSetXML(self.testType, self.cmdline.infilename)
        jdata = self.testsetxml.getJSON()
        if self.testType == 'metam':
            self.targetIDLookup = self.testsetxml.getTargetList()
            self.sourceIDLookup = self.testsetxml.getSourceList()
            self.targetNameLookup = self.testsetxml.getTargetIdList()
            self.sourceNameLookup = self.testsetxml.getSourceIdList()
        elif self.testType == 'metas':
            self.sourceDimIDLookup = self.testsetxml.getDimensions()
            self.sourceIDLookup = self.testsetxml.getSourceList()

        self.testId = self.testsetxml.getTestSetId()
        self.testItemCount = self.testsetxml.getTestItemCount()     
        self.tmplogfilename = self.cmdline.logfilename + '.tmp'
        self.logger = IARPALogger(self.testType, self.testId, self.tmplogfilename,
                                  self.cmdline.teamname, self.testItemCount)
        if self.cmdline.debug:
            mnjson.writefile(os.path.basename(self.cmdline.infilename) + '.pre.json', jdata)
        return jdata
    
    def getLogger(self):
        """ Retrieve the python logger (not to be confused to the IARPA logging class).
        
        :returns: python logger
        
        """
        return self.logger
    
    def setupPyLogging(self):
        """ Setup python logging to work so that it integrates with IARPA's
        logging requirements.
        
        """
        msgformat = u'%(asctime)-15s - %(message)s'
        dateformat = u'%Y-%m-%dT%H:%M:%SZ'
        lfmt = logging.Formatter(msgformat, dateformat)
        
        # root logger
        rlogger = logging.getLogger()
        
        # info handler: screen (stderr)
        infohand = logging.StreamHandler()
        infohand.setFormatter(lfmt)

        if self.cmdline.verbose:
            infohand.setLevel(logging.INFO)
            rlogger.setLevel(logging.INFO)
        else:
            infohand.setLevel(logging.WARN)
            rlogger.setLevel(logging.WARN)    
        # debug handler: to file
        if self.cmdline.debug:
            dbglogfname = os.path.basename(self.cmdline.infilename) + '.debug.log'
            debughand = logging.FileHandler(dbglogfname,
                                            mode='w',
                                            encoding='utf-8')
            debughand.setLevel(logging.DEBUG)
            debughand.setFormatter(lfmt)    
            rlogger.addHandler(debughand)
            rlogger.setLevel(logging.DEBUG)

        rlogger.addHandler(infohand)
    
    def setmetadScoreT(self, score):
        """ Set the score threshhold for discarding LMs.  If LM's score < self.lmscoret
        then discard the LM.
        
        :param score: threshhold score
        :type score: float
        
        """
        self.lmscoret = score
    
    def setSecondaryMappingThreshold(self, score):
        """ Set the mapping score threshold that must be surpassed for a secondary
        mapping to be included in the answer set.
        
        :param score: the threshold score
        :type score: float
        """
        self.secondaryMappingThreshold = score
    
    def metadProcessResult(self, sent):
        """ Process result sentence of metad test type, for output XML generation.
        
        :param sent: sentence
        :type sent: dict
        
        """
        (testItemId, sId) = self.testsetxml.getTestItemSentenceIds(sent['id'])
        if 'lms' in sent:
            for lm in sent['lms']:
                thisscore = lm.get('score')
                if (not thisscore) or (float(thisscore) < self.lmscoret):
                    self.pylogger.info(u'lm %s %s skipped because score %.2f < %.2f' % (lm['target']['lemma'],
                                                                                       lm['source']['lemma'],
                                                                                       lm['score'],
                                                                                       self.lmscoret))
                    continue
                else:
                    self.pylogger.info(u'adding lm %s %s with score %s',lm['target']['lemma'],
                                                                        lm['source']['lemma'],
                                                                        pprint.pformat(thisscore))
                self.resultset.addLM(testItemId, sId,
                                     lm['target']['lemma'],
                                     lm['source']['lemma'])
    
    def metaaProcessResult(self, sent):
        """ Process result sentence of metaa test type, for output XML generation.
        
        :param sent: sentence
        :type sent: dict
        
        """
        testItemId = self.testsetxml.getTestItemId(sent['id'])
        lm = sent['lms'][0]
        self.resultset.addAffect(testItemId, lm['affect'])
        
    def metamProcessResult(self, jdata):
        """ Process result of metam test type, for output XML generation.  Must put
        together mapping output of all the sentences in the test item.
        
        :param jdata: sentence
        :type jdata: dict
        
        """
        global DEFAULT_GOV_ID
        testItemResults = {}
        testItemList = []
        for doc in jdata['documents']:
            testItemId = doc['name'].split(':')[1]
            #
            # Target concept is selected by majority
            # Source concept is selected by score weighting
            testItemResults[testItemId] = {'target':Counter(), 'source':{'total':0.0}, 'sourcefreq':Counter()}
            testItemList.append(testItemId)
        sentVecByTestItem = {}
        for sent in jdata['sentences']:        
            testItemId = self.testsetxml.getTestItemId(sent['id'])
            if testItemId not in sentVecByTestItem:
                sentVecByTestItem[testItemId] = []
            for lm in sent['lms']:
                if 'concept' not in lm['target']:
                    targetconcept = 'DEFAULT'
                else:
                    targetconcept = lm['target']['concept']
                sourceconcept = lm['source']['concept']
                try:
                    sentVecByTestItem[testItemId].append([testItemId,lm['target']['lemma'],
                                                          lm['source']['lemma'],
                                                          targetconcept,sourceconcept,
                                                          lm['extractor'],sent['text']])
                except KeyError:
                    sentVecByTestItem[testItemId].append([testItemId,lm['target']['form'],
                                                          lm['source']['form'],
                                                          targetconcept,sourceconcept,
                                                          lm['extractor'],sent['text']])
                tconId = DEFAULT_GOV_ID
                if targetconcept:
                    if targetconcept in self.targetIDLookup:
                        tconId = self.targetIDLookup[targetconcept]
                testItemResults[testItemId]['target'].update([tconId])
                sconList = []
                # sourceconcept is a string CONCEPT:RANK:SCORE,CONCEPT:RANK:SCORE...
                if sourceconcept:
                    if u',' in sourceconcept:
                        sconList = sourceconcept.split(u',')
                    else:
                        sconList = [sourceconcept]
                for sconTrip in sconList:
                    if sconTrip == u'NONE':
                        continue
                    elif u':' not in sconTrip:
                        # maybe its from the KMS system
                        if sconTrip in self.sourceIDLookup:
                            # its a valid source label-- add dummy rank/score
                            # with low score so as not to overwhelm
                            sconTrip += ':2:0.10'
                    try:
                        scon, rank, score = sconTrip.split(u':', 2)
                    except:
                        self.pylogger.error('invalid source concept %s in sentence %s',
                                            sconTrip, sent['id'])
                        continue
                    if scon in self.sourceIDLookup:
                        sconId = self.sourceIDLookup[scon]
                        if sconId == DEFAULT_GOV_ID:
                            continue
                        weightedScore = float(score) / float(rank)
                        if scon in testItemResults[testItemId]['source']:
                            testItemResults[testItemId]['source'][scon] += weightedScore
                            testItemResults[testItemId]['sourcefreq'][scon] += 1
                        else:
                            testItemResults[testItemId]['source'][scon] = weightedScore
                            testItemResults[testItemId]['sourcefreq'][scon] = 1
                        testItemResults[testItemId]['source']['total'] += weightedScore
        for testItemId in testItemList:
            sourceResults = testItemResults[testItemId]['source']
            sourceFreqs = testItemResults[testItemId]['sourcefreq']
            # discard the counts for target
            try:
                mostcommontarg, _ = testItemResults[testItemId]['target'].most_common(1)[0]
            except IndexError:
                mostcommontarg = 'DEFAULT'
            try:
                mostcommonsour, topscount = sourceFreqs.most_common(1)[0]
                topscount = float(topscount)
            except IndexError:
                topscount = 1.0
            wscoreTotal = sourceResults['total']
            del sourceResults['total']
            # normalize weighted scores by total
            for scon in sourceResults:
                finalScore = (sourceResults[scon] / wscoreTotal) * (sourceFreqs[scon] / topscount)
                self.pylogger.debug('Scon %s has pre-scale score %f and freq %d, post scale = %f',
                                    scon,sourceResults[scon] / wscoreTotal,sourceFreqs[scon],finalScore)
                sourceResults[scon] = finalScore
            rankedSources = sorted(sourceResults.keys(), key=lambda scon: sourceResults[scon],
                                   reverse=True)
            topsources = []
            if not rankedSources:
                # give a random answer
                topsources.append(random.choice(self.sourceIDLookup.values()))
            else:
                topsources.append(self.sourceIDLookup[rankedSources[0]])
                if (len(rankedSources) > 1) and (sourceResults[rankedSources[1]] > self.secondaryMappingThreshold):
                    topsources.append(self.sourceIDLookup[rankedSources[1]])
                for sconid in topsources:
                    sconname = self.sourceNameLookup[sconid]
                    self.pylogger.debug('testItem %s: reporting %s score %.4f',
                                      testItemId, sconname, sourceResults[sconname])
            self.resultset.addMapping(testItemId,
                                      mostcommontarg,
                                      topsources)
            for vec in sentVecByTestItem[testItemId]:
                vec.insert(-1,self.targetNameLookup[mostcommontarg])
                for sconid in topsources:
                    sconname = self.sourceNameLookup[sconid]
                    try:
                        vec.insert(-1,u'%s:%f'%(sconname,sourceResults[sconname]))
                    except KeyError:
                        vec.insert(-1,u'%s:%f'%(sconname,0.0))                
        if self.cmdline.debug:
            outputdatafname = os.path.basename(self.cmdline.infilename) + '.result.txt'
            outrf = codecs.open(outputdatafname,'w',encoding='utf-8')
            for testItemId in testItemList:
                for vec in sentVecByTestItem[testItemId]:
                    print >> outrf, u'\t'.join(['' if not item else item for item in vec])
                
    def metasProcessResult(self, sent):
        """ Process result sentence of metas test type, for output XML generation.
        
        :param sent: sentence
        :type sent: dict
        
        """
        global DEFAULT_GOV_ID
        testItemId = self.testsetxml.getTestItemId(sent['id'])
        lm = sent['lms'][0]
        sourceconceptdim = lm['source']['dimension']
        sconId = DEFAULT_GOV_ID
        sdimId = DEFAULT_GOV_ID
        if sourceconceptdim:
            if sourceconceptdim in self.sourceDimIDLookup:
                dimId = self.sourceDimIDLookup[sourceconceptdim]
                (sconId, sdimId) = dimId.split('.', 1)
        else:
            sconId = self.sourceIDLookup[lm['source']['concept']]
        self.resultset.addSource(testItemId, sconId, sdimId)
        
    def writeOutput(self, jdata):
        """ Write out the output XML files (results XML, Log XML) required
        by IARPA.
        
        :param jdata: processed MetaNet JSON format data
        :type jdata: dict
        
        """
        global DEFAULT_GOV_ID
        if self.cmdline.json:
            outmode = self.config.getValue('outputmode',default='allsentences')
            if outmode=='onlylms':
                lmjdata = {u'lang':jdata['lang'],
                           u'cwd':os.getcwd(),
                           u'input_file':self.cmdline.infilename,
                           u'parameters':jdata['parameters'],
                           u'start_processing_time':jdata['start_processing_time'],
                           u'end_processing_time':jdata['end_processing_time'],
                           u'anno_type':u'lm',
                           u'annotations':jdata['lmlist']
                           }
                mnjson.writefile(self.cmdline.outfilename, lmjdata)
                return
            if outmode == 'lmsentences':
                lmsentences = []
                idx = 0
                for sent in jdata["sentences"]:
                    if sent.get("lms"):
                        sent[u'idx'] = idx
                        idx += 1
                        lmsentences.append(sent)
                jdata["sentences"] = lmsentences
            mnjson.writefile(self.cmdline.outfilename, jdata)
            return
        
        if self.cmdline.debug:
            mnjson.writefile(os.path.basename(self.cmdline.infilename) + '.post.json', jdata)
             
        # prepare and write out the result XML
        tmpoutfilename = self.cmdline.outfilename + '.tmp'
        self.resultset = IARPAResultSetXML(self.testType, self.testId, tmpoutfilename,
                                              self.cmdline.teamname)
        
        processResult = {'metaa':self.metaaProcessResult,
                         'metad':self.metadProcessResult,
                         'metas':self.metasProcessResult}
        if self.testType in processResult:
            for sent in jdata['sentences']:
                if ('lms' not in sent) or not sent['lms']:
                    continue
                processResult[self.testType](sent)
        elif self.testType == 'metam':
            self.metamProcessResult(jdata)

        self.resultset.writeResultSetXML()    
        # end logger
        self.logger.writeLogXML()

        # prettify the XML output files
        finaloutfile = codecs.open(self.cmdline.outfilename, "w", encoding='utf-8')
        subprocess.call(['xmllint', '--format', tmpoutfilename],
                        stdout=finaloutfile)
        finallogfile = codecs.open(self.cmdline.logfilename, "w", encoding='utf-8')
        subprocess.call(['xmllint', '--format', self.tmplogfilename],
                        stdout=finallogfile)
        finaloutfile.flush()
        finallogfile.flush()
        os.remove(tmpoutfilename)
        os.remove(self.tmplogfilename)

# ============================================================================== #        

class TestSetXML:
    """ Primary class for reading IARPA's input XML format.  Instantiate with
    a test type in [metaa,metad,metam,metas] and input filename.
    
    """
    def __init__(self, stype, infilename):
        """ Initialize instance
        
        :param stype: test type [metaa,metad,metam,metas]
        :type stype: str
        :param infilename: input file name
        :type infilename: str
        
        """
        if stype == 'metaa':
            self.inputhandler = MetaATestSetXMLHandler()
        elif stype == 'metad':
            self.inputhandler = MetaDTestSetXMLHandler()
        elif stype == 'metam':
            self.inputhandler = MetaMTestSetXMLHandler()
        elif stype == 'metas':
            self.inputhandler = MetaSTestSetXMLHandler()
        else:
            raise Exception('Invalid test type.  Must be in [metaa, metad, metam, metas].')
        self.stype = stype 
        parser = sax.make_parser()
        parser.setContentHandler(self.inputhandler)
        parser.setFeature(sax.handler.feature_namespaces, 1)
        # let parser do decoding
        parser.parse(infilename)
        
    def getJSON(self):
        """ Retrieve json-compatible dict version of the input XML """
        return self.inputhandler.getJSON()
    
    def getTestSetId(self):
        """ Retrieve the TestSet Id (of the whole XML file) """
        return self.inputhandler.getTestSetId()
 
    def getTestItemId(self, sId):
        """ Given a sentence id, retrieve the TestItem id """
        return self.inputhandler.getTestItemId(sId)
    
    def getTargetList(self):
        """ Retrieve list of target concepts and id numbers """
        if self.stype not in ['metas', 'metam']:
            raise Exception('SourceList in metas, metam type XML only')
        return self.inputhandler.getTargetList()

    def getTargetIdList(self):
        """ Retrieve list of target concepts and id numbers: go from IDs
        to target concept names """
        if self.stype not in ['metas', 'metam']:
            raise Exception('SourceList in metas, metam type XML only')
        return self.inputhandler.getTargetIdList()
    
    def getSourceList(self):
        """ Retrieve list of source concepts and id numbers """
        if self.stype not in ['metas', 'metam']:
            raise Exception('SourceList in metas, metam type XML only')
        return self.inputhandler.getSourceList()
    
    def getSourceIdList(self):
        """ Retrieve list of source concepts and id numbers: go from IDs
        to source concept names """
        if self.stype not in ['metas', 'metam']:
            raise Exception('SourceList in metas, metam type XML only')
        return self.inputhandler.getSourceIdList()
    
    def getDimensions(self):
        """ Retrieve list of source dimensions and id numbers """
        if self.stype != 'metas':
            raise Exception('Cannot retrieve dimensions for non-metas type XML')
        return self.inputhandler.getDimensions()
    
    def getTestItemSentenceIds(self, sId):
        """ The Id on the sentences contains testitem ids as well as for the
         sentence, in the case of metad.  Retrieve just the sentence part.
         
         """
        if self.stype != 'metad':
            raise Exception('TestItem ID and S ID distinct only for metad')
        return self.inputhandler.getTestItemSentenceIds(sId)

    def getTestItemCount(self):
        return self.inputhandler.getTestItemCount()
#
# ===========================================================================
#

class IARPALogger:
    """
    Class for generating the XML and Console logs that IARPA wants
    stype = ['metad','metam','metas','metaa']
    It would be nice if we didn't have to store up a DOM in
    memory for this, but we can't stream because of the count attribute
    in the main tag.
    
    .. note:: count is supposed to be the number of TIs, if there are no LogEntries.
    """
    def __init__(self, stype, testId, filename='LogFile.xml', teamId='ICSI', tiCount=0):
        """ Initialize instance
        
        :param stype: test type ['metad','metam','metas','metaa']
        :type stype: str
        :param testId: test identifier
        :type testId: str
        :param filename: log output file name
        :type filename: str
        :param teamId: team identifier
        :type teamId: str
        :param tiCount: number of test items
        :type tiCount: int
        
        """
        et.register_namespace(stype, NAMESPACES[stype])
        et.register_namespace('xsi', NAMESPACES['xsi'])
        
        self.testId = testId
        self.ns = stype
        self.filename = filename
        self.logroot = et.Element(stype + ':LogFile');
        self.logroot.set('testId', testId)
        self.logroot.set('teamId', teamId)
        self.logroot.set('xsi:schemaLocation', SCHEMAS[stype])
        self.logroot.set('xmlns:' + stype, NAMESPACES[stype])
        self.logroot.set('xmlns:xsi', NAMESPACES['xsi'])
        self.logroot.set('count', str(tiCount))
        self.logcount = 0
        self.logentry = {}
        # start logging
        tsentry = et.SubElement(self.logroot, self.ns + ':TestStartTime')
        tsentry.text = self.getTime()
        self.pconsole('%s - starting processing on test %s' % (tsentry.text, testId))
    
    def pconsole(self, msg):
        print >> sys.stderr, msg
    
    def pinfo(self, msg):
        """ For printing messages that go only to the console: NOT to the XML
        file.  automatically prepended with time stamp """
        print >> sys.stderr, u'%s - %s' (self.getTime(), msg)
    
    def start(self, testitem_id):
        # le = et.SubElement(self.logroot, self.ns+':LogEntry')
        # le.set('id',testitem_id)
        # self.logcount += 1
        # record start time
        # logstart = et.SubElement(le, self.ns+':StartTime')
        # logstarttext = self.getTime()
        # self.pconsole("%s - starting processing on %s" % (logstarttext,testitem_id))
        # self.logentry[testitem_id] = le
        pass
    
    def end(self, testitem_id):
        # record end time
        # logend = et.SubElement(self.logentry[testitem_id], self.ns+':EndTime')
        # logendtext = self.getTime()
        # self.pconsole("%s - ending processing on %s" % (logendtext,testitem_id))
        pass
    
    def getTestItemId(self, sId):
        return sId.split(':')[1]
    
    def getTime(self):
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    def writeLogXML(self):
        """ End logging and write out the XML file """
        teentry = et.SubElement(self.logroot, self.ns + ':TestEndTime')
        teentry.text = self.getTime()
        self.pconsole('%s - ended processing on test %s' % (teentry.text, self.testId))
        if self.logcount > 0:
            self.logroot.set('count', str(self.logcount))
        # write out file
        logtree = et.ElementTree(self.logroot)
        logtree.write(self.filename, encoding='UTF-8', xml_declaration=True)


class IARPAResultSetXML:
    """ Class for converting MN JSON to IARPA's ResultSet XML.  Use add methods 
    to insert answers of the relevant type.
    
    """
    def __init__(self, stype, testId, filename='ResultSetFile.xml', teamId='ICSI'):
        """ Initialize instance
        
        :param stype: test type ['metad','metam','metas','metaa']
        :type stype: str
        :param testId: test identifier
        :type testId: str
        :param filename: resultset output file name
        :type filename: str
        :param teamId: team identifier
        :type teamId: str
        
        """
        et.register_namespace(stype, NAMESPACES[stype])
        et.register_namespace('xsi', NAMESPACES['xsi'])
        
        self.ns = stype
        self.filename = filename
        self.rsroot = et.Element(stype + ':ResultSet');
        self.rsroot.set('testId', testId)
        self.rsroot.set('teamId', teamId)
        self.rsroot.set('xsi:schemaLocation', SCHEMAS[stype])
        self.rsroot.set('xmlns:' + stype, NAMESPACES[stype])
        self.rsroot.set('xmlns:xsi', NAMESPACES['xsi'])
        self.rscount = 0


    def addLM(self, testItemId, sentId, targetText, sourceText):
        if self.ns != 'metad':
            raise Exception('Attempt to add LM to non-metad type XML')
        result = et.SubElement(self.rsroot, 'metad:Result')
        result.set('testItemId', testItemId)
        result.set('sentenceId', sentId)
        rstarget = et.SubElement(result, 'metad:LmTargetText')
        rstarget.text = targetText
        rssource = et.SubElement(result, 'metad:LmSourceText')
        rssource.text = sourceText
        self.rscount += 1
    
    def addMapping(self, testItemId, targetId, sourceIdList):
        if self.ns != 'metam':
            raise Exception('Attempt to add Mapping to non-metam type XML')
        result = et.SubElement(self.rsroot, 'metam:Result')
        result.set('testItemId', testItemId)
        for sourceId in sourceIdList:
            rstarget = et.SubElement(result, 'metam:SourceId')
            rstarget.text = sourceId
        rssource = et.SubElement(result, 'metam:TargetId')
        rssource.text = targetId
        self.rscount += 1
        
    def addSource(self, testItemId, sourceId, dimensionId):
        if self.ns != 'metas':
            raise Exception('Attempt to add Source to non-metas type XML')
        result = et.SubElement(self.rsroot, 'metas:Result')
        result.set('testItemId', testItemId)
        rstarget = et.SubElement(result, 'metas:SourceId')
        rstarget.text = sourceId
        rssource = et.SubElement(result, 'metas:DimensionId')
        rssource.text = dimensionId
        self.rscount += 1
    
    def addAffect(self, testItemId, affect):
        if self.ns != 'metaa':
            raise Exception('Attempt to add Affect to non-metaa type XML')
        # note: 999 is the default affect
        if affect == 999:
            polarity = 'XXX'
        else:
            if affect > 0:
                polarity = 'POS'
            elif affect < 0:
                polarity = 'NEG'
            else:
                polarity = 'NEUT'
                affect = 1
        intensity = str(abs(affect))
        result = et.SubElement(self.rsroot, 'metaa:Result')
        result.set('testItemId', testItemId)
        rstarget = et.SubElement(result, 'metaa:LmAffectPolarity')
        rstarget.text = polarity
        rssource = et.SubElement(result, 'metaa:LmAffectIntensity')
        rssource.text = intensity
        self.rscount += 1
        
    def writeResultSetXML(self):
        """ Write out result set XML file """
        self.rsroot.set("count", str(self.rscount))
        rstree = et.ElementTree(self.rsroot)
        rstree.write(self.filename, encoding='UTF-8', xml_declaration=True)

# ===============================================================================
#
# Supporting Classes Below
#
# ===============================================================================

class MetaDTestSetXMLHandler(sax.ContentHandler):
    """
    Converts IARPA m4detect TestSets to MN JSON documents.
    Each TestSet file will produce 1 json file with multiple documents
    
    """
    sep = u':'
    
    def __init__(self):
        sax.ContentHandler.__init__(self)

    def initTestSet(self, tsId=""):
        self.testSetId = tsId
        self.testItemId = ""
        self.sId = ""
        self.testItemLang = ""
        self.testItemCount = 0
        self.str_list = []
        self.sentences = []
        self.documents = []
        self.sIndex = -1  # used to populate sentence index (in json file)
        self.defaultLang = None        

    def startElementNS(self, name, qname, attributes):
        (namespace, localname) = name
        if localname == u'TestSet':
            self.initTestSet(attributes.getValueByQName(u'testId'))
        elif localname == u'TestItem':
            self.testItemId = attributes.getValueByQName(u'id')
            self.testItemLang = attributes.getValueByQName(u'lang')
            if not self.defaultLang:
                self.defaultLang = self.testItemLang
            self.testItemCount = int(attributes.getValueByQName(u'count'))
            self.sId = ""
        elif localname == u'S':
            self.sId = attributes.getValueByQName(u'id')
            self.str_list = []
        return

    def normalizeText(self, textstr):
        textstr = re.sub(ur'[\r\n\t]', u' ', textstr.strip())
        textstr = re.sub(ur' {2,}', u' ', textstr)
        return textstr

    def endElementNS(self, name, qname):
        (namespace, localname) = name
        if localname == u'S':
            self.sIndex += 1
            sentelem = mnjson.getJSONSentence(self.generateSentenceId(),
                                              self.sIndex,
                                              self.normalizeText(u''.join(self.str_list)))
            self.sentences.append(sentelem)
            self.sId = ""
        elif localname == u'TestItem':
            docId = self.sep.join([self.testSetId, self.testItemId])
            docH = mnjson.getJSONDocumentHeader(docId,
                                               self.testSetId,
                                               self.testItemId,
                                               docId,
                                               'unk',
                                               self.testItemCount,
                                               self.testItemLang)
            self.documents.append(docH)
            
 
    def characters(self, content):
        # save content only in case of S element
        if self.sId != "":
            self.str_list.append(content)

    def generateSentenceId(self):
        return self.sep.join([self.testSetId,
                              self.testItemId,
                              self.sId]);

    def getJSON(self):
        jdata = mnjson.getJSONRoot(lang=self.defaultLang,
                                   docs=self.documents,
                                   sents=self.sentences)
        return jdata

    def getTestSetId(self):
        return self.testSetId

    def getTestItemId(self, sId):
        return sId.split(self.sep)[1]
    
    def getTestItemSentenceIds(self, sId):
        parts = sId.split(self.sep)
        return (parts[1], parts[2])
    
    def getTestItemCount(self):
        return self.testItemCount
    
class MetaATestSetXMLHandler(sax.ContentHandler):
    """
    Converts IARPA m4affect TestSets to MN JSON
    Each TestSet file will produce 1 json file with 1 document.
    
    """
    sep = u':'
    
    def __init__(self):
        sax.ContentHandler.__init__(self)

    def initTestSet(self, tsId=""):
        self.testSetId = tsId
        self.testItemCount = 0
        self.testItemId = ""
        self.documents = []
        self.sentences = []
        self.sIndex = -1  # used to populate sentence index (in json file)
        self.defaultLang = None        
        self.str_list = []
        self.lm_str_list = None

    def initTestItem(self, tiId="", tiLang=""):
        self.testItemId = tiId
        self.testItemLang = tiLang
        self.lm = {'source':{},
                   'target':{}}
        self.str_list = []
        self.lm_str_list = None

    def startElementNS(self, name, qname, attributes):
        (namespace, localname) = name
        if localname == u'TestSet':
            self.initTestSet(attributes.getValueByQName(u'testId'))
            self.testItemCount = attributes.getValueByQName(u'count')
        elif localname == u'TestItem':
            self.initTestItem(attributes.getValueByQName(u'id'),
                              attributes.getValueByQName(u'lang'))
            if not self.defaultLang:
                self.defaultLang = self.testItemLang
        elif localname == u'LmSource':
            self.processLmStart('source')
        elif localname == u'LmTarget':
            self.processLmStart('target')
        return

    def processLmStart(self, domain):
        # Execute at the start of an <LmTarget> or <LmSource> block
        # records start index
        preText = u''.join(self.str_list).lstrip()
        self.lm[domain]['start'] = len(preText)
        self.str_list = [preText]
        self.lm_str_list = []            
        
    def processLmEnd(self, domain):
        # execute at the start of an <LmTarget> or <LmSource> block
        # computes end index, saves the form
        form = u''.join(self.lm_str_list)
        self.lm_str_list = None
        self.lm[domain]['form'] = form
        self.lm[domain]['end'] = self.lm[domain]['start'] + len(form)
        self.str_list.append(form)

    def endElementNS(self, name, qname):
        (namespace, localname) = name
        if localname == u'LmTarget':
            self.processLmEnd('target')
        elif localname == u'LmSource':
            self.processLmEnd('source')
        elif localname == u'TestItem':
            self.sIndex += 1
            sentelem = mnjson.getJSONSentence(self.generateSentenceId(),
                                              self.sIndex,
                                              u''.join(self.str_list).rstrip())
            # assumption: each sentence has 1 lm
            sentelem['lms'] = [self.lm]
            self.sentences.append(sentelem)
            self.str_list = None
        elif localname == u'TestSet':
            docId = self.sep.join([self.testSetId, self.testItemId])
            docH = mnjson.getJSONDocumentHeader(self.testSetId,
                                               self.testSetId,
                                               self.testSetId,
                                               self.testSetId,
                                               'unk',
                                               self.testItemCount,
                                               self.testItemLang)
            self.documents.append(docH)
            
 
    def characters(self, content):
        # save content into lm_str_list or str_list depending on
        # which is not None
        if self.lm_str_list != None:
            self.lm_str_list.append(content)
        elif self.str_list != None:
            self.str_list.append(content)

    def generateSentenceId(self):
        return self.sep.join([self.testSetId,
                              self.testItemId]);

    def getJSON(self):
        jdata = mnjson.getJSONRoot(lang=self.defaultLang,
                                   docs=self.documents,
                                   sents=self.sentences)
        return jdata

    def getTestSetId(self):
        return self.testSetId
    
    def getTestItemId(self, sId):
        return sId.split(self.sep)[1]

    def getTestItemCount(self):
        return self.testItemCount

class MetaMTestSetXMLHandler(MetaDTestSetXMLHandler, MetaATestSetXMLHandler):
    """
    Converts IARPA m4mapping TestSets to MN JSON.
    Each TestSet file will produce 1 json file with 1 document.
    Inherits and extends MetaATestSetXMLHandler: parsing of
    SourceList and TargetList elements.
    
    """
    
    def initTestSet(self, tsId=""):
        MetaDTestSetXMLHandler.initTestSet(self, tsId)
        MetaATestSetXMLHandler.initTestSet(self, tsId)
        # dict from Names to Id
        self.sourceList = None
        self.targetList = None
        # dict from Id to Names
        self.sourceIdList = None
        self.targetIdList = None

    def startElementNS(self, name, qname, attributes):
        MetaDTestSetXMLHandler.startElementNS(self, name, qname, attributes)
        (namespace, localname) = name
        if localname == u'LmSentence':
            self.sId = attributes.getValueByQName(u'id')
            self.str_list = []
            self.lm = {'source':{},
                       'target':{}}
            self.lm_str_list = None
        elif localname == u'LmSource':
            self.processLmStart('source')
        elif localname == u'LmTarget':
            self.processLmStart('target')
        elif localname == u'SourceList':
            self.sourceList = {}
            self.sourceIdList = {}
        elif localname == u'TargetList':
            self.targetList = {}
            self.targetIdList = {}
        elif localname == u'Source':
            self.sourceList[attributes.getValueByQName(u'name')] = attributes.getValueByQName(u'id')
            self.sourceIdList[attributes.getValueByQName(u'id')] = attributes.getValueByQName(u'name')
        elif localname == u'Target':
            self.targetList[attributes.getValueByQName(u'name')] = attributes.getValueByQName(u'id')
            self.targetIdList[attributes.getValueByQName(u'id')] = attributes.getValueByQName(u'name')
        return
    
    def endElementNS(self, name, qname):
        MetaDTestSetXMLHandler.endElementNS(self, name, qname)
        (namespace, localname) = name
        if localname == u'LmTarget':
            self.processLmEnd('target')
        elif localname == u'LmSource':
            self.processLmEnd('source')
        elif localname == u'LmSentence':
            self.sIndex += 1
            sentelem = mnjson.getJSONSentence(self.generateSentenceId(),
                                              self.sIndex,
                                              self.normalizeText(u''.join(self.str_list)))
            # assumption: each sentence has 1 lm
            sentelem['lms'] = [self.lm]
            self.sentences.append(sentelem)
            self.str_list = None
            self.sId = ""
        return
    
    def characters(self, content):
        MetaATestSetXMLHandler.characters(self, content)
    
    def getTargetList(self):
        return self.targetList
    
    def getSourceList(self):
        return self.sourceList
    
    def getTargetIdList(self):
        return self.targetIdList    

    def getSourceIdList(self):
        return self.sourceIdList

class MetaSTestSetXMLHandler(MetaMTestSetXMLHandler):
    """
    Converts IARPA m4source TestSets to MN JSON.
    Each TestSet file will produce 1 json file with 1 document.
    Inherits from MetaMTestSetXMLHandler and extends-- to parse
    Subdimensions for sources
    
    """
    def initTestSet(self, tsId=""):
        MetaMTestSetXMLHandler.initTestSet(self, tsId)
        self.testItemSourceConcept = None
        self.testItemTargetConcept = None
        self.currentSource = None
        self.currentSourceId = None
        self.dimension = {}
        
    def startElementNS(self, name, qname, attributes):
        MetaMTestSetXMLHandler.startElementNS(self, name, qname, attributes)
        (namespace, localname) = name
        if localname == 'TestItem':
            self.testItemTargetConcept = attributes.getValueByQName(u'targetId')
            self.testItemSourceConcept = attributes.getValueByQName(u'sourceId')
            self.lm['target']['concept'] = self.targetIdList[self.testItemTargetConcept]
            self.lm['source']['concept'] = self.sourceIdList[self.testItemSourceConcept]
        elif localname == 'Source':
            self.currentSource = attributes.getValueByQName(u'name')
            self.currentSourceId = attributes.getValueByQName(u'id')
        elif localname == 'Dimension':
            dName = '%s.%s' % (self.currentSource, attributes.getValueByQName('name'))
            dId = '%s.%s' % (self.currentSourceId, attributes.getValueByQName('id'))
            self.dimension[dName] = dId
    
    def getDimensions(self):
        return self.dimension


