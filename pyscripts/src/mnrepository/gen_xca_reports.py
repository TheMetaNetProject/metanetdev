#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
.. module:: gen_xca_reports
    :platform: Unix
    :synopsis: Generate XCA excel reports from GMR database

Uses the :mod:`xlsxwriter` module to generate a XCA report according to IARPA's
requirements alongside the 3.1 version of the GMR.  This report includes
charts as well as tables of numbers.  It generates both the general and
case study reports.

.. moduleauthor:: Jisup <jhong@icsi.berkeley.edu>

"""
import sys, re, logging, pprint, argparse, setproctitle, time, operator, string, collections
from decimal import Decimal
import xlsxwriter
import gmrdb
from mnformats.xlsxwrapper import XlsxWrapper

class XCAReports(XlsxWrapper):
    """ Class for generating XCA reports for the v3.1 GMR precisely according to
    IARPA's example file. Updated to generate reports for the case study.
    """
    dimname = {'EN':'English',
               'ES':'Spanish',
               'FA':'Persian',
               'RU':'Russian',
               'INDO': 'INDIVIDUAL_OVERSIGHT',
               'GOVO': 'GOVERNMENT_OVERSIGHT',
               'GEN': 'GENERAL'}
        
    def __init__(self, gdb, outfname, casemode=False):
        """
        :param gdb: GMR database connection
        :type gdb: :class:`gmrdb.GMRDB`
        :param outfname: output filename
        :type outfname: str
        """
#        super(XlsxWrapper,self).__init__(outfname)  
        XlsxWrapper.__init__(self,outfname)
        self.logger = logging.getLogger(__name__)
        self.gdb = gdb
        self.lmcounts = {} # per lang, per cm source, (lm count, %)
        self.casemode = casemode
        if casemode:
            self.langs = ['EN']
            self.prots = ['INDO','GOVO']
        else:
            self.langs = ['EN','ES','FA','RU']
            self.prots = []
        
    def addSheetHeader(self, ws, reportTitle):
        """ Used to write out the first three lines of every sheet, which have the same
        form and concent.
        :param ws: worksheet
        :type ws: :class:`xlsxwriter.WorkSheet`
        :param reportTitle: title of the sheet
        :type reportTitle: str
        """
        ws.write_row(0,0,['Report',reportTitle])
        ws.write_row(1,0,['Team','ICSI'])
        ws.write_row(2,0,['Date',time.strftime("%m/%d/%Y")])
        return 3
           
    def genLMCounts(self, lang, prot=None):
        """ Create a LM_Counts sheet in the workbook for the given language.  This sheet
        contains counts of LMs per source concept, and includes pie charts.
        :param lang: language
        :type lang: str
        :param prot: protagonist that it is generating for
        :type prof: str
        """
        if prot:
            protagonist = self.dimname[prot]
            label = "Protagonist"
        else:
            prot = lang
            protagonist = None
            label = "Language"
        self.logger.info('generating CM Source/LM Counts (Ranked) for %s',prot)
        sheetname = "%s_LM_Counts" % (prot)
        ws = self.wb.add_worksheet(sheetname)
        irow = self.addSheetHeader(ws,'Single %s: CM Source/LM Counts (Ranked)' % (label))
        self.lmcounts[prot] = {}
        tconcount = 0
        for tcon in self.gdb.getTargetConcepts():
            cmsources = self.gdb.getCMSourcesFromTarget(lang,tcon,protagonist) # returns only prot CMs
            cmrows = []
            for scon in cmsources:
                # should this count all the LMs, or only the ones marked for that prot?
                lmcount = self.gdb.getCountLMsFromTargetSource(lang,tcon,scon,protagonist)
                cmrows.append([scon.source_concept,lmcount,Decimal(0),Decimal(0)])
            cmrows.sort(key=lambda row: row[1],reverse=True)
            tconcount += 1
            lmcountsbycmsource = {}
            tconstartrow = irow
            irow = self.addRow(ws, irow, 'Target', tcon.target_concept)
            irow = self.addRow(ws, irow, label, prot)
            irow += 1
            totallmcount = sum(row[1] for row in cmrows)
            cumpercentage = Decimal(0)
            for cmrow in cmrows:
                cmrow[2] = cmrow[1] / Decimal(totallmcount)
                cumpercentage += cmrow[2]
                cmrow[3] = cumpercentage
            irow = self.addRow(ws, irow, 'No. Sources', len(cmrows))
            irow = self.addRow(ws, irow, 'No. LMs', totallmcount)
            irow += 1
            irow = self.addRow(ws, irow, 'CM Source', '#LMs', '%LMs', '%Cum')
            targetdata_start_row = irow
            for cmrow in cmrows:
                irow = self.addRow(ws, irow, cmrow[0], int(cmrow[1]), float(cmrow[2]), float(cmrow[3]))
                lmcountsbycmsource[cmrow[0]] = (int(cmrow[1]),float(cmrow[2]))
            targetdata_end_row = irow - 1
            targetdata_column = 1
            targetdata_labels = 0
            irow += 2
            self.lmcounts[prot][tcon.target_concept] = lmcountsbycmsource
            if targetdata_end_row >= targetdata_start_row:
                self.logger.info('Creating CM Source/LM Counts chart for %s in %s',tcon.target_concept,prot)
                valstring = '=%s!%s:%s' % (sheetname,
                                           self.getCoord(targetdata_start_row, targetdata_column),
                                           self.getCoord(targetdata_end_row, targetdata_column))
                catstring = '=%s!%s:%s' % (sheetname,
                                           self.getCoord(targetdata_start_row, targetdata_labels),
                                           self.getCoord(targetdata_end_row, targetdata_labels))
                chart = self.wb.add_chart({'type':'pie'})
                chart.add_series({'categories': catstring,
                                  'values': valstring,
                                  'points': [],
                                  })
                chart.set_size({'width':720,'height':500})
                chart.set_style(18)
                ws.insert_chart(self.getCoord(tconstartrow, 5, fix=False),chart)
            
    def genXDimLMCountsAlpha(self):
        """ Adds a sheet containing counts of LMs across the languages, with CM sources
        sorted alphabetically.  It includes a bar chart.
        """
        if self.casemode:
            label = "Protagonist"
            lab = "Prot"
            dimensions = self.prots
        else:
            label = "Language"
            lab = "Lang"
            dimensions = self.langs
        self.logger.info('generating X%s LM Counts (Alpha)',lab)
        sheetname = "X%s_LMCounts(Alpha)" % (lab)
        ws = self.wb.add_worksheet(sheetname)
        irow = self.addSheetHeader(ws,'Cross-%s: CM Source/LM Counts (Alphabetic)' % (label))
        for tcon in self.gdb.getTargetConcepts():
            tconstartrow = irow
            irow = self.addRow(ws, irow, 'Target', tcon.target_concept)
            irow += 2
            # get all the source concepts for all languages
            cmsourceset = set()
            lheaders = []
            for dim in dimensions:
                if dim in self.lmcounts:
                    cmsourceset |= set(self.lmcounts[dim][tcon.target_concept].keys())
                lheaders.append('')
                lheaders.append(self.dimname[dim])
            xdimrows = []
            for cmsource in sorted(list(cmsourceset)):
                xdimrow = [cmsource]
                for dim in dimensions:
                    try:
                        lmcount, lmperc = self.lmcounts[dim][tcon.target_concept][cmsource]
                        xdimrow.append(lmcount)
                        xdimrow.append(lmperc)
                    except KeyError:
                        xdimrow.append(Decimal('0'))
                        xdimrow.append(Decimal('0.0000'))
                xdimrows.append(xdimrow)
            irow = self.addRow(ws,irow,lheaders)
            l2headers = ['CM Source']
            for _ in dimensions:
                l2headers.extend(['#LMs','%LMs'])
            irow = self.addRow(ws,irow,l2headers)
            startrow = irow
            for xdimrow in xdimrows:
                irow = self.addRow(ws,irow,xdimrow)
            endrow = irow - 1
            catcol = 0
            irow += 3
            # add chart
            chart = self.wb.add_chart({'type':'column'})
            for idx,dim in enumerate(dimensions):
                datacol = 2*(idx+1)
                chart.add_series({'name':self.dimname[dim],
                                  'categories':'=%s!%s:%s'%(sheetname,
                                                            self.getCoord(startrow,catcol),
                                                            self.getCoord(endrow,catcol)),
                                  'values':'=%s!%s:%s'%(sheetname,
                                                        self.getCoord(startrow, datacol),
                                                        self.getCoord(endrow,datacol)),
                                  })
            chart.set_title({'name':'Cross-%s: CM Source LM Percentages (%s)'%(label,tcon.target_concept)})
            chart.set_style(18)
            chart.set_size({'width':1500,'height':600})
            ws.insert_chart(self.getCoord(tconstartrow, 10, fix=False),
                            chart,
                            {'x_offset':1, 'y_offset': 1})
  
    def genXDimLMCountsRanked(self):
        """ Adds a sheet with Sources ranked by LM counts, per dimension (language or protagonist).
        """
        if self.casemode:
            label = "Protagonist"
            lab = "Prot"
            dimensions = self.prots
        else:
            label = "Language"
            lab = "Lang"
            dimensions = self.langs
        self.logger.info('generating X%s LM Counts (Ranked)',lab)
        ws = self.wb.add_worksheet("X%s_LMCounts(Ranked)"%(lab))
        irow = self.addSheetHeader(ws,'Cross-%s: CM Source/LM Counts (Ranked)'%(label))
        lheaders = []
        for dim in dimensions:
            lheaders.append(self.dimname[dim])
            lheaders.append("#LMs")
            lheaders.append("")
        for tcon in self.gdb.getTargetConcepts():
            irow = self.addRow(ws, irow, 'Target', tcon.target_concept)
            irow += 2
            irow = self.addRow(ws,irow,lheaders)
            rowstartpos = irow
            highestendrowpos = irow
            for idx,dim in enumerate(dimensions):
                irow = rowstartpos
                colpos = 3*idx
                lmcounts = self.lmcounts[dim][tcon.target_concept]
                cmsourcelist = sorted(lmcounts.keys(),key=lambda x:lmcounts[x][0],
                                      reverse=True)
                for cmsource in cmsourcelist:
                    irow = self.addRowAt(ws,irow,colpos,cmsource,lmcounts[cmsource][0])
                if irow > highestendrowpos:
                    highestendrowpos = irow
            irow = highestendrowpos + 3
    
    def genCMDomainDistribution(self, lang=None):
        """ Adds a sheet that show for all the languages how many CMs there are per target
        concept, for each target domain.  Includes pie charts.
        :param lang: language must be specified in case mode
        :type lang: str
        """
        if self.casemode:
            dimensions = self.prots
        else:
            dimensions = self.langs
        self.logger.info('generating CM domain distribution')
        sheetname = "CM_DomainDistribution"
        ws = self.wb.add_worksheet(sheetname)
        irow = self.addSheetHeader(ws,'Conceptual Domain: CM Target/LM Counts')
        header1 = ['', '']
        header2 = ['CM Target','Owner']
        for dim in dimensions:
            header1.append('#CMs')
            header2.append(self.dimname[dim])
        tconbydom = {}
        for tcon in self.gdb.getTargetConcepts():
            if self.casemode:
                if tcon.case_concept not in tconbydom:
                    tconbydom[tcon.case_concept] = []
                tconbydom[tcon.case_concept].append(tcon)
            else:
                if tcon.cultural_concept not in tconbydom:
                    tconbydom[tcon.cultural_concept] = []
                tconbydom[tcon.cultural_concept].append(tcon)
        tconcol = 0
        dimdataoffset = 2
        pie_offsets = {'EN': (0, 0),
                       'ES': (13,0),
                       'FA': (0,6),
                       'RU': (13,6),
                       'INDO': (0, 0),
                       'GOVO': (13, 0)}
        for tdom in sorted(tconbydom.keys()):
            tdomstartrow = irow
            irow = self.addRow(ws, irow, 'Domain', tdom)
            irow += 2
            irow = self.addRow(ws, irow, header1)
            irow = self.addRow(ws, irow, header2)
            datastartrow = irow
            for tcon in tconbydom[tdom]:
                tconrow = [tcon.target_concept,tcon.target_owner]
                if self.casemode:
                    for dim in dimensions:
                        tconrow.append(int(self.gdb.getCMCountByTargetConceptLang(tcon,lang,self.dimname[dim])))
                else:
                    for dim in dimensions:
                        tconrow.append(int(self.gdb.getCMCountByTargetConceptLang(tcon,dim)))
                irow = self.addRow(ws, irow, tconrow)
            dataendrow = irow-1
            irow += 20  
            for idx,dim in enumerate(dimensions):
                self.logger.info('Creating CM domain dist chart for %s in %s',tdom,dim)
                datacol = dimdataoffset+idx
                valstring = '=%s!%s:%s' % (sheetname,
                                           self.getCoord(datastartrow, datacol),
                                           self.getCoord(dataendrow, datacol))
                catstring = '=%s!%s:%s' % (sheetname,
                                           self.getCoord(datastartrow, tconcol),
                                           self.getCoord(dataendrow, tconcol))
                chart = self.wb.add_chart({'type':'pie'})
                chart.add_series({'categories': catstring,
                                  'values': valstring,
                                  'points': [],
                                  })
                chart.set_title({'name': self.dimname[dim]})
                chart.set_size({'width':300,'height':200})
                chart.set_style(18)
                ws.insert_chart(self.getCoord(tdomstartrow + pie_offsets[dim][0],
                                              7 + pie_offsets[dim][1], fix=False),chart)
                
            
        
    def genLexicalCounts(self, lang, prot=None):
        """ Adds a sheet with counts of all the source lexical items in the given language.
        :param lang: language
        :type lang: str
        """
        if prot:
            protagonist = self.dimname[prot]
            label = "Protagonist"
        else:
            prot = lang
            protagonist = None
            label = "Language"
        self.logger.info("generating Lexical Counts for %s",prot)
        ws = self.wb.add_worksheet("%s_Lexical_Counts" % (prot))
        irow = self.addSheetHeader(ws,'Single %s: CM Source/LM Source Lexical Counts' % (label))
        
        for tcon in self.gdb.getTargetConcepts():
            irow = self.addRow(ws, irow, 'Target', tcon.target_concept)
            irow = self.addRow(ws, irow, label, prot)
            irow += 1
            cmsources = self.gdb.getCMSourcesFromTarget(lang,tcon,protagonist)
            lexcountrows = []
            mincount = 2000000000
            for scon in cmsources:
                sconlexrows = self.gdb.getCMLexicalCounts(lang,tcon,scon,protagonist)
                for slrow in sconlexrows:
                    lexcountrows.append([scon.source_concept,slrow.lm_source_lemma,slrow.count])
                    if slrow.count < mincount:
                        mincount = slrow.count
            if not lexcountrows:
                mincount = 0
            irow = self.addRow(ws, irow, 'Minimum LM Count', mincount)
            irow += 1
            irow = self.addRow(ws, irow, 'CM Target','CM Source', 'LM Source', '#Occurences')
            lexcountrows.sort(key=operator.itemgetter(0,1))
            for lexrow in lexcountrows:
                irow = self.addRow(ws, irow, tcon.target_concept, lexrow[0], lexrow[1], lexrow[2])
            irow += 2
    
    def genSchemaRanks(self, lang, prot=None):
        """ Adds a sheet with top 5 source schemas for each target schema in terms of LM counts.
        :param lang: language
        :type lang: str
        :param prot: protagonist to generate ranks for
        :type prot: str
        """
        if prot:
            protagonist = self.dimname[prot]
            label = "Protagonist"
        else:
            prot = lang
            protagonist = None
            label = "Language"
        self.logger.info("generating Schema Counts for %s",prot)
        ws = self.wb.add_worksheet("%s_Schema_Counts" % (prot))
        irow = self.addSheetHeader(ws,'Single %s: Target Schema/Source Schema LM Counts'%(label))
        
        lms = self.gdb.getLMsFromLang(lang,protagonist)
        tscounts = {}
        for lm in lms:
            targetschema, sourceschemas = self.gdb.getLMProperties(lm)
            if targetschema not in tscounts:
                tscounts[targetschema] = {}
            for sourceschema in sourceschemas:
                if sourceschema not in tscounts[targetschema]:
                    tscounts[targetschema][sourceschema] = 1
                else:
                    tscounts[targetschema][sourceschema] += 1
        for tschema in sorted(tscounts.keys()):
            irow = self.addRow(ws, irow, 'Target schema', tschema)
            irow += 1
            irow = self.addRow(ws, irow, 'Source schema', '#LMs')
            for sschema, lmcount in collections.Counter(tscounts[tschema]).most_common(5):
                irow = self.addRow(ws, irow, sschema, lmcount)
            irow += 2
        
def main():
    """ Command for generating the XCA reports.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate XCA Reports Spreadsheet (Excel xlsx)")
    parser.add_argument('outputfilebase',help='Output filename base (xlsx extension will be added)')
    parser.add_argument('--gdb-user',dest='gdbuser',default='gmruser',
                        help='GMR database username')
    parser.add_argument('-p','--gdb-pw',dest='gdbpw',default=None,required=True,
                        help='GMR database password')
    parser.add_argument('--gdb-name',dest='gdbname',default='icsi_'+time.strftime("%Y%m%d"),
                        help='GMR database name')
    parser.add_argument('--case-mode',dest='casemode',action='store_true',
                        help="Run in case study mode")
    parser.add_argument('-v','--verbose',help='Verbose messages',
                        action='store_true')
    parser.add_argument('-t1','--tier1',help='Generate tier 2 reports only',
                        action='store_true')
    parser.add_argument('-t2','--tier2',help='Generate tier 2 reports only',
                        action='store_true')
    cmdline = parser.parse_args()
    
    # hide the password entered as a paramater (from top / ps)
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(-p|--gdb-pw)(=|\s+)(\S+)',ur'\1\2XXXX',pstr)
    setproctitle.setproctitle(pstr)

    logLevel = logging.WARN
    if cmdline.verbose:
        logLevel = logging.INFO
    logging.basicConfig(level=logLevel,
                        format='%(asctime)s %(levelname)s %(message)s')
    
    if cmdline.casemode:
        gdb = gmrdb.GMRDBCase(socket='/tmp/mysql.sock',
                                 user=cmdline.gdbuser,
                                 passwd=cmdline.gdbpw,
                                 dbname=cmdline.gdbname)
    else:
        gdb = gmrdb.GMRDBGeneral(socket='/tmp/mysql.sock',
                                 user=cmdline.gdbuser,
                                 passwd=cmdline.gdbpw,
                                 dbname=cmdline.gdbname)
    
    if not cmdline.tier2:
        # generate tier1 report
        report = XCAReports(gdb, cmdline.outputfilebase+'-tier1.xlsx',casemode=cmdline.casemode)
        if cmdline.casemode:
            for prot in report.prots:
                report.genLMCounts('EN', prot)
                report.genLexicalCounts('EN', prot)
        else:
            for lang in report.langs:
                report.genLMCounts(lang)
                report.genLexicalCounts(lang)
        report.genXDimLMCountsAlpha()
        report.genXDimLMCountsRanked()
        if cmdline.casemode:
            report.genCMDomainDistribution('EN')
        else:
            report.genCMDomainDistribution()
        report.saveWb()

    if not cmdline.tier1:
        report2 = XCAReports(gdb, cmdline.outputfilebase+'-tier2.xlsx',casemode=cmdline.casemode)
        if cmdline.casemode:
            for prot in report2.prots:
                report2.genSchemaRanks('EN', prot)
        else:
            for lang in report2.langs:
                report2.genSchemaRanks(lang)
        report2.saveWb()
        
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    
