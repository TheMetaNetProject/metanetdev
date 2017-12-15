#!/usr/bin/env python
# encoding: utf-8
"""
.. module:: programsources
   :platform: Unix
   :synopsis: Utility for reading and searching IARPA source dimensions document

Tool for reading data out of an excel file that IARPA
intends to send us periodically, out of which we must get
the concepts and dimensions to map our LMs to.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
import sys, os, codecs
from openpyxl.reader.excel import load_workbook
import cPickle as pickle
import logging, re, argparse

reload(sys)
sys.setdefaultencoding('utf-8')

# default file to load up

class ProgramSources:
    """
    Utility class for reading info out of IARPAs sources excel sheet.  Note
    that source dimensions (aka dimensions) are all referred to via
    CONCEPT.Dimension, e.g. ABYSS.Type
    """
    progsourcedir = '/u/metanet/repository/program'
    progsourcefile = 'meta_sources_combined_hmb_latest.xlsx'
    lupsource = None
    psourcelu = None
    
    def __init__(self, progsourcesfile=None, cachedir=None, verbose=False, force=False):
        """
        :param progsourcesfile: excel file with program sources and dimensions
        :type progsourcesfile: str
        :param cachedir: directory to create and read cache files
        :type cachedir: str
        :param verbose: display additional status messages
        :type verbose: bool
        :param force: force cache regeneration
        :type force: bool
        """
        # force is to force generation of cache
        if 'PROGSOURCEPATH' in os.environ:
            self.progsourcedir = os.environ['PROGSOURCEPATH']
        if not cachedir:
            cachedir = self.progsourcedir + '/cache'
        self.cachef = '%s/cache.programsources' % (cachedir)
        self.verbose = verbose
        logger = logging.getLogger("ProgramSources")
        if os.path.exists(self.cachef) and (not force):
            logger.info("Loading sources lookups from cache...")
            self.loadcache()
            return

        # Otherwise, load and generate lookups
        logger.info("Generating sources lookups...")
        if not progsourcesfile:
            progsourcesfile = '%s/%s' % (self.progsourcedir,self.progsourcefile)
        plist = self.getprogramsources(progsourcesfile)
        self.lupsource = {'en':{},
                          'es':{},
                          'ru':{},
                          'fa':{}}
        self.psourcelu = {'en':{},
                          'es':{},
                          'ru':{},
                          'fa':{}}
        for p in plist:
            ssubd = p['scon']+'.'+p['sdim'].replace('\n','')
            for lang in ['en','es','ru','fa']:
                luset = set()
                if p[lang]:
                    wordlist = p[lang].replace(u'?','').strip()
                    if not wordlist:
                        continue
                    wordlist = re.sub(ur'\s*(\(|\[)[a-zA-Z0-9_, ]+(\)|\])\s*','',wordlist,flags=re.U)
                    logger.info("Program source-subd=%s, words=%s"%(ssubd,wordlist))
                    for w in wordlist.split(','):
                        lu = w.strip().replace('\n','')
                        luset.add(lu)
                        if lu not in self.lupsource[lang]:
                            self.lupsource[lang][lu] = set()
                        self.lupsource[lang][lu].add(ssubd)
                        # HACK:
                        # if the lu is multiple words, add the first separately too
                        # e.g. slide into will add 'slide' as well as 'slide into'
                        if ' ' in lu:
                            lu1 = lu.split(' ')[0]
                            luset.add(lu1)
                            if lu1 not in self.lupsource[lang]:
                                self.lupsource[lang][lu1] = set()
                            self.lupsource[lang][lu1].add(ssubd)
                if ssubd not in self.psourcelu[lang]:
                    self.psourcelu[lang][ssubd] = set()
                self.psourcelu[lang][ssubd].update(luset)
        logger.info("Caching source lookups...")
        if not os.path.exists(cachedir):
            os.mkdir(cachedir)
        self.cacheme()
    
    def cacheme(self):
        f = open(self.cachef,'wb')
        pickle.dump(self.__dict__,f,2)
        f.close()

    def loadcache(self):
        f = open(self.cachef,'rb')
        tmp_dict = pickle.load(f)
        f.close()
        self.__dict__.update(tmp_dict)
  
    def getprogramsources(self,progsourcesfile):
        """
        Returns the contents of IARPA's standard metaphor project source and
        source subdimensions as a list of dictionaries, with the following
        keys::
        
            scon: PROG SOURCE (ABYSS)
            sdim: PROD SOURCE DIMENSION (Type)
            en: ENGLISH (Lex Items)
            es: SPANISH
            ru: RUSSIAN
            fa: PERSIAN
        
        Note that except for Lex Items, spaces are turned into _'s to match
        the version in the GMR tables.
        """
        if self.verbose:
            print "Reading in program sources",progsourcesfile
        wb = load_workbook(progsourcesfile)
        psources = []
        ws = wb.get_sheet_by_name("concepts")
        for row in ws.rows[1:]:
            (scon,sdim,owner,en,enschema,es,esschema,ru,ruschema,fa,faschema) = (cell.value for cell in row[0:11])
            if not scon:
                continue
            if not sdim:
                sdim = "Null"
            psource = {'scon':scon.strip().replace(' ','_').replace('-','_'),
                       'sdim':sdim.strip().replace(' ','_').replace('-','_').replace('/','_'),
                       'en':en,'es':es,'ru':ru,'fa':fa}
            psources.append(psource)
        return psources
    
    def getSSubd(self, lu, lang):
        """
        Given an LU and a lang, return all the source subdimensions that list
        that LU as being in its semantic cluster
        """
        if lu in self.lupsource[lang]:
            return self.lupsource[lang][lu]
        else:
            return set()
        
    def getLUs(self,ssubd, lang):
        """
        Given a source subdimension and a lang, return a list of the LUs in its
        semantic cluster
        """
        if ssubd in self.psourcelu[lang]:
            return self.psourcelu[lang][ssubd]
        else:
            return set()
        
    def getBestSSubd(self,sslus, lang):
        """
        Given a list of LUs and a lang, return a ranked list of subdimensions.
        List items are tuples consisting of the subdimension and a score.
        """
        possible_subds = set()
        for slu in sslus:
            subds = self.getSSubd(slu, lang)
            possible_subds.update(subds)
        if not possible_subds:
            return None
        subdlist = []
        for subd in possible_subds:
            subdlus = self.getLUs(subd,lang)
            # number of intersecting words / sum of all words
            sum = len(sslus.union(subdlus))
            subdlist.append((subd, len(sslus.intersection(subdlus)) / float(sum)))        
        subdlist.sort(key=lambda tup: tup[1], reverse=True)
        return subdlist
    
    def getAllSSubd(self):
        slist = []
        for lang in ['en','es','ru','fa']:
            slist.extend(self.psourcelu[lang].keys())
        return sorted(slist)
                
    
def main():
    """ Code for generating the cache independently. """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate Cache files for Program Sources utility",
        epilog="Note: Any existing cache will be overwritten.")
    parser.add_argument("-i", "--inputprogsourcefile",
                        default=None,
                        help="Program sources file to use, instead of default")
    parser.add_argument("-c", "--cachedir",
                        default=None,
                        help="Directory to generate cache files (instead of default)")
    cmdline = parser.parse_args()    
    progs = ProgramSources(cmdline.inputprogsourcefile, cmdline.cachedir, verbose=True, force=True)
    
if __name__ == '__main__':
    status = main()
    sys.exit(status)
