#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
.. module:: gen_lm_data
    :platform: Unix
    :synopsis: Generate excel and tab separate format version of the LM data for analysis

Queries the MetaNet internal LM database to generate Excel or tab-separated
text format data for loading into statistical analysis systems.  Because the 
data comes from the internal LM database, it includes information that the GMR
does not, as well as LMs that did not make it into the GMR due to score
cut-off or failure to map to concepts.

.. moduleauthor:: Jisup <jhong@icsi.berkeley.edu>

"""
import sys, re, logging, pprint, argparse, setproctitle, time, operator, string, collections
from decimal import Decimal
import xlsxwriter, codecs
import metanetdb
from mnformats.xlsxwrapper import XlsxWrapper

class LMDBDataGenerator(XlsxWrapper):
    """ Class for generating LM database data into Excel format (as well
    as tab-separated text)
    """
        
    def __init__(self, mdb, outfbase, maketab=False):
        """
        :param mdb: MN LM database connection
        :type mdb: :class:`metanetdb.MetanetLMDB`
        :param outfbase: output filename base, to which extension will be added
        :type outfbase: str
        :param maketab: flag to cause tab-separated version also to be generated
        :type maketab: bool
        """
#        super(XlsxWrapper,self).__init__(outfname)  
        XlsxWrapper.__init__(self,outfbase + '.xlsx')
        self.logger = logging.getLogger(__name__)
        self.mdb = mdb
        self.outputtabfname = outfbase + u'.tab'
        self.maketab = maketab     
           
    def genLMData(self, lang, tconstring=None):
        """ Create a LM_Counts sheet in the workbook for the given language.  This sheet
        contains counts of LMs per source concept, and includes pie charts.
        :param lang: language
        :type lang: str
        :param tconstring: target concept substring
        :type tconstring: str
        """
        if tconstring:
            self.logger.info('generating LM Data for target concept string "%s" for lang %s',tconstring,lang)
            sheetname = "LM_Data_%s_%s" % (lang,tconstring)
        else:
            self.logger.info('generating LM Data for lang %s',lang)
            sheetname = "LM_Data_%s" % (lang)
        ws = self.wb.add_worksheet(sheetname)
        irow = 0
        headerlist = ['LM_instance_id',
            'LM_id',
            'Target concept',
            'Target frame',
            'Target lemma',
            'Construction',
            'Source lemma',
            'Source frame',
            'Source family 1',
            'Source family 2',
            'Source concept',
            'Mapping score',
            'M4city score',
            'Coreness',
            'Map method',
            'CMs',
            'Corpus',
            'Document',
            'Document Type',
            'Protagonist',
            'Sentence_id',
            'Sentence']
        irow = self.addHeaderRow(ws, irow, headerlist)
        M4SCORECOL = 12
        CORENESSCOL = 13
        
        if self.maketab:
            self.tfile = codecs.open(self.outputtabfname,'w',encoding='utf-8')
            print >> self.tfile, u'\t'.join(headerlist)
        
        if tconstring:
            rowtuples = self.mdb.getLMDataByTargetConceptSubString(lang,tconstring)
        else:
            rowtuples = self.mdb.getLMData(lang)
        for row in rowtuples:
            (lmiid, lmid, tconcept, tframeL, tlemma, cxn, slemma, sframeL, sfamilyL,
             sconceptL, smappingstr, score, promrcstr, conmrcstr, cmstr, corpus, docname,
             doctype, perspective, sid, text) = row
            dvec = [corpus, docname, doctype, perspective, sid, text]
            cmlist = []
            if cmstr:
                cmlist = [re.sub(ur'.*#Metaphor_','',cmuri) for cmuri in cmstr.split(u',')]
            else:
                cmlist = ['NULL']
            mappinglist = []
            if smappingstr:
                mappingstrs = smappingstr.split(u';')
                for mapping in mappingstrs:
                    frame, sfamily, sconcept, scoreness, smethod = mapping.split(u'|')
                    if u',' in sfamily:
                        sfam1, sfam2 = sfamily.split(u',',1)
                    else:
                        sfam1 = sfamily
                        sfam2 = 'NULL'
                    if u',' in sconcept:
                        for sconstr in sconcept.split(u','):
                            scon, rankscore = sconstr.split(u':',1)
                            svec = [frame, sfam1, sfam2, scon, rankscore, float(score), float(scoreness), smethod]
                            mappinglist.append(svec)
                    elif sconcept:
                        scon, rankscore = sconcept.split(u':',1)
                        svec = [frame, sfam1, sfam2, scon, rankscore, float(score), float(scoreness), smethod]
                        mappinglist.append(svec)
                    else:
                        svec = [frame, sfam1, sfam2, 'NULL', 'NULL', float(score), float(scoreness), smethod]
                        mappinglist.append(svec)
            if promrcstr:
                promrcstrs = promrcstr.split(u';')
                for mrcstr in promrcstrs:
                    metarc, tframe, sframe, cmstr = mrcstr.split(u'|')
                    cms = cmstr.split(u',')
                    tvec = [lmiid, lmid, tconcept, tframe, tlemma, cxn, slemma]
                    for mvec in mappinglist:
                        if mvec[0] == sframe:
                            for cm in cms:
                                vec = tvec + mvec + [cm] + dvec
                                vec = [item if item else 'NULL' for item in vec]
                                if vec[M4SCORECOL]=='NULL':
                                    vec[M4SCORECOL] = 0.0
                                if vec[CORENESSCOL]=='NULL':
                                    vec[CORENESSCOL] = 0.0
                                irow = self.processRow(ws, irow, vec)
            else:
                tvec = [lmiid, lmid, tconcept, tframeL, tlemma, cxn, slemma]
                for cm in cmlist:
                    for mvec in mappinglist:
                        vec = tvec + mvec + [cm] + dvec
                        vec = [item if item else 'NULL' for item in vec]
                        if vec[M4SCORECOL]=='NULL':
                            vec[M4SCORECOL] = 0.0
                        if vec[CORENESSCOL]=='NULL':
                            vec[CORENESSCOL] = 0.0
                        irow = self.processRow(ws, irow, vec)
                
    def processRow(self, ws, irow, vec):
        """ Process a row of data--add it to the spreadsheet and to the tab-separated
        file.
        :param ws: excel worksheet
        :type ws: :class:`xlsxwriter.WorkSheet`
        :param irow: row number
        :type irow: int
        :param vec: vector with row data
        :type vec: list
        """
        try:
            irow = self.addRow(ws, irow, vec)
        except:
            self.logger.error(u'Error adding row: %s',pprint.pformat(vec))
            raise
        
        if self.maketab:
            print >> self.tfile, u'\t'.join([unicode(item) for item in vec])
        return irow
    
def main():
    """ Command for generating the LM data
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate LM data in Excel xlsx format")
    parser.add_argument('outputfilebase',help='Output filename base (xlsx extension will be added)')
    parser.add_argument('--mdb-name',dest='mdbname',default='metanetlm_'+time.strftime("%Y%m%d"),
                        help='MN DB database name')
    parser.add_argument('-l','--lang',help='Language',
                        default='en')
    parser.add_argument('-v','--verbose',help='Verbose messages',
                        action='store_true')
    parser.add_argument('-t', '--tab', help='Also generate a tab separated file',
                        action="store_true")
    parser.add_argument('--tcon',dest='tconstring',
                        help='Target concept substring to generate data from, e.g. GUN')
    cmdline = parser.parse_args()
    
    logLevel = logging.WARN
    if cmdline.verbose:
        logLevel = logging.INFO
    logging.basicConfig(level=logLevel,
                        format='%(asctime)s %(levelname)s %(message)s')
    
    mdb = metanetdb.MetaNetLMDB(socket='/tmp/mysql.sock',
                             user='readonly_user',
                             passwd='readme',
                             dbname=cmdline.mdbname)

    xldata = LMDBDataGenerator(mdb, cmdline.outputfilebase, maketab=cmdline.tab)
    xldata.genLMData(cmdline.lang, cmdline.tconstring)
    xldata.saveWb()
            
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    
