#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
.. module:: coresupport
    :platform: Unix
    :synopsis: Update GMR database to populate the cm2lm_core_case/general tables with core lexical support

Updates the GMR database to populate the cm2lm_core_case/general tables with core lexical support

.. moduleauthor:: Steve Doubleday <stevedoubleday@gmail.com>

"""
import sys, re, logging, argparse, setproctitle, time
import gmrdb

ROWLIMIT=12

class CoreSupport:
    """ Class for populating the cm2lm_core_case/general tables with core lexical support.
    """
    def __init__(self, gdb, casemode=False, rowlimit=ROWLIMIT):
        self.logger = logging.getLogger(__name__)
        self.casemode = casemode
        self.gdb = gdb
        self.rowlimit = rowlimit
        self.totalrows = 0
        #print(dir(gdb))
    
    def populateCoreTable(self):
        if self.casemode: 
            self.logger.info('populating cm2lm_core_case with at most %d entries per cm', self.rowlimit)
        else:     
            self.logger.info('populating cm2lm_core_general with at most %d entries per cm', self.rowlimit)
#         self.logger.info('generating CM Source/LM Counts (Ranked) for %s',prot)
        for cmdata in self.gdb.getCMidLangSourceTarget():
            self.logger.info('cm: %d lang: %s, source: %s, target: %s', cmdata.id, cmdata.language, cmdata.source, cmdata.target)
            scores = []
            for cmprop in self.gdb.getCMFromSourceTargetLang(cmdata.language, cmdata.source, cmdata.target ):
                schema = cmprop.value
                mappingscore = cmprop.nvalue 
                self.logger.info('cm: %d schema: %s, mapping score: %f', cmprop.cm.id, schema, mappingscore)
                for lmprop in self.gdb.getScoreFromCmLangProperty(cmprop.cm.id, cmdata.language, schema):
                    lm = lmprop.minId
                    sourcelemma = lmprop.lm_source_lemma 
                    metaphoricityscore = lmprop.nvalue
                    rankingscore = mappingscore * metaphoricityscore  
                    self.logger.info('lm: %d, lemma: %s, metaphoricity score: %f, ranking score: %f', lm, sourcelemma, metaphoricityscore, rankingscore)
                    tup = (rankingscore, cmprop.cm.id, lm, sourcelemma)  
                    scores.append(tup)
            self.updateTableWithTopScores(scores)
        self.logger.info('Complete.  Rows written: %d', self.totalrows)
        

    def updateTableWithTopScores(self, scoretuples):
        scoretuples.sort(key=lambda row: row[0],reverse=False)
        nodups = {}
        for tup in scoretuples: 
            lm = tup[2]
            nodups[lm] = tup
        noduplist = nodups.values()
        noduplist.sort(key=lambda row: row[0],reverse=True)
        topscores = noduplist[:self.rowlimit]
        for tup in topscores:
            if self.casemode:  
                core = self.gdb.insert_cm2lm_core_case(tup[1], tup[2], tup[0])
            else:     
                core = self.gdb.insert_cm2lm_core_general(tup[1], tup[2], tup[0])
            self.logger.info('added score id %d to db: cm: %d, lm: %d, lemma: %s, ranking score: %f', core.id, tup[1], tup[2], tup[3], tup[0])
            self.totalrows = self.totalrows + 1 

        
def main():
    """ Command for populating the core support tables.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Update GMR with core lexical support: cm2lm_core_gase/general tables")
    parser.add_argument('--gdb-user',dest='gdbuser',default='gmruser',
                        help='GMR database username')
    parser.add_argument('-p','--gdb-pw',dest='gdbpw',default=None,required=True,
                        help='GMR database password')
    parser.add_argument('--gdb-name',dest='gdbname',default='icsi_'+time.strftime("%Y%m%d"),
                        help='GMR database name')
    parser.add_argument("--row-limit",dest="rowlimit",
                        type=int, default=ROWLIMIT,
                        help="Max number of rows to save in support of a single CM")
    parser.add_argument('--case-mode',dest='casemode',action='store_true',
                        help="Run in case study mode")
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
    
    coresupport = CoreSupport(gdb, cmdline.casemode, cmdline.rowlimit)
    coresupport.populateCoreTable()
    
    return 0    

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    
