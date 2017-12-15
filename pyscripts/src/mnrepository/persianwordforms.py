#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: persianwordforms
    :platform: Unix
    :synopsis: library for looking up persion wordforms to retrieve the root form or vice-versa

.. moduleauthor:: Jisup <jhong@icsi.berkeley.edu>
"""
import sys, os, logging, pprint, codecs, argparse
import cPickle as pickle

DEFAULTPWFDIR='/u/metanet/extraction/persian'
DEFAULTPWFFNAME='PerVerbNounInflects.txt'
class PersianWordForms:
    """ Creates lookup tables, which are pickled for performance, from
    text format list of inflected forms.
    """
    def __init__(self, pwfdir=DEFAULTPWFDIR,pwfile=DEFAULTPWFFNAME,
                 cachedir=None, force=False):
        self.logger = logging.getLogger(__name__)
        self.root2wforms = {}
        self.wform2root = {}
        self.all2all = {}
        if not cachedir:
            cachedir = pwfdir
        self.cachef = '%s/cache.pwf' % (cachedir)
        pwfpath = u'%s/%s' % (pwfdir, pwfile)
        infmodtime = os.path.getmtime(pwfpath)
        if (os.path.exists(self.cachef) and (not force) and 
                (os.path.getmtime(self.cachef) > infmodtime)):
            self.loadcache()
            return
        with codecs.open(pwfpath,'r', encoding='utf-8') as pwffile:
            lineno = 0
            for line in pwffile:
                lineno += 1
                try:
                    rootf, pos, infl = line.split(u'\t')
                except ValueError:
                    self.logger.error(u'Error: invalid format at line %d: %s',lineno,line)
                    continue
                #self.logger.info(u'rootf=%s pos=%s infls=%s',rootf,pos,infl)
                iforms = []
                for wf in infl.split(u','):
                    wf = wf.strip()
                    if wf:
                        iforms.append(wf)
                #self.logger.info(u'%d inflected forms of %s',len(iforms),rootf)
                #self.logger.info(u'iforms=%s',iforms)
                self.root2wforms[rootf] = set(iforms)
                #self.logger.info(u'iforms=%s',iforms)
                iforms.append(rootf)
                allset = set(iforms)
                self.all2all[rootf] = allset
                for inflform in iforms:
                    self.wform2root[inflform] = rootf
                    self.all2all[inflform] = allset
        if not os.path.exists(cachedir):
            os.mkdir(cachedir)
        self.cacheme()
        
    def cacheme(self):
        f = open(self.cachef,'wb')
        pickle.dump((self.root2wforms,
                     self.wform2root,
                     self.all2all),f,2)
        f.close()

    def loadcache(self):
        f = open(self.cachef,'rb')
        (self.root2wforms,
         self.wform2root,
         self.all2all) = pickle.load(f)
        f.close()                
    
    def getRoot(self, wform):
        return self.wform2root.get(wform)
    
    def getWordForms(self, rootf):
        if rootf in self.root2wforms:
            return self.root2wforms[rootf]
        else:
            return [] 
    
    def getAllForms(self, aform):
        if aform in self.all2all:
            return self.all2all[aform]
        else:
            return []
        
def main():
    """ Generates the cache """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Persan word form and root lookup",
        epilog="This generates the cache.")
    parser.add_argument("-d","--datadir",help="Directory containin wordforms data",
                        default=DEFAULTPWFDIR)
    parser.add_argument("-w","--wordformsfile",help="File name of word forms file",
                        default=DEFAULTPWFFNAME)
    parser.add_argument("-c","--cachedir",
                        help="Directory to create cache file.")
    parser.add_argument("-r","--root",
                        help="Look up word forms for given root.")
    parser.add_argument("-f","--force",
                        action="store_true",
                        help="Force cache regeneration.")
    parser.add_argument("-a","--all",
                        help="Lookup all word forms from one of them.")
    parser.add_argument("-v","--verbose",action="store_true",
                        help="Verbose messages.")
    cmdline = parser.parse_args()

    msgformat = '%(asctime)-15s - %(message)s'
    dateformat = '%Y-%m-%dT%H:%M:%SZ'
    if cmdline.verbose:
        deflevel = logging.INFO
    else:
        deflevel = logging.WARN
    logging.basicConfig(format=msgformat, datefmt=dateformat, level=deflevel)
    
    pwf = PersianWordForms(pwfdir=cmdline.datadir,pwfile=cmdline.wordformsfile,
                           cachedir=cmdline.cachedir,force=cmdline.force)
    if cmdline.root:
        print pprint.pformat(pwf.getWordForms(cmdline.root))
    if cmdline.all:
        print pprint.pformat(pwf.getAllForms(cmdline.all))

if __name__ == "__main__":
    status = main()
    sys.exit(status)
