#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: fnxml
   :platform: Unix
   :synopsis: Library for querying FrameNet (via XML).  Limited to Frames and LUs.

Library for querying FrameNet (via XML).  Limited to Frames and LUs.  Data is loaded
from the FN website (https://framenet2.icsi.berkeley.edu/fnReports/data/luIndex.xml)
and cached.

Lookups generated include frame name -> lu names, lu names/lpos -> frame names
and then frame name -> relation -> frame name

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>
"""
import xml.etree.ElementTree as ET
import re, codecs, sys, os
import cPickle as pickle
import urllib2, logging, argparse, time, pprint

class FrameNet:
    """ Class for reading FrameNet XML from the FrameNet website and generating
    cache dictionaries for looking up frames and LUs.
    
    """
    FN_BASE = 'https://framenet2.icsi.berkeley.edu/fnReports/data'
    FN_INDEX_URL = FN_BASE + '/luIndex.xml'
    FNREL_URL = FN_BASE + '/frRelation.xml'
    
    def __init__(self, cachedir='.', force=False):
        """
        :param cachedir: directory to read and write cache files to
        :type cachedir: str
        :param force: flag to force regeneration of cache
        :type force: bool
        
        """
        self.logger = logging.getLogger(__name__)
        self.cachedir = cachedir
        self.cachef = '%s/cache.fndata' % (self.cachedir)
        self.framelu = None
        self.lposframe = None
        self.framelpos = None
        self.fRels = None
        self.feRels = None
        if os.path.exists(self.cachef) and (not force):
            self.loadcache()
            return
        self.parseLUXML()
        self.parseRelsXML()
        if not os.path.exists(self.cachedir):
            os.mkdir(self.cachedir)
        self.cacheme()
    
    def cacheme(self):
        """ Caches the class data to disk
        """
        f = open(self.cachef,'wb')
        pickle.dump((self.framelu,
                     self.framelpos,
                     self.lposframe,
                     self.fRels,
                     self.feRels),f,2)
        f.close()

    def loadcache(self):
        """ Retrieves the class data from disk
        """
        f = open(self.cachef,'rb')
        (self.framelu,
         self.framelpos,
         self.lposframe,
         self.fRels,
         self.feRels) = pickle.load(f)
        f.close()
        
    def parseLUXML(self,xmlfile=None):
        """ Parse FrameNet LU XML files, retrieving them from the FrameNet
        website, and populate internal tables with Frame/LU lookup information.
        :param xmlfile: if given, will parse only that xml file
        :type xmlfile: str
        """
        tree = None
        self.framelu = {}
        self.lposframe = {}
        self.framelpos = {}
        namespaces = {'fn':'http://framenet.icsi.berkeley.edu'}
        POSre = re.compile(r'\.([A-Za-z]|adj|adv|aa)$')
        if xmlfile:
            self.logger.info('Parsing LU XML file %s',xmlfile)
            tree = ET.parse(xmlfile)
        else:
            self.logger.info('Parsing LU XML file %s',self.FN_INDEX_URL)
            tree = ET.parse(urllib2.urlopen(self.FN_INDEX_URL))
        for lu in tree.getiterator('{http://framenet.icsi.berkeley.edu}lu'):
            fname = lu.get('frameName')
            if fname not in self.framelu:
                self.framelu[fname] = set()
            if fname not in self.framelpos:
                self.framelpos[fname] = set()
            lempos = lu.get('name')
            lemma = POSre.sub('',lempos)
            # include both lempos and lemma
            self.framelu[fname].add(lempos)
            self.framelu[fname].add(lemma)
            if lempos not in self.lposframe:
                self.lposframe[lempos] = set()
            self.lposframe[lempos].add(fname)
            if fname not in self.framelpos:
                self.framelpos[fname] = set()
            self.framelpos[fname].add(lempos)
        self.logger.info("Loaded %d frames",len(self.framelu))
    
    def parseRelsXML(self,xmlfile=None):
        """ Parses FrameNet relations XML file, from the website if the path is
        not passed in.
        :param xmlfile: relations xml file (if not using the website)
        :type xmlfile: str
        """
        tree = None
        self.fRels = {}
        self.feRels = {}
        namespaces = {'fn':'http://framenet.icsi.berkeley.edu'}
        POSre = re.compile(r'\.([A-Za-z]|adj|adv|aa)$')
        if xmlfile:
            self.logger.info('Parsing frameRelations XML file %s',xmlfile)
            tree = ET.parse(xmlfile)
        else:
            self.logger.info('Parsing frameRelations XML file %s',self.FNREL_URL)
            tree = ET.parse(urllib2.urlopen(self.FNREL_URL))
        
        for rtype in tree.getiterator('{http://framenet.icsi.berkeley.edu}frameRelationType'):
            rName = rtype.get('name')
            subName = rtype.get('subFrameName')
            supName = rtype.get('superFrameName')
            subRel = rName + '.' + subName
            supRel = rName + '.' + supName
            for fRel in rtype.iter('{http://framenet.icsi.berkeley.edu}frameRelation'):
                subFrame = fRel.get('subFrameName')
                supFrame = fRel.get('superFrameName')
                # record subFrame relation
                if subFrame not in self.fRels:
                    self.fRels[subFrame] = {}
                if subRel not in self.fRels[subFrame]:
                    self.fRels[subFrame][subRel] = []
                self.fRels[subFrame][subRel].append(supFrame)
                # record superFrame relations
                if supFrame not in self.fRels:
                    self.fRels[supFrame] = {}
                if supRel not in self.fRels[supFrame]:
                    self.fRels[supFrame][supRel] = []
                self.fRels[supFrame][supRel].append(subFrame)
                
                for feRel in fRel.iter('{http://framenet.icsi.berkeley.edu}FERelation'):
                    subFE = subFrame + '.' + feRel.get('subFEName')
                    supFE = supFrame + '.' + feRel.get('superFEName')
                    # record subFE relation
                    if subFE not in self.feRels:
                        self.feRels[subFE] = {}
                    if subRel not in self.feRels[subFE]:
                        self.feRels[subFE][subRel] = []
                    self.feRels[subFE][subRel].append(supFE)
                    # record superFE relations
                    if supFE not in self.feRels:
                        self.feRels[supFE] = {}
                    if supRel not in self.feRels[supFE]:
                        self.feRels[supFE][supRel] = []
                    self.feRels[supFE][supRel].append(subFE)
        self.logger.info('Relations loaded for %d frames and %d FEs',len(self.fRels),len(self.feRels))
        
    def getLUs(self,fname):
        """ Given a frame name, return its LUs as a set of lemmas and lpos
        :param fname: frame name
        :type fname: str
        :returns: set of LU lemmas and lpos (not qualified with frame name)
        
        """
        try:
            return self.framelu[fname]
        except:
            return set()
    
    def getRelatedFrames(self, subjFrame, relation):
        """
        Given a subject frame and a relation, retrieve the object frame.
        I.e. subjFrame is relation of objFrame. Returns a list of objFrames
        :param subjFrame: the frame that the relation is predicated on
        :type subFrame: str
        :param relation: the name of the relation
        :type relation: str
        :returns: a list of frames related to the subjFrame by the relation
        """
        try:
            return self.fRels[subjFrame][relation]
        except:
            if subjFrame not in self.fRels:
                self.logger.debug('%s has no relations',subjFrame)
            elif relation not in self.fRels[subjFrame]:
                self.logger.debug('Frame %s is not %s of any frame',subjFrame,relation)
            return []
    
    def getFramesFromLPOS(self, lpos):
        """ Given a lempos string, return the set of frames it appears in.
        :param lpos: lempos (e.g. run.v)
        :type lpos: str
        :returns: set of frame names
        
        """
        try:
            return self.lposframe[lpos]
        except:
            return set()

    def getLUsFromFrame(self,fname):
        """ Given a frame name, return its LUs as a set of lpos
        :param fname: frame name
        :type fname: str
        :returns: set of LU lpos (not qualified with frame name)
        
        """
        try:
            return self.framelpos[fname]
        except:
            return set()

    def getFrameRelations(self, frame):
        """ Given a frame, returns all relations that are predicated on that frame.
        :param frame: frame name
        :type frame: str
        :returns: list of relations
        """
        if frame in self.fRels:
            return self.fRels[frame].keys()
        return []

def main():
    """ Used for testing and/or manual cache regeneration
    """
    datestring = time.strftime("%Y%m%d")
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="FN data lookup")
    parser.add_argument('--lpos', help="Lookup this lpos")
    parser.add_argument('--frame', help="List LUs and related frames of this frame")
    parser.add_argument('-f','--force',action='store_true',
                        help='Force rebuilding of lookups')
    parser.add_argument('-v','--verbose',action='store_true',
                        help='Display more status messages')
    parser.add_argument('-c','--cachedir',help='Directory to generate and load cache from',
                        default='.')
    cmdline = parser.parse_args()
        
    # this routine has to write its own files
    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if cmdline.verbose:
        deflevel = logging.DEBUG
    else:
        deflevel = logging.INFO
    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)
    fn = FrameNet(cachedir=cmdline.cachedir, force=cmdline.force)
    if cmdline.lpos:
        frames = fn.getFramesFromLPOS(cmdline.lpos)
        print "frames:", pprint.pformat(frames)
    if cmdline.frame:
        lus = fn.getLUs(cmdline.frame)
        print "LUs:", pprint.pformat(lus)
        for rel in fn.getFrameRelations(cmdline.frame):
            rframes = fn.getRelatedFrames(cmdline.frame, rel)
            print '  ', cmdline.frame, 'is %s of' % (rel), pprint.pformat(rframes)

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    