#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
.. module:: gmrupdate
    :platform: Unix
    :synopsis: Module for updating the GMR database from the MetaNet LM database.

Module for updating the GMR database from the MetaNet LM database. Includes code for
mapping from expressions to concepts via the MetaNet conceptual network
(:py:mod:`mnrepository.metanetrdf`).

.. moduleauthor:: Jisup <jhong@icsi.berkeley.edu>

"""
import sys, re, logging, pprint, argparse, setproctitle
from collections import Counter
from cnmapping import ConceptualNetworkMapper
import gmrdb, metanetdb
from mnpipeline.affectlookup import AffectLookup

class GMR_Updater:
    """ Used to convert MetaNet internal LM database to the GMR.  Includes
    methods for mapping from expressions to schemas to concepts.
    """
    def __init__(self,lang, cachedir=None, useSE=None, forceSearch=False):
        """
        :param lang: language
        :type lang: str
        :param cachedir: location of cache for creation and use
        :type cachedir: str
        :param useSE: domain name or IP of Sparql Endpoint
        :type useSE: str
        :param forceSearch: flag to force mapping computation (even if already in the LM db)
        :type forceSearch: bool
        """
        self.logger = logging.getLogger(__name__)
        self.cnmapper = ConceptualNetworkMapper(lang,cachedir,useSE)
        self.lang = lang
        self.afflookup = AffectLookup(lang)
        self.POSre = re.compile(ur'\.([A-Za-z]|adj|adv|aa)$',flags=re.U)
        self.forceSearch = forceSearch

    def getTargetConcept(self,lm):
        """ Given an LM database item, returns the target concept, and 
        saves the schemas and concept in the LM row """
        tschemas, tconcept = self.cnmapper.getTargetSchemasAndConceptFromLemma(lm.targetlemma)
        # save schemas to LM database
        tsNameList = []
        for tschema in tschemas:
            tsName = self.cnmapper.mr.getNameString(tschema)
            tsNameList.append(tsName)
        if tsNameList:
            lm.targetschema = u','.join(tsNameList)
            lm.save()     
        # save concept to LM database
        if tconcept:
            lm.targetconcept = tconcept
            lm.save()
        return tconcept
    
    def getSourceDimension(self,lm):
        """
        Given an LM db row, returns source dimension in the form CONCEPT.Dimension,
        e.g. DISEASE.Type.  Saves schemas and the dimension to DB.
        """
        sschemas, sconcepts = self.cnmapper.getSourceSchemasAndDimensionFromLemma(lm.sourcelemma)
        # save the schemas to the MetaNetDB
        ssNameList = []
        for sschema in sschemas:
            ssName = self.cnmapper.mr.getNameString(sschema)
            ssNameList.append(ssName)
        if ssNameList:
            lm.sourceschema = u','.join(ssNameList)
        # save concept to LM database
        if sconcepts:
            lm.sourceconcept = u','.join(sconcepts)
            lm.save()
        return sconcepts
    
    def getDocType(self, corpus, uri, dtype):
        """ Given corpus name, provenance uri, and document type.  Return
        document type categories as specified by IARPA.
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
    
    def dropPOS(self,lempos):
        """ Drop the pos part of a lempos.
        """
        return self.POSre.sub('',lempos)
    
    def process_lms(self, lmdb, gdb, skipna=True):
        """ Process LMs in the MetaNet LM database and insert LMs into the GMR.
        :param lmdb: MetaNet LM database object
        :type lmdb: :mod:metanetdb.MetaNetLMDB
        :param gdb: GMR database object
        :type gdb: :mod:gmrdb.GMRDB
        """
        cm_list = []
        for lm in lmdb.getLMs(self.lang):
            #self.logger.info("Processing LM (%s,%s)" % (lm.sourcelemma, lm.targetlemma))
            if self.forceSearch:
                self.logger.info("Forced search on LM (%s,%s)",lm.sourcelemma, lm.targetlemma)
                tconceptstr = self.getTargetConcept(lm)
                sconceptlist = self.getSourceDimension(lm) # note: this returns CONCEPT.Dimension
            else:
                tconceptstr = lm.targetconcept
                sconceptlist = lm.sourcedimension.split(',')
            if (not tconceptstr) or (not sconceptlist):
                self.logger.info(u'Skipping LM (%s,%s) because tcon=%s scon=%s',
                                 lm.targetlemma,lm.sourcelemma,tconceptstr,u','.join(sconceptlist))
                continue
            self.logger.info(u'LM (%s,%s) has concepts (%s,%s)',
                             lm.targetlemma,lm.sourcelemma,tconceptstr,u','.join(sconceptstr))
            # option to skip NULL.ALL LMs
            if not sconceptlist:
                continue
            tconcept = gdb.getTargetConcept(self.lang,tconceptstr)
            sconcepts = gdb.getSourceConcepts(self.lang,sconceptlist) # eg DISEASE
            for lmi in lmdb.getLMInstances(lm):
                sent = lmi.sentence
                doc = sent.document
                dtype = self.getDocType(doc.corpus,doc.uri,doc.type)
                lm_target = self.dropPOS(lm.targetlemma)
                lm_source = self.dropPOS(lm.sourcelemma)
                # insert/update GMR lm
                g_lm_sent = gdb.update_lm_sent(self.lang, sent.text, sent.ext, dtype)
                gdb.update_lm(self.lang, lmi.id, lm_target, lm_source, 
                              tconcept, g_lm_sent)
                cmkey = (tconcept.id,sconcept.id)
                cm_list.append(cmkey)
        # insert CMs into database, only if there are at least 10 LMs motivating CM        
        cm_counter = Counter(cm_list)
        for cmkey,freq in cm_counter.most_common():
            if freq >= 10:
                (tconceptid,sconceptid) = cmkey
                gdb.insert_cm(self.lang, tconceptid, sconceptid)
                self.logger.info("Adding CM %s because it has %d LM mappings.",cmkey,freq)
            else:
                self.logger.info("Not adding CM %s because it has %d LM mappings.",cmkey,freq)

