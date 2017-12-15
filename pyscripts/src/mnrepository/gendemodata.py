#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
.. module:: gen_demo_data
    :platform: Unix
    :synopsis: Generate excel format and tab-separated text format data for the demo

Generates Excel and tab-separated text file format versions of the LM data
in the GMR for statistical analysis.  The file is augmented with data from
Metanet internal LM database, so that Tier 2 features can also be included
in the analyses.

.. moduleauthor:: Jisup <jhong@icsi.berkeley.edu>

"""
import sys, re, logging, pprint, argparse, time, operator, string, collections, codecs, os
import xlsxwriter
from decimal import Decimal
from metanetdb import MetaNetLMDB
from gmrdb import GMRDBCase, GMRDBGeneral
from mnformats.mnconfig import MetaNetConfigParser
from mnformats.xlsxwrapper import XlsxWrapper

class GenDemoData():
    """ Class for generate data for the IARPA demo system presented
    in Dec 2014.
    """
        
    def __init__(self, configfname=None, mode=None, dstamp=None,
                 outfbase=None, maketab=False,
                 casemode='case'):
        """
        Initialize the class instance
        :param mdb: MN LM database connection
        :type mdb: :class:`metanetdb.MetanetLMDB`
        :param configfname: configuration filename
        :type configfname: str
        :param mode: configuration mode to read from the config file
        :type mode: str
        :param dstamp: dstamp to use to select matching GMR and LM databases
        :type dstamp: str
        :param outfbase: output filename
        :type outfbase: str
        :param casemode: case or general mode
        :type casemode: str
        """

        self.logger = logging.getLogger(__name__)
                
        MNSYSTEM_CONF = os.environ.get('MNSYSTEM_CONF')
        if configfname:
            cfname = configfname
        elif MNSYSTEM_CONF:
            #cfile = os.environ['MNSYSTEM_CONF']
            cfname = os.environ['MNSYSTEM_CONF']
        else:
            HOME = os.environ.get('HOME')
            if HOME:
                cfname = u'%s/.mnsystem.conf' % (HOME)
            else:
                cfname = u'.mnsystem.conf'
        
        if not dstamp:
            dstamp=time.strftime('%Y%m%d')
        if not outfbase:
            outfbase = 'demo_data_' + dstamp
        
        self.xlwrapper = XlsxWrapper(outfbase + '.xlsx')
        self.outputtabfname = outfbase + u'.tab'
        self.maketab = maketab     

        self.logger.info(u'loading configuration from %s', cfname)
        config = MetaNetConfigParser(cfname,'gendemodata',mode)
        
        gmrsock = config.getValueFromComp('gmrdb','socket',default='/tmp/mysql.sock')
        gmruser = config.getValueFromComp('gmrdb','username',required=True)
        gmrpw = config.getValueFromComp('gmrdb','password',required=True)
        gmrdbbase = config.getValueFromComp('gmrdb','dbnamebase',default='icsi_gmr_')
        
        mnsock = config.getValueFromComp('mndb','socket',default='/tmp/mysql.sock')
        mnuser = config.getValueFromComp('mndb','username',required=True)
        mnpw = config.getValueFromComp('mndb','password',required=True)
        mndbbase = config.getValueFromComp('mndb','dbnamebase',default='metanetlm_')
        
        self.gmrdb = {}
        self.mndb = MetaNetLMDB(socket=mnsock,
                                user=mnuser,
                                passwd=mnpw,
                                dbname=mndbbase+dstamp)
        if casemode=='case':
            self.gmrdb = GMRDBCase(socket=gmrsock,
                                           user=gmruser,
                                           passwd=gmrpw,
                                           dbname=gmrdbbase+dstamp)
        elif casemode=='general':
            self.gmrdb = GMRDBGeneral(socket=gmrsock,
                                          user=gmruser,
                                          passwd=gmrpw,
                                          dbname=gmrdbbase+dstamp)
        self.casemode = casemode
        
    def getLMByConceptGroupQuery(self,lang,congroup):
        """ Returns the queries used to retrieve LM data from the GMR.
        :param lang: language
        :type lang: str
        :param congroup: concept group to query
        :type congroup: str
        """
        if self.casemode == 'case':
            q = \
            u'SELECT lm.id, lm.extid, lm.lm_target, lm.lm_source, lm.protagonist_id, cmt.case_concept,'\
            u'cmt.target_concept, cmt.target_owner, cms.source_concept, cms.source_owner, '\
            u'cm.protagonist_id, lm_sent.url, lm_sent.text FROM lm, cm_target_case as cmt, '\
            u'cm_source as cms, cm_case as cm, lm_sentence as lm_sent, lm2cm_source as lm2cms, '\
            u'lm2cm_target_case as lm2cmt WHERE lm2cmt.lm_id = lm.id AND '\
            u'lm2cmt.cm_target_case_id=cmt.id AND cm.cm_target_case_id = cmt.id AND '\
            u'lm2cms.lm_id=lm.id AND lm2cms.cm_source_id=cms.id AND cm.cm_source_id=cms.id '\
            u'AND lm.lm_sentence_id = lm_sent.id AND cmt.case_concept = "%s" AND cm.language = "%s" '\
            u'AND lm.language = "%s";'
        elif self.casemode == 'general':
            q = \
            u'SELECT lm.id, lm.extid, lm.lm_target, lm.lm_source, lm.protagonist_id, cmt.cultural_concept,'\
            u'cmt.target_concept, cmt.target_owner, cms.source_concept, cms.source_owner, '\
            u'cm.protagonist_id, lm_sent.url, lm_sent.text FROM lm, cm_target_general as cmt, '\
            u'cm_source as cms, cm_general as cm, lm_sentence as lm_sent, lm2cm_source as lm2cms, '\
            u'lm2cm_target_general as lm2cmt WHERE lm2cmt.lm_id = lm.id AND '\
            u'lm2cmt.cm_target_general_id=cmt.id AND cm.cm_target_general_id = cmt.id AND '\
            u'lm2cms.lm_id=lm.id AND lm2cms.cm_source_id=cms.id AND cm.cm_source_id=cms.id '\
            u'AND lm.lm_sentence_id = lm_sent.id AND cmt.cultural_concept = "%s" AND cm.language = "%s" '\
            u'AND lm.language = "%s";'
        return q % (congroup, lang.upper(), lang.upper())    
                
    def getData(self,lang='en',tcongroup='GUN_OVERSIGHT'):
        """ Retrieve the the LM data for the given language and target concept group.
        :param lang: language
        :type lang: str
        :param tcongroup: target concept group
        :type tcongroup: str
        :return: iterator with each row as an LM instance
        :rtype: iterator
        """
        self.lmquery = self.getLMByConceptGroupQuery(lang,tcongroup)
        self.logger.info(u'Query to retrieve LMs from GMR:\n%s',self.lmquery)
        for row in self.gmrdb.execute_sql(self.lmquery):
            (lmid,lmextid,
            tform,sform,
            lmprotid,
            congroup,tcon,tconowner,
            scon,sconowner,
            cmprotid,
            senturl,text) = row
            for irow in self.mndb.getLMFromInstanceID(lmextid).tuples():
                (lmiid,mnlmid,
                tlemma,tschema,slemma,sschemaL,sfamilyL,sconL,
                cxn,smappingstr,
                score,cm,
                corpus,docname,doctype,
                prot,sid) = irow
                yield (lmiid, lmid, tcon, tschema, tlemma, cxn,
                    slemma, sschemaL, sfamilyL, sconL,smappingstr,score,cm,corpus,docname,
                    doctype, prot, sid, text)
    
    def genDataRow(self,ws,irow,row):
        """ Generate a row of output format data (excel/tab-separated) from the
        row vector passed in.
        :param ws: worksheet
        :type ws: :class:xlsxwriter.WorkSheet
        :param irow: row number
        :type irow: int
        :param row: row data vector
        :type row: list
        """
        (lmiid, lmid, tconcept, tschema, tlemma, cxn, slemma, sschemaL, sfamilyL,
         sconceptL, smappingstr, score, cmstr, corpus, docname,
         doctype, perspective, sid, text) = row
        tvec = [lmiid, lmid, tconcept, tschema, tlemma, cxn, slemma]
        dvec = [corpus, docname, doctype, perspective, sid, text]
        self.logger.info('generating row for lm %d and lmi %d', lmid, lmiid)
        cmlist = []
        M4SCORECOL = 12
        CORENESSCOL = 13
        if cmstr:
            cmlist = cmstr.split(u',')
        else:
            cmlist = ['NULL']
        mappinglist = []
        if smappingstr:
            mappingstrs = smappingstr.split(u';')
            for mapping in mappingstrs:
                schema, sfamily, sconcept, scoreness, smethod = mapping.split(u'|')
                if u',' in sfamily:
                    sfam1, sfam2 = sfamily.split(u',',1)
                else:
                    sfam1 = sfamily
                    sfam2 = 'NULL'
                if u',' in sconcept:
                    for sconstr in sconcept.split(u','):
                        scon, rankscore = sconstr.split(u':',1)
                        svec = [schema, sfam1, sfam2, scon, rankscore, float(score), float(scoreness), smethod]
                        mappinglist.append(svec)
                elif sconcept:
                    scon, rankscore = sconcept.split(u':',1)
                    svec = [schema, sfam1, sfam2, scon, rankscore, float(score), float(scoreness), smethod]
                    mappinglist.append(svec)
                else:
                    svec = [schema, sfam1, sfam2, 'NULL', 'NULL', float(score), float(scoreness), smethod]
                    mappinglist.append(svec)
        for cm in cmlist:
            for mvec in mappinglist:
                vec = tvec + mvec + [cm] + dvec
                vec = [item if item else 'NULL' for item in vec]
                if vec[M4SCORECOL]=='NULL':
                    vec[M4SCORECOL] = 0.0
                if vec[CORENESSCOL]=='NULL':
                    vec[CORENESSCOL] = 0.0
                irow = self.processRow(ws, irow, vec)
        return irow 
    
    def genLMData(self, lang='en', tcongroup='GUN_OVERSIGHT', tconstring=None):
        """ Generates the LM data spreadsheet in the two supported formats.
        The LM data is retrieved from the GMR and then each is looked up in the
        MetaNet LM database to add Tier 2 data.  Optionally a tconstring can
        passed in, in which case LMs mapped to target concepts that contain the
        substring in the MetaNet LM database (which were not in the GMR) will
        be appended.
        :param lang: language
        :type lang: str
        :param tcongroup: target concept group
        :type tcongroup: str
        :param tconstring: target concept substring
        :type tconstring: str
        """
        self.logger.info('generating LM Data for target concept group "%s" for lang %s',tcongroup,lang)
        sheetname = "Demo_Data_%s_%s" % (lang,tcongroup)
        ws = self.xlwrapper.wb.add_worksheet(sheetname[0:30])
        irow = 0
        headerlist = ['LM_instance_id',
            'LM_id',
            'Target concept',
            'Target schema',
            'Target lemma',
            'Construction',
            'Source lemma',
            'Source schema',
            'Source family 1',
            'Source family 2',
            'Source concept',
            'Mapping score',
            'M4city score',
            'Coreness',
            'Extactor',
            'Map method',
            'CMs',
            'Corpus',
            'Document',
            'Document Type',
            'Protagonist',
            'Sentence_id',
            'Sentence']
        irow = self.xlwrapper.addHeaderRow(ws, irow, headerlist)
        
        
        if self.maketab:
            self.tfile = codecs.open(self.outputtabfname,'w',encoding='utf-8')
            print >> self.tfile, u'\t'.join(headerlist)
        
        for row in self.getData(lang, tcongroup):
            irow = self.genDataRow(ws,irow,row)

        if tconstring:
            for row in self.mndb.getNullSourceLMDataByTargetConceptSubString(lang,tconstring):
                irow = self.genDataRow(ws,irow,row)
        
    def processRow(self, ws, irow, vec):
        """ Add spreadsheet for data to the sheet and/or print to the tab-separated file.
        :param ws: worksheet
        :type ws: :class:`xlsxwriter.WorkSheet`
        :param irow: row number
        :type irow: int
        :param vec: row data vector
        :type vec: list
        :return: incremented row number
        :rtype: int
        """
        try:
            irow = self.xlwrapper.addRow(ws, irow, vec)
        except:
            self.logger.error(u'Error adding row: %s',pprint.pformat(vec))
            raise
        
        if self.maketab:
            print >> self.tfile, u'\t'.join([unicode(item) for item in vec])
        return irow
    
def main():
    """ Command for generating the LM data for Dec Demo
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate LM data from GMR database, with supplemental frame and "\
            " frame family info from the MetaNet MySQL database. ")
    parser.add_argument('-g','--tcongroup',
                        default='GUN_OVERSIGHT',
                        help='Target concept group to generate data from, e.g. GUN_OVERSIGHT')
    parser.add_argument('-s','--tconstring',
                        default='GUN',
                        help='String to use to retrieve auxiliary data from MNDB')                        
    parser.add_argument('-o','--outputfilebase',
                        default='DemoData_'+time.strftime('%Y%m%d'),
                        help='Output filename base (xlsx extension will be added)')
    parser.add_argument('-d','--dstamp',dest='dstamp',default=time.strftime('%Y%m%d'),
                        help='Datestamp string to use to retrieved matching databases for MN and GMR')
    parser.add_argument('-l','--lang',help='Language',
                        default='en')
    parser.add_argument('-v','--verbose',help='Verbose messages',
                        action='store_true')
    parser.add_argument('-t', '--tab', help='Also generate a tab separated file',
                        action="store_true")
    parser.add_argument('-c', '--config',help='Override configuration file')
    parser.add_argument('-m', '--mode',help='Case mode or general mode',default='case')
    cmdline = parser.parse_args()
    
    logLevel = logging.WARN
    if cmdline.verbose:
        logLevel = logging.INFO
    logging.basicConfig(level=logLevel,
                        format='%(asctime)s %(levelname)s %(message)s')
        
    dgen = GenDemoData(dstamp=cmdline.dstamp,maketab=cmdline.tab,casemode=cmdline.mode,
                       outfbase=cmdline.outputfilebase)
    dgen.genLMData(cmdline.lang,cmdline.tcongroup,cmdline.tconstring)
    dgen.xlwrapper.saveWb()
        
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    
