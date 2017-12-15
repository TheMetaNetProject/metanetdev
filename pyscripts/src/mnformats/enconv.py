#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
English Corpus Conversion Utilities

jhong@icsi.berkeley.edu
Nov 1, 2013
"""
import ujson
import gzip, collections
import os,math,sys,re,codecs
import mnjson
from xml import sax

reload(sys)
sys.setdefaultencoding('utf-8')

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

class BNCXMLHandler(sax.ContentHandler):
    #
    # Event handler for SAX based parsing of Rasp-parsed BNC-XML
    #
    def initDoc(self):
        self.content = None
        self.title = None
        self.docid = None
        self.sentno = None
        self.senttext = None
        self.words = None
        self.word = None
        self.sentlen = 0
        self.dparse = None
        self.sentences = []
        self.document = None
        self.ntoi = None
        self.classCode = None
    
    def startElement(self, name, attrs):
        try:
            if name==u'bncDoc':
                self.initDoc()
            elif name==u'title':
                if self.title is None:
                    self.content = []
            elif name==u'idno':
                if (self.docid is None) and (attrs.getValue(u'type') == u'bnc'):
                    self.content = []
                else:
                    self.content = None
            elif name==u'classCode':
                if self.classCode is None:
                    self.content = []
                else:
                    self.content = None
            elif name==u's':
                self.sentno = attrs.getValue(u'n')
                self.words = []
                self.senttext = []
                self.dparse = []
                self.sentlen = 0
                self.content = None
                self.ntoi = {}
            elif name==u'w':
                if u'n' not in attrs:
                    self.content = None
                    return
                self.content = []
                rpos = None
                if u'rpos' in attrs:
                    rpos = attrs.getValue(u'rpos')
                self.word = {u'idx':None,
                             u'form':None,
                             u'rpos':rpos,
                             u'n':attrs.getValue(u'n'),
                             u'lem':attrs.getValue(u'lem'),
                             u'c5':attrs.getValue(u'c5'),
                             u'pos':attrs.getValue(u'pos'),
                             u'hw':attrs.getValue(u'hw')}
            elif name==u'c':
                self.content = []
                self.word = {u'idx':None,
                             u'form':None,
                             u'rpos':attrs.getValue(u'rpos'),
                             u'n':attrs.getValue(u'n'),
                             u'lem':attrs.getValue(u'lem'),
                             u'c5':attrs.getValue(u'c5'),
                             u'pos':None,
                             u'hw':None}
            elif name==u'gap':
                if u'n' in attrs:
                    self.content = []
                    resp = None
                    reason = None
                    desc = None
                    rpos = None
                    if u'resp' in attrs:
                        resp = attrs.getValue(u'resp')
                    if u'reason' in attrs:
                        reason = attrs.getValue(u'reason')
                    if u'desc' in attrs:
                        desc = attrs.getValue(u'desc')
                    if u'rpos' in attrs:
                        rpos = attrs.getValue(u'rpos')
                    self.word = {u'idx':None,
                                 u'form':None,
                                 u'n':attrs.getValue(u'n'),
                                 u'desc':desc,
                                 u'lem':attrs.getValue(u'lem'),
                                 u'rpos':rpos,
                                 u'resp':resp,
                                 u'reason':reason}
                else:
                    self.content = None
            elif name==u'gr':
                self.content = None
                # subtract 1 from the integers so they refer to array indices
                subtype = None
                head = None
                dep= None
                if u'subtype' in attrs:
                    subtype = attrs.getValue(u'subtype')
                if u'dep' in attrs:
                    dep = attrs.getValue(u'dep')
                if u'head' in attrs:
                    head = attrs.getValue(u'head')
                self.gritem = {u'type':attrs.getValue(u'type'),
                               u'subtype':subtype,
                               u'head':head,
                               u'dep':dep}
                self.dparse.append(self.gritem)
        except:
            print >> sys.stderr, "Error:", self.docid, self.sentno, name
            for attr in attrs.keys():
                print >> sys.stderr, "  ", attr, "=", attrs.getValue(attr)            
            raise
    def endElement(self, name):
        if name==u'title':
            if self.title is None:
                self.title = u''.join(self.content).strip()
        elif name==u'idno':
            if (self.docid is None) and (self.content is not None):
                self.docid = u''.join(self.content).strip()
        elif name==u'classCode':
            if self.content is not None:
                self.classCode = u''.join(self.content).strip()
                self.content = None
        elif name==u's':
            try:
                # insert dparse into into the words hash
                for gr in self.dparse:
                    # if dep defined, attach to that word, if not use head (passive, prt)
                    if gr[u'dep'] is None:
                        if gr[u'head'] not in self.ntoi:
                            # note: it may not be in there because rasp may have incorrectly
                            # handled gaps such that there is misalignment
                            continue
                        headidx = self.ntoi[gr[u'head']]
                        if u'dep' not in self.words[headidx]:
                            self.words[headidx]['dep'] = []
                        depidx = None
                        # note: it may not be in there because rasp may have incorrectly
                        # handled gaps such that there is misalignment
                        self.words[headidx]['dep'] = {u'type':gr[u'type'],
                                                      u'subtype':gr[u'subtype']}
                    else:
                        if gr[u'dep'] not in self.ntoi:
                            continue
                        # depidx is a number: use it. head may or may not exist
                        depidx = self.ntoi[gr[u'dep']]
                        if gr[u'head'] is None:
                            headidx = None
                        else:
                            if gr[u'head'] not in self.ntoi:
                                continue
                            headidx = self.ntoi[gr['head']]
                        #print gr[u'dep'], self.dparse, self.words
                        if u'dep' not in self.words[depidx]:
                            self.words[depidx]['dep'] = []
                        self.words[depidx]['dep'] = {u'type':gr['type'],
                                                     u'subtype':gr['subtype'],
                                                     u'head':gr['head']}
                        
                # save the sent element
                sentelem = {u'id':u'BNC:%s:%s'%(self.docid,self.sentno),
                            u'idx':len(self.sentences),
                            u'text':u''.join(self.senttext),
                            u'word':self.words,
                            u'dparse':self.dparse}
                self.sentences.append(sentelem)
            except:
                print >> sys.stderr, "Error:",self.docid,name,self.sentno
                print >> sys.stderr, "Words:",self.words
                print >> sys.stderr, "DParse:",self.dparse
                raise
        elif name in [u'w',u'c',u'gap']:
            # skip if there's no content
            if self.content is None:
                return
            # compute start and end positions of the current word
            # by maintaining a variable with the length of the sentence
            # so far
            wordtext = u''.join(self.content)
            self.senttext.append(wordtext)
            self.word['form'] = wordtext.strip()
            self.word['start'] = self.sentlen
            self.word['end'] = self.sentlen + len(self.word['form'])
            self.word['idx'] = len(self.words) #idx is usu 1 less than n because it indexes the array
            if u' ' in self.word['n']:
                # this is account for n="3 4 5" for words like "show/tell"
                for eachn in self.word['n'].split(u' '):
                    self.ntoi[eachn] = self.word['idx']
            else:
                self.ntoi[self.word['n']] = self.word['idx']
            self.words.append(self.word)
            self.sentlen += len(wordtext)
            self.content = None
        elif name=='bncDoc':
            # end of document, create the doc json structure
            docheader = mnjson.getJSONDocumentHeader(self.docid,
                                                     u'BNC',
                                                     self.title,
                                                     u'BNC:'+self.docid,
                                                     self.classCode,
                                                     len(self.sentences))
            self.document = mnjson.getJSONRoot(u'en',docs=[docheader],
                                               sents=self.sentences)
            
    def characters(self, content):
        if self.content is not None:
            self.content.append(content)
    
    def getDocument(self):
        return self.document

def convert_bncxml_to_json(infile):
    """
    Converts RASP-parsed BNC-XML to json.
    """
    inputhandler = BNCXMLHandler()
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    parser.parse(infile)
    
    return inputhandler.getDocument()