def main():
    """ Command for running the GMR generation from the MetaNet LM database.
    Requires passing in database authentication information at runtime.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Update the GMR from the MetaNet LM database")
    parser.add_argument('-l','--lang',dest='lang',required=True,
                        help="update GMR for this language.")
    parser.add_argument('--disable-skip-null-all',dest='skipnulls',action='store_false',
                        help='Do not skip LMs whose source gets mapped to NULL.ALL')
    parser.add_argument('-f','--force',action='store_true',
                        help='Force search for target and source concepts.')
    parser.add_argument('--use-se',dest="useSE",default=None,
                        help='SPARQL endpoint for conceptual graph searches')
    parser.add_argument('--gdb-user',dest='gdbuser',default='gmruser',
                        help='GMR database username')
    parser.add_argument('--gdb-pw',dest='gdbpw',default=None,required=True,
                        help='GMR database password')
    parser.add_argument('--gdb-name',dest='gdbname',default='icsi_gmr_21',
                        help='GMR database name')
    parser.add_argument('--mdb-user',dest='mdbuser',default='mdbuser',
                        help='MetaNet LM database username')
    parser.add_argument('--mdb-pw',dest='mdbpw',default=None,required=True,
                        help='MetaNet LM database password')
    parser.add_argument('--mdb-name',dest='mdbname',
                        help='Metanet LM database name. Default: lang + mnlm')
    cmdline = parser.parse_args()
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(--mdb-pw|--gdb-pw)(=|\s+)(\S+)',ur'\1\2XXXX')
    setproctitle.setproctitle(pstr)
    
    logfname = 'updategmr_%s.log' % (cmdline.lang)
    
    logging.basicConfig(filename=logfname,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    gmrupdater = GMR_Updater(cmdline.lang,useSE=cmdline.useSE,
                             forceSearch=cmdline.force)
    if cmdline.mdbname:
        mdbname = cmdline.mdbname
    else:
        mdbname = cmdline.lang + 'mnlm'
    lmdb = metanetdb.MetaNetLMDB(socket='/tmp/mysql.sock',
                                 user=cmdline.mdbuser,
                                 passwd=cmdline.mdbpw,
                                 dbname=mdbname)
    
    gdb = gmrdb.GMRDB(socket='/tmp/mysql.sock',
                      user=cmdline.gdbuser,
                      passwd=cmdline.gdbpw,
                      dbname=cmdline.gdbname)
    gmrupdater.process_lms(lmdb, gdb, cmdline.skipnulls)
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    
