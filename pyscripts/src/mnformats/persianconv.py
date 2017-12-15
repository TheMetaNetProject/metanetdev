"""
MetaNet Interchange JSON format utility methods

jhong@icsi.berkeley.edu
May 1, 2013
"""

import ujson
import simplejson
import json
import gzip, collections
import os
import math
import sys
import csv
import re
import nltk.tokenize
import codecs
import urllib2
import jsonschema
from xml import sax
from mnwiki import MediaWikiParser
import xml.etree.ElementTree as elementTree
from collections import OrderedDict
from nltk.tokenize import sent_tokenize
from mnformats import mnjson

MAXSENTSPERFILE = 5000

class HamshahriXMLHandler(sax.ContentHandler):
    
    def __init__(self,infname,outdir,zip=False):
        self.jdata = mnjson.getJSONRoot(lang='fa',docs=[],sents=[])
        self.whitespacere = re.compile(ur'\s+',flags=re.U)
        self.content = None
        self.sentidx = -1
        if zip:
            self.ext = 'json.gz'
        else:
            self.ext = 'json'
        self.infbase = os.path.basename(infname).split('.')[0]
        self.outdir = outdir
        self.chunkno = 0
        
    def initDoc(self):
        self.content = None
        self.hidecontent = None
        self.title = None
        self.docid = None
        self.doctype = 'news'
        self.sentno = 0
    
    def startElement(self, name, attrs):
        try:
            if name==u'DOC':
                self.initDoc()
            elif name==u'DOCID':
                self.content = []
            elif name==u'CAT':
                if attrs.getValue('xml:lang')=='en':
                    self.content = []
            elif name==u'TITLE':
                self.content = []
            elif name==u'IMAGE':
                if self.content:
                    self.hidecontent = self.content
                    self.content = None
        except:
            print >> sys.stderr, "Error:", self.docid, name
            for attr in attrs.keys():
                print >> sys.stderr, "  ", attr, "=", attrs.getValue(attr)            
            raise
        
    def endElement(self, name):
        global MAXSENTSPERFILE
        if name==u'IMAGE':
            if self.hidecontent:
                self.content = self.hidecontent
                self.hidecontent = None
        elif name==u'DOCID':
            self.docid = u''.join(self.content).strip()
        elif name==u'TITLE':
            self.title = u''.join(self.content).strip()
        elif name==u'CAT':
            if self.content:
                self.doctype = u'news '+ u''.join(self.content).strip()
        elif name==u'TEXT':
            if self.content:
                contentstring = self.whitespacere.sub(u' ',
                                                      u''.join(self.content).strip())
                sents = sent_tokenize(contentstring)
                for sent in sents:
                    senttext = sent.strip()
                    if not senttext:
                        continue
                    self.sentno += 1
                    self.sentidx += 1
                    sentelem = mnjson.getJSONSentence(u'%s:%s'%(self.docid,self.sentno),
                                                      self.sentidx,
                                                      senttext)
                    self.jdata[u'sentences'].append(sentelem)
                self.content = None
        elif name=='DOC':
            # end of document, create the doc json structure
            self.jdata[u'documents'].append(mnjson.getJSONDocumentHeader(self.docid,
                                            u'Hamshahri',
                                            self.title,
                                            self.docid,
                                            self.doctype,
                                            self.sentno))
            if self.sentidx >= MAXSENTSPERFILE:
                self.chunkno += 1
                self.writefile()
    
    def writefile(self):
        '''
        Write out json file: this is to keep the file sizes manageable
        '''
        if self.chunkno:
            outfname = '%s/%s_%03d.%s' % (self.outdir,self.infbase,self.chunkno,self.ext)
        else:
            outfname = '%s/%s.%s' % (self.outdir,self.infbase,self.ext)
        mnjson.writefile(outfname,self.jdata)
        self.jdata = mnjson.getJSONRoot(lang='fa',docs=[],sents=[])
        self.sentidx = -1
        self.content = None
        
    def characters(self, content):
        if self.content is not None:
            self.content.append(content)
            
    def hasUnwrittenData(self):
        if self.sentidx >= 0:
            return True
        return False
        
def convert_hamshahri_to_json(infname,outdir,zip):
    """
    Hamshahri XML to JSON
    """
    inputhandler = HamshahriXMLHandler(infname,outdir,zip)
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    try:
        parser.parse(infname)
        if inputhandler.hasUnwrittenData():
            # increment chunkno if we've written out a chunk
            if inputhandler.chunkno:
                inputhandler.chunkno += 1
            inputhandler.writefile()
    except sax.SAXException, message:
        print >> sys.stderr, "Error parsing %s: %s" % (infname,message)
        
