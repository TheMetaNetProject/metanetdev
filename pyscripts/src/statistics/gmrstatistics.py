#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
.. module:: gmrstatistics
    :platform: Unix
    :synopsis: Generate statistics on recent GMR test and production runs 

Uses the :mod:`xlsxwriter` module to generate a XCA report according to IARPA's
requirements alongside the 3.1 version of the GMR.  This report includes
charts as well as tables of numbers.

.. moduleauthor:: Steve Doubleday  <stevedoubleday@gmail.com>

"""
import sys, re, logging, pprint, argparse, setproctitle, time, operator, string, collections
from decimal import Decimal
import xlsxwriter
from mnrepository import gmrdb
import pickle
# from mnformats.xlsxwrapper import XlsxWrapper

# class Statistics(XlsxWrapper):
class Statistics():
    """ Class for generating gmr statistics 
    """
    dimname = {'EN':'English',
               'ES':'Spanish',
               'FA':'Persian',
               'RU':'Russian',
               'INDO': 'INDIVIDUAL_OVERSIGHT',
               'GOVO': 'GOVERNMENT_OVERSIGHT',
               'GEN': 'GENERAL'}

    def __init__(self, testmode, gmrrun, outputfilebase, runningstats, gdbg, gdbc):
        """
    :param cmdline: command line parameters 
    :type cmdline: parse output from (:mod:argparse)
    :param jdata: MetaNet JSON format data
    :type jdata: dict
    :returns: JSON dict with LMs added
        :param testmode: test=True; production=False
        :param testmode:  boolean 
        :param gmrrun: gmr identifier, formatted yyyy.mm.dd  or yyyy.mm.ddTn if test 
        :type gmrrun: str 
        :param outputfilebase: filename base (including path).  Suffix will be added to create various output files 
        :type outputfilebase: str  
        :param runningstats: file name of pickled dictionary of cumulative statistics; this run will be added 
        :type runningstats: str 
        :param gdbg:  gmr database (General)
        :type  gdbg: class:`gmrdb.GMRDBGeneral`
        :param gdbc: gmr database (Case)
        :type gdbc type: :class:`gmrdb.GMRDBCase`
        """
#         self.xlsfile = outputfilebase+'.xlsx'
        self.picklefile = outputfilebase+'.p'
        self.textfile = outputfilebase+'.txt'
#         XlsxWrapper.__init__(self,self.xlsfile)
        self.logger = logging.getLogger(__name__)
        self.gdbg = gdbg
        self.gdbc = gdbc
        self.gmrrun = gmrrun
        self.lastrun = self.gmrrun
        self.runningstats = runningstats
        self.testmode = testmode
        self.lmcounts = {} # per lang, per cm source, (lm count, %)
        self.langscase = ['EN']
        self.protscase = ['INDO','GOVO']
        self.langs = ['EN','ES','FA','RU']
        self.langsall = self.langs
        self.langsall.append('EN-case')
        self.prots = []
        self.statsdata = {}
        self.deltathreshold = 0.1
 
    def loadCumulativeStatistics(self):
        try: 
            f = open(self.runningstats, 'rb')
            self.statsdata = pickle.load(f)
            f.close
        except: 
            self.logger.info('Error opening file; creating new one: %s',self.runningstats) 
            print('Error opening file; creating new one: ',self.runningstats)
 
    def addRun(self):
        if self.testmode: 
            krun = 'test-runs'
        else: 
            krun = 'prod-runs'
        runs = [] 
        if not krun in self.statsdata:
            self.statsdata[krun] = runs
        runs = self.statsdata[krun]
        if len(runs) > 0:
            self.lastrun = runs[-1]
        present = False
        for run in runs: 
            if run == self.gmrrun: 
                present=True 
        if not present: 
            runs.append(self.gmrrun)
        sortruns = sorted(runs)
        self.statsdata[krun] = sortruns

    def buildConceptCountsForLang(self, lang, gdb, case):
        if case: 
            lang = lang+'-case'
        self.logger.info('generating counts for %s',lang) 
        
        tconcount = 0
        for tcon in gdb.getTargetConcepts():
            cmsources = gdb.getCMSourcesFromTarget(lang,tcon,None) 
            cmrows = []
            for scon in cmsources:
                lmcount = gdb.getCountLMsFromTargetSource(lang,tcon,scon,None)
                cmrows.append(lmcount)
            tconcount += 1
            totallmcount = sum(lmcount for lmcount in cmrows)
            if not tcon.target_concept in self.concepts:
                self.concepts[tcon.target_concept] = {}
            if not lang in self.concepts[tcon.target_concept]: 
                self.concepts[tcon.target_concept][lang] = {}
            self.concepts[tcon.target_concept][lang][self.gmrrun] = {'Sources' : len(cmrows), 'LMs' : totallmcount}
                      
    def buildConceptCounts(self):
        if not 'concepts' in self.statsdata:
            self.statsdata['concepts'] = {}
        self.concepts = self.statsdata['concepts']
        self.logger.info('build counts for run %s',self.gmrrun) 
        self.buildConceptCountsForLang('EN', self.gdbg, False)
        self.buildConceptCountsForLang('ES', self.gdbg, False)
        self.buildConceptCountsForLang('RU', self.gdbg, False)
        self.buildConceptCountsForLang('FA', self.gdbg, False)
        self.buildConceptCountsForLang('EN', self.gdbc, True)
       
            
    def updateCumulativeStats(self):
        self.logger.info('writing the cumulative stats file %s',self.runningstats) 
        try: 
            f = open(self.runningstats, 'wb')
            pickle.dump(self.statsdata, f)
            f.close()
        except: 
            raise
        self.logger.info('writing stats as a backup file for this run %s',self.picklefile) 
        try:     
            f = open(self.picklefile, 'wb')
            pickle.dump(self.statsdata, f)
            f.close()
        except: 
            raise
    
    def buildDeltas(self, lang):
        deltas = []
        for tcon in sorted(list(self.concepts)):
            try: 
                newrun = self.concepts[tcon][lang][self.gmrrun]
                source = newrun['Sources']  
                lms = newrun['LMs']
                newkey = True  
            except KeyError:
                source = 0
                lms = 0
            try: 
                lastrun = self.concepts[tcon][lang][self.lastrun]
                lastsource = lastrun['Sources']  
                lastlms = lastrun['LMs']
                lastkey = True  
            except KeyError:
                lastsource = 0
                lastlms = 0
            delta = [tcon, source, lastsource, Decimal(0), lms, lastlms, Decimal(0)]
            self.logger.info('concept %s lang %s new-s %d new-lm %d old-s %d old-lm %d',tcon, lang, source, lms, lastsource, lastlms) 
#             print('concept %s lang %s new-s %d new-lm %d old-s %d old-lm %d',tcon, lang, source, lms, lastsource, lastlms) 
            def buildField(field, lastfield):
                isdelta = False    
                if lastfield == 0:
                    if field > 0: 
                        isdelta = True
                        value = Decimal(1.0)
                    else:
                        isdelta = False
                        value = None    
                else: 
                    if field > 0: 
                        d = (field / Decimal(lastfield))-Decimal(1.0)
                        dabs = abs(d)
                        if dabs > self.deltathreshold: 
                            isdelta = True
                            value = d.quantize(Decimal('0.01'))
                        else: 
                            isdelta = False
                            value = None    
                    else: 
                        isdelta = True
                        value = Decimal(-1.0)
                return isdelta, value
            isdeltasource, delta[3] = buildField(source, lastsource)
            isdeltalms, delta[6] = buildField(lms, lastlms)
            if isdeltasource or isdeltalms:                  
                deltas.append(delta)
            
        return deltas
    
    def buildDeltaTextFile(self):
        self.logger.info('building text file of deltas from last run')
        if self.testmode:
            mode = 'test'
        else:
            mode = 'production' 
        with open(self.textfile, 'w') as f:
            f.write("Summary of GMR {}".format(mode)+" run {}".format(self.gmrrun)+"\n")
            f.write("Logs for this run:\n")
            f.write("/n/banquet/dc/mnauto/logs/gmr{}".format(self.gmrrun)+".txt\n")
            f.write("/n/banquet/dc/mnauto/logs/gmrdetail{}".format(self.gmrrun)+".txt\n")
            f.write("Databases:\n")
            dbrun = self.gmrrun.translate(None, '.')
            f.write("icsi_gmr_{}".format(dbrun)+"\n")
            f.write("metanetlm_{}".format(dbrun)+"\n")
            f.write("XCA reports: /xa/metanet/gmr{}".format(self.gmrrun)+"/import/icsi_xca_*.xlsx\n")
            f.write("LM report: /xa/metanet/gmr{}".format(self.gmrrun)+"/import/casestudydata_{}".format(dbrun)+".xlsx\n")
            f.write("GMR Database dump: /u/metanet/repository/gmrdumps/icsi_gmr_v*_{}".format(dbrun)+".sql.gz\n\n")
            f.write("Differences (only) reported from the previous run {}".format(self.lastrun)+
                    " at a ratio threshold of plus or minus {}".format(self.deltathreshold)+"\n")
            for lang in self.langsall: 
                f.write("______________\n")
                f.write(lang+" Target Concept\t#Sources\t#Previous\tDelta sources\t#LMs\t#Previous\tDelta LMs\n")
                deltas = self.buildDeltas(lang)
                if len(deltas) == 0:
                    f.write("\nNo differences found for {}".format(lang)+"\n\n")
                else:     
                    for delta in deltas:
                        space = ""
                        if len(delta[0]) < 8:
                            space = "\t"
                        f.write(delta[0]+space+"\t\t"+str(delta[1])+"\t\t"+str(delta[2])+"\t\t"+str(delta[3])+"\t\t"+str(delta[4])+"\t\t"+str(delta[5])+"\t\t"+str(delta[6])+"\n")
                    f.write("\n")    
         
    def generateReports(self): 
        self.logger.info('generating reports') 
        self.buildDeltaTextFile()
#         TODO:  write spreadsheet?
 
 
        
        
def main():
    """ Command for generating the XCA reports.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate cumulative statistics file, and text and spreadsheet reports (Excel xlsx)")
    parser.add_argument('outputfilebase',help='Output filename base (p, txt, and xlsx extensions will be added)')
    parser.add_argument('--cumulative-stats',dest='runningstats',
                        default='/n/banquet/dc/mnauto/reports/gmr_cumulative_statistics.p',
                        help='File of cumulative statistics')
    parser.add_argument('--gdb-user',dest='gdbuser',default='gmruser',
                        help='GMR database username')
    parser.add_argument('-p','--gdb-pw',dest='gdbpw',default=None,required=True,
                        help='GMR database password')
    parser.add_argument('--run',dest='gmrrun',help='gmr run identifier:  yyyy.mm.dd or, if test: yyyy.mm.ddTn',
                        default=None,required=True)
    parser.add_argument('--gdb-name',dest='gdbname',default='icsi_'+time.strftime("%Y%m%d"),
                        help='GMR database name')
    parser.add_argument('--test',dest='testmode',action='store_true',
                        help="Process a test run; if absent, production assumed")
    parser.add_argument('--initial',dest='initial',action='store_true',
                        help="Initial load")
    parser.add_argument('-v','--verbose',help='Verbose messages',
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
    
    if cmdline.initial: 
        if cmdline.testmode: 
            runs = ['2014.10.18T3', '2014.10.19T5', '2014.10.19T6', '2014.10.25T1', '2014.10.29T1', '2014.10.29T2', '2014.10.29T3', 
                     '2014.11.04T1', '2014.11.10T2']
        else:     
            runs = ['2014.10.19', '2014.10.29', ]
        for run in runs:
            dbrun = run.translate(None, '.')
            gdbc = gmrdb.GMRDBCase(socket='/tmp/mysql.sock',
                                     user=cmdline.gdbuser,
                                     passwd=cmdline.gdbpw,
                                     dbname='icsi_gmr_'+dbrun)
            gdbg = gmrdb.GMRDBGeneral(socket='/tmp/mysql.sock',
                                     user=cmdline.gdbuser,
                                     passwd=cmdline.gdbpw,
                                     dbname='icsi_gmr_'+dbrun)
            stats = Statistics(cmdline.testmode, run, cmdline.outputfilebase+run, cmdline.runningstats, gdbg, gdbc)    
            stats.loadCumulativeStatistics() 
            stats.addRun()
            stats.buildConceptCounts() 
            stats.updateCumulativeStats() 
            stats.generateReports()
            
    else: 
        gdbc = gmrdb.GMRDBCase(socket='/tmp/mysql.sock',
                                 user=cmdline.gdbuser,
                                 passwd=cmdline.gdbpw,
                                 dbname=cmdline.gdbname)
        gdbg = gmrdb.GMRDBGeneral(socket='/tmp/mysql.sock',
                                 user=cmdline.gdbuser,
                                 passwd=cmdline.gdbpw,
                                 dbname=cmdline.gdbname)
        stats = Statistics(cmdline.testmode, cmdline.gmrrun, cmdline.outputfilebase, cmdline.runningstats, gdbg, gdbc)    
    
    
        stats.loadCumulativeStatistics() 
        stats.addRun()
        stats.buildConceptCounts() 
        stats.updateCumulativeStats() 
        stats.generateReports()
    
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    
