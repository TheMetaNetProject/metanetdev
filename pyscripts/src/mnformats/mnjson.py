#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: mnjson
   :platform: Unix
   :synopsis: MetaNet Interchange JSON format utility methods

Utility methods for building, reading, and writing the MetaNet interchange JSON format.
A jsonschema schema which describes the format can be found at

https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json

At to the top level the json file is structured as follows:
{
'encoding': 'UTF-8',
'lang': 'en',
'jsonschema': 'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json',
'documents': [],
'sentences': []
}
The lang field should identify the language of the file via a 2 letter code.  Currently,
these are either 'en', 'es', 'fa', or 'ru'.

The documents array contains items with the following structure:
{
'name':'document name',
'corpus':'corpus name',
'description':'description of the document',
'provenance':'uri to the document',
'type':'blog',
'size':number of sentences,
'pubdate':'2014-07-14',
'perspective':'individual oversight'
}

The document name should be unique.  The type field should contain a string that identifies what kind of document it is 'news',
'blog', 'journal article', etc.  If publication date is not available on the document itself
it should contain the date that the document was retrieved, i.e. if it was fetched from the
web.  It must be in the YYYY-MM-DD format.  The perspective contains a string that identifies the perspective, 
or none if it is neutral or irrelevant.

The sentences array contains items with the following structure:
{
id':'sentence identifier',
'idx': index of this sentence in the array,
'text': u'the sentence text'
}

The sentence identifier must have the form 'document name:sentence number' to uniquely
identify the sentence.

The structure defined above is sufficient for input into the current LM detection system.

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""

import ujson, pprint, logging, traceback
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
from mnpipeline.treetagger import TreeTagger
from depparsing.parser.util import sanitized

reload(sys)
sys.setdefaultencoding('utf-8')

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

METANET_IXSCHEMA = u'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json'
SEPARATOR = "____"

# ===================================================================
# Utility functions for constructing parts of the JSON format:
# - root, document, sentence
#

def getJSONRoot(lang='en',jschema=METANET_IXSCHEMA,docs=None,sents=None):
    """ Generate root structure for JSON format
    """
    jroot = {'encoding':'UTF-8',
             'lang':lang,
             'jsonschema':jschema,
             'documents':docs,
             'sentences':sents}
    return jroot

def getJSONDocumentHeader(name='',corp='',desc='',prov='',type='',size=0,lang=None,pubdate=None,persp=None):
    """ Generate document header structure for JSON """
    jdoc = {'name':name,
            'corpus':corp,
            'description':desc,
            'provenance':prov,
            'type':type,
            'size':size}
    if lang:
        jdoc['lang']=lang
    if pubdate:
        jdoc['pubdate']=pubdate
    if persp:
        jdoc['perspective']=persp
    return jdoc

def getJSONSentence(id='',idx=0,text=''):
    """ Generate minimal sentence structure for JSON """
    jsent = {u'id':id,
             u'idx':idx,
             u'text':text}
    return jsent

# ========================================================================
# Utility functions for reading and writing JSON format
#

def writefile(fname, jobj):
    """ write the json dict to file
    """
    if fname.endswith('.gz'):
        with gzip.open(fname,"wb") as f:
            ujson.dump(jobj, f, ensure_ascii=True)
    else:
        with codecs.open(fname,"w",encoding='utf-8') as f:
            ujson.dump(jobj, f, ensure_ascii=True)

def loadfile(fname):
    """ load the file an return the json data as a dict """
    jdata = None
    if fname.endswith('.gz'):
        with gzip.open(fname,'rb') as f:
            jdata = ujson.load(f)
    else:
        jdata = ujson.load(file(fname))
    return jdata

####################################################################################
####################################################################################
#
# Below this point are converters for various kinds of file formats that we've
# had to deal with.
#
####################################################################################
####################################################################################

class MNTreeTagger:
    """
    A wrapper class around TreeTagger, for running it on the sentences list in the
    JSON format and distributing the tags into the format's list of word properties.
    TreeTagger is used for English, Spanish, and Russian.
    
    """
    langmap = {'en': 'english',
               'es': 'spanish',
               'ru': 'russian',
               'fa': None}
    
    def __init__(self,lang):
        """
        :param lang: language
        :type lang: str
        """
        self.tagger = TreeTagger(encoding='utf8',language=self.langmap[lang])
        self.logger = logging.getLogger(__name__)
        self.lang = lang
        
    def cleanText(self, sentences):
        """ Clean the sentence texts of problematic characters and save the result
        in ctext field.
        """
        sqre = re.compile(u'[’‘’‹›]',flags=re.U)
        dqre = re.compile(u'[“”«»„“]',flags=re.U)
        ntdotre = re.compile(ur'[.]([^0-9])', flags=re.U)
        ntmarkre = re.compile(ur'[!?](.)', flags=re.U)
        plere = re.compile(ur'([.!?])+$', flags=re.U)
        for sent in sentences:
            sent['ctext'] = sanitized(dqre.sub(u'"',sqre.sub(u'\'',sent['text'].strip()))).replace(u'\u00A0',u' ')
            if self.lang in ['ru', 'fa']:
                sent['ctext'] = ntmarkre.sub(r',\1,',
                                             ntdotre.sub(r',\1',
                                                         plere.sub(r'\1',sent['ctext'])))        
    def run(self, sentences):
        """ Run the POS tagger and Add tags in the 'word' field of sentences. Note
        that TreeTagger also lemmatizes. """
        textkey = 'text'
        if 'ctext' in sentences[0]:
            textkey = 'ctext'
        taggedsents = self.tagger.tag([sent[textkey] for sent in sentences])
        sentidx = -1
        for taggedsent in taggedsents:
            sentidx += 1
            sentence = sentences[sentidx]
            sentpos = 0
            sentwords = []
            otext = sentence['text']
            # don't process empty sentences
            if not otext:
                continue
            try:
                widx = -1
                for tagset in taggedsent:
                    widx += 1
                    if len(tagset)==3:
                        (word,pos,lemma) = tagset
                    elif len(tagset)==1:
                        word=tagset[0]
                        pos='X'
                        lemma=tagset[0]
                    else:
                        continue
                    if word=='\'' or word=='"':
                        # just ignore ' and " since we do substitution on it
                        tword = {'idx':widx,
                                 'form':word,
                                 'pos':pos,
                                 'lem':lemma,
                                 'start':None,
                                 'end':None,
                                 'n':str(widx+1)}
                    else:
                        startindex = otext.find(word,sentpos)
                        endindex = startindex + len(word)
                        sentpos = endindex
                        if lemma=='<unknown>':
                            lemma = word
                        if lemma=='@card@':
                            lemma = word
                        if self.lang=='es':
                            if (word.lower().startswith(u'impuesto')) and (lemma.lower()==u'imponer'):
                                lemma=u'impuesto'
                                pos=u'NC'
                            elif (word.lower()==u'crean') and (lemma.lower()==u'crear|creer'):
                                lemma=u'crear'
                            elif (lemma.lower()==u'dolar|doler') and pos.startswith('V'):
                                lemma=u'doler'
                            elif lemma.lower()==u'henchir|hinchar':
                                lemma=u'hinchar'
                            elif lemma.lower()==u'salar|salir':
                                lemma=u'salir'
                            elif lemma.lower()==u'deuda|deudo':
                                lemma=u'deuda'
                        elif self.lang=='en':
                            if (word.lower()==u'taxes') and (lemma.lower()==u'taxis'):
                                lemma=word[0:3]
                        tword = {'idx':widx,
                                 'form':word,
                                 'pos':pos,
                                 'lem':lemma,
                                 'start':startindex,
                                 'end':endindex,
                                 'n':str(widx+1)}
                    sentwords.append(tword)
            except ValueError:
                print >> sys.stderr, "Error processing tags:",taggedsent
                raise
            if 'word' in sentence and sentence['word']:
                if len(sentence['word']) != len(sentwords):
                    print >> sys.stderr, 'sentence[word]=', sentence['word']
                    print >> sys.stderr, 'sentwords=', sentwords
                    for widx in range(max(len(sentwords),len(sentence['word']))):
                        try:
                            print >> sys.stderr, sentence['word'][widx], '<==>', sentwords[widx]
                        except:
                            try:
                                print >> sys.stderr, sentence['word'][widx], '<==> X'
                            except:
                                print >> 'X <==>', sentwords[widx]
                    raise Exception("Error processing sentence %d: sent[word]len=%s but wordslen=%d." % (sentidx,
                                                                                                         len(sentence['word']),
                                                                                                         len(sentwords)))
                else:
                    for widx in range(len(sentwords)):
                        # merge the tags into existing words
                        sentence['word'][widx].update(sentwords[widx])
            else:              
                sentence['word'] = sentwords
                
    def findLMWord(self,wstring,wfstart,words,searchfield='form',returnfield='lem'):
        """ Given a wordform and its start position, find the corresponding word
        in the list of words. """
        if wstring.endswith(u'\'s') or wstring.endswith(u'\u2019s'):
            # truncate 's
            wstring = wstring[0:-2]
        if u' ' in wstring:
            # its a MWE!  Run findLMWord on the first word of the MWE, then
            # concatenate the lemmas corresponding to the other words.
            # Note: this is not guaranteed to be correct
            wstrings = wstring.split()
            idx, lem = self.findLMWord(wstrings[0],wfstart, words)
            lems = []
            for i in range(idx,idx+len(wstrings)):
                w = words[i]
                lems.append(w[returnfield])
            return idx, u' '.join(lems)
        closeWs = []
        for w in words:
            # in some cases IARPA's target/source tags split a word, e.g. <tg>burocracia>/tg>
            # so use startswith rather than == as criteria
            if w[searchfield].lower().startswith(wstring.lower()):
                if wfstart==w['start']:
                    return w['idx'], w[returnfield]
                else:
                    closeWs.append((abs(wfstart-w['start']), w['idx'], w[returnfield]))
        # These are matches but the start position doesn't line up.  In that case
        # return the match that is closest in position
        if closeWs:
            closeWs = sorted(closeWs, key=lambda w: w[0])
            return closeWs[0][1], closeWs[0][2]
        else:
            raise LookupError
        
    def processLMs(self, sentences):
        """ go through all the LMs and find their corresponding word to retrieve lemmas """
        for sent in sentences:
            if not 'lms' in sent:
                continue
            words = sent['word']
            for lm in sent['lms']:
                tg = lm['target']
                sc = lm['source']
                if 'lemma' not in tg:
                    try:
                        widx, tg['lemma'] = self.findLMWord(tg['form'],tg['start'],words)
                        if u' ' not in tg['lemma']:
                            # not a MWE, save POS
                            tg['pos'] = words[widx]['pos']
                            # check if form needs to be fixed
                            if (words[widx]['form'].lower() != tg['form'].lower()) and \
                                words[widx]['form'].lower().startswith(tg['form'].lower()):
                                self.logger.warn('correcting LM target form %s to %s in %s',
                                                 tg['form'],words[widx]['form'],sent['id'])
                                tg['form']=words[widx]['form']
                    except LookupError:
                        self.logger.error("error in sentence %s: target form %s not found"%(sent['id'],tg['form']))
                if 'lemma' not in sc:
                    try:
                        widx, sc['lemma'] = self.findLMWord(sc['form'],sc['start'],words)
                        if u' ' not in sc['lemma']:
                            # not a MWE, save POS
                            sc['pos'] = words[widx]['pos']
                            # check if form needs to be fixed
                            if (words[widx]['form'].lower() != sc['form'].lower()) and \
                                words[widx]['form'].lower().startswith(sc['form'].lower()):
                                self.logger.warn('correcting LM source form %s to %s in %s',
                                                 sc['form'],words[widx]['form'],sent['id'])
                                sc['form']=words[widx]['form']
                    except LookupError:
                        self.logger.error("error in sentence %s: source form %s not found"%(sent['id'],sc['form']))
                if ('form' not in tg) and ('start' in tg):
                    try:
                        widx, tg['form'] = self.findLMWord(tg['lemma'],tg['start'],words,searchfield='lem',returnfield='form')
                    except LookupError:
                        self.logger.error("error in sentence %s: target lemma %s not found"%(sent['id'],tg['lemma']))
                        
                
def validate(insource,schemapath=None):
    """ validate JSON object or file by default against the schema
        on the metanet wiki site
    """
    global METANET_IXSCHEMA
    # determine type of data to validate and load it up
    if type(insource)==file:
        data = json.load(file(insource),encoding="UTF-8")
    elif type(insource)==dict:
        data = insource
    else:
        raise Exception("Unsupported source type for validation:"+type(insource))
    # load up the schema
    # if one is passed as parameter, use that.  If not, then look in the data.
    # If not there, then use the default.
    if not schemapath:
        # first look at data itself
        if u'jsonschema' in data:
            schemapath = data[u'jsonschema']
        else:
            schemapath = METANET_IXSCHEMA
    if schemapath.startswith("http"):
        schema = json.load(urllib2.urlopen(schemapath), encoding="UTF-8")
    else:
        schema = json.load(file(schemapath),encoding="UTF-8")
    # run validation and return
    return(jsonschema.validate(data, schema))
        

class IARPATestSetXMLHandler(sax.ContentHandler):
    """
    Builds subcorpora 1 per language based on content of XML file
    which is in the TestSet format specified by IARPA
    """
    currentTestSetId = ""
    currentTextId = ""
    currentSId = ""
    currentLang = ""
    str_list = []
    subcorps = {}
    pertext = False
    currentIndex = ""
    
    def __init__(self, pertext):
        self.pertext = pertext
        sax.ContentHandler.__init__(self)

    def startElementNS(self, name, qname, attributes):
        global SEPARATOR
        (namespace, localname) = name
        if localname == u'TestSet':
            self.currentTextId = ""
            self.currentSId = ""
            self.currentLang = ""
            self.currentTestSetId = attributes.getValueByQName(u'testId')
        elif localname == u'Text':
            self.currentTextId = attributes.getValueByQName(u'id')
            self.currentLang = attributes.getValueByQName(u'lang')
            if self.pertext:
                self.currentIndex = self.currentTestSetId + SEPARATOR + self.currentTextId + SEPARATOR + self.currentLang
            else:
                self.currentIndex = self.currentLang
            if self.currentLang not in self.subcorps:
                self.subcorps[self.currentIndex] = []
            self.currentSId = ""
        elif localname == u'S':
            self.currentSId =  attributes.getValueByQName(u'id')
            self.str_list = []
        return

    def endElementNS(self, name, qname):
        (namespace, localname) = name
        if localname == u'S':
            sentelem = {}
            sentelem['id'] = self.generateSentenceId()
            sentelem['text'] = u''.join(self.str_list)
            self.subcorps[self.currentIndex].append(sentelem)
            self.currentSId = ""
 
    def characters(self, content):
        # save content only in case of S element
        if self.currentSId != "":
            self.str_list.append(content)

    def generateSentenceId(self):
        return u':'.join([self.currentTestSetId,
                         self.currentTextId,
                         self.currentSId]);

    def getSubcorpora(self):
        return self.subcorps

class IARPAResultXMLHandler(sax.ContentHandler):
    """
    Reads Result format and converts into wiki
    """    
    testId = u''
    teamId = u''
    count = u''
    
    content = []
    result = {}
    readContent = False
    resultlines = []
    summarylines = []
    intdir = u''
    timestamp = u''
    domain = u''
    testtype = u''
    tscounter = 0
    lmflagcounter = 0
    
    def __init__(self, intdir, timestamp, domain=u'', testtype=u''):
        self.intdir = intdir
        self.timestamp = timestamp
        self.domain = domain
        self.testtype = testtype
        self.tscounter = 0
        self.lmflagcounter = 0
        sax.ContentHandler.__init__(self)

    def startElementNS(self, name, qname, attributes):
        global SEPARATOR
        (namespace, localname) = name
        self.readContent = False
        if localname == u'ResultSet':
            self.testId = attributes.getValueByQName(u'testId')
            self.teamId = attributes.getValueByQName(u'teamId')
            self.count = attributes.getValueByQName(u'count')
        elif localname == u'Result':
            self.result = {}
            self.result[u'id'] = attributes.getValueByQName(u'id')
        else:
            self.readContent = True
            self.content = []
        return

    def endElementNS(self, name, qname):
        global SEPARATOR
        (namespace, localname) = name
        if localname == u'ResultSet':
            self.summarylines.append(u'{{TestSummary')
            if self.domain:
                self.summarylines.append(u'|Domain='+self.domain)
            if self.testtype:
                self.summarylines.append(u'|Type='+self.testtype)
            self.summarylines.append(u'|Timestamp='+self.timestamp)
            self.summarylines.append(u'|TeamId='+self.teamId)
            self.summarylines.append(u'|Number of sets='+str(self.tscounter))
            self.summarylines.append(u'|Number of sets with LMs='+str(self.lmflagcounter))
            percent = 100.0 * (float(self.lmflagcounter) / float(self.tscounter))
            self.summarylines.append(u'|Percentage of sets with LMs=%.1f' % (percent))
            self.summarylines.append(u'}}')
        elif localname == u'Result':
            self.tscounter += 1
            self.resultlines.append(u'{{TestResult')
            for elem, value in self.result.iteritems():
                if (elem=="LmFlag") and (value=="1"):
                    self.lmflagcounter += 1
                self.resultlines.append(u'|{0}={1}'.format(elem,value))
            self.resultlines.append(u'}}')
            # parse the intermediate json file
            intfile = u'{0}/processed.{1}{2}{3}.json.post'.format(self.intdir,
                                                                  self.testId,
                                                                  SEPARATOR,
                                                                  self.result[u'id'])
            if os.path.exists(intfile):
                jsondoc = loadfile(intfile)
                if 'sentences' in jsondoc:
                    for sent in jsondoc['sentences']:
                        self.resultlines += convert_jsonsentence_wikiexample(sent)
        elif self.readContent:
            content = u''.join(self.content)
            self.result[localname] = content
 
    def characters(self, content):
        # save content only in case of S element
        if self.readContent:
            self.content.append(content)
            
    def getResults(self):
        results = []
        results += self.summarylines
        results += self.resultlines
        return results

def convert_iarpa_testset_to_jsonlist(infile, pertext=False):
    """
    Converts iarpa testset file to MN JSON.  Returns a dict of JSON dictionary
    objects, indexed either by lang or by textid + SEP + lang depending
    on whether pertext is set.
    """
    global METANET_IXSCHEMA, SEPARATOR
    jsondict = {}
    
    inputhandler = IARPATestSetXMLHandler(pertext)
        
    # setup a NS enabled SAX parser
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    parser.setFeature(sax.handler.feature_namespaces, 1)
    # let parser do decoding
    parser.parse(infile)
    
    # retrieve subcorpora from inputhandler
    subcorps = inputhandler.getSubcorpora()
    
    # if pertext is NOT set, then subcorps is indexed by lang (en, es, ru)
    # but if pertext is set, then it is indexed by testsetid SEP textid SEP
    # lang.
    #
    for index in subcorps:
        # setup outfile
        setid = None
        textid = None
        lang = index
        filespec = lang
        if pertext:
            (setid,textid,lang) = index.split(SEPARATOR)
            filespec = setid + SEPARATOR + textid

        documentnode = {}
        documentnode['lang'] = lang
        documentnode['encoding'] = u'UTF-8'
        documentnode['jsonschema'] = METANET_IXSCHEMA
        documentnode['sentences'] = subcorps[index]
        jsondict[filespec] = documentnode
        
    return jsondict

def convert_spl_to_json(linesource, lang, docname,
                        corpus=None,
                        description=None,
                        provenance=None,
                        doctype=None,
                        comments=False):
    '''
    linesource - is either an open file, or a list of strings
    comments - indicates that the first column contains comments that should be associate with the respective sentence
    '''
    subcorp = []
    sentnumber = 0
    for sent in linesource:
        # skip comments which start with a # sign
        text = sent.strip()
        if (not text) or text.startswith(u'#'):
            continue
        sentnumber += 1
        s = getJSONSentence(u'%s:%d' % (docname,sentnumber),
                            sentnumber-1,
                            text)
        # if the comments flag is set then the first column (tab-separated)
        # should be parsed as a comment
        if comments:
            m = re.search(u'^([^\t]+)\t(.*)$',text)
            if m:
                s[u'text'] = m.group(2).strip()
                s[u'comment'] = m.group(1)
        subcorp.append(s)
        
    docheader = getJSONDocumentHeader(name=docname,
                                      corp=corpus,
                                      desc=description,
                                      prov=provenance,
                                      type=doctype,
                                      size=sentnumber,
                                      lang=lang)
    jsonroot = getJSONRoot(lang,docs=[docheader],sents=subcorp)

    return jsonroot

def get_csv_from_gdoc(pageurl):
    """
    returns a csv reader from a google doc url
    """
    wordlist = []
    page = urllib2.urlopen(pageurl)
    reader = csv.reader(page)
    return reader

def get_json_from_sentences(sentences, lang, provenance=u''):
    global METANET_IXSCHEMA
    # setup outfile
    documentnode = {}
    documentnode['lang'] = lang
    documentnode['encoding'] = u'UTF-8'
    documentnode['jsonschema'] = METANET_IXSCHEMA
    if provenance:
        documentnode['provenance'] = provenance
    # filter english sentences out of Persian examples
    if lang=='fa':
        fsentences = []
        for sent in sentences:
            # heuristic: if the first two words are ascii-based words, then skip
            if re.search(r'^[A-Za-z0-9_-]+ [A-Za-z0-9_-]+',sent['text'],re.U|re.I):
                continue
            else:
                fsentences.append(sent)
        documentnode['sentences'] = fsentences
    else:
        documentnode['sentences'] = sentences
    return documentnode

def add_csv_to_sentlist(csvreader, sentlist, sentence_col, subdomain_col, comment_col, idprefix=u''):
    rownum = -1
    idcounter = len(sentlist) + 1
    for row in csvreader:
        rownum += 1
        # skip header
        if rownum==0:
            continue
        colnum = -1
        sentence = None
        comment = None
        subdomain = None
        for col in row:
            colnum += 1
            cellval = col.decode('utf=8').strip()
            if int(sentence_col)==colnum:
                # read the sentence, replace consecutive whitespace with space
                sentence = re.sub(r'\s+',r' ',cellval,0,re.U|re.I)
            if int(comment_col)==colnum:
                # read the comment
                comment = cellval
            if is_int(subdomain_col):
                if int(subdomain_col)==colnum:
                    subdomain = cellval
            else:
                subdomain = subdomain_col
        if sentence:
            sent = {}
            sent['id'] = idprefix + str(idcounter)
            idcounter += 1
            sent['text'] = sentence
            if comment:
                sent['comment'] = comment
            if subdomain:
                if 'comment' in sent:
                    sent['comment'] = subdomain + ': '+sent['comment']
                else:
                    sent['comment'] = subdomain
            sentlist.append(sent)

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def convert_text_to_json(linesource, lang, idprefix=u'', provenance=u''):
    """
    Converts running text to json.  Newlines are assumed to mark
    paragraphs, which are indicated in the id string.
    """
    global METANET_IXSCHEMA
    subcorp = []
    paragnumber = 0
    for line in linesource:
        line = line.strip()
        # skip blank lines
        if not line:
            continue
        paragnumber += 1
        sentences = nltk.tokenize.sent_tokenize(line)
        sentnumber = 0     
        for sent in sentences:
            sentnumber += 1
            s = {'id':u'{0}p{1}:s{2}'.format(idprefix,str(paragnumber),str(sentnumber)),
                 'text':sent.strip()}
            subcorp.append(s)
    
    # setup outfile
    documentnode = {}
    documentnode['lang'] = lang
    documentnode['encoding'] = u'UTF-8'
    documentnode['jsonschema'] = METANET_IXSCHEMA
    if provenance:
        documentnode['provenance'] = provenance
    documentnode['sentences'] = subcorp
    return documentnode

class BNCFakeXMLHandler(sax.ContentHandler):
    def __init__(self):
        self.sentcontent = None
    def startElement(self, name, attrs):
        if name==u's':
            # start sentence charlist
            self.sentcontent = []
        elif name==u'text':
            self.docid = attrs.getValue(u'id')
            self.title = attrs.getValue(u'title')
            self.sentlist = []
            self.sentid = 0
    def endElement(self, name):
        global METANET_IXSCHEMA
        if name==u's':
            self.sentid += 1
            text = u''.join(self.sentcontent)
            sent = {u'id':u'BNC:%s:%d'%(self.docid,self.sentid),
                    u'text':text}
            self.sentlist.append(sent)
            self.sentcontent = None
        elif name==u'text':
            documentnode = {}
            documentnode['lang'] = u'en'
            documentnode['encoding'] = u'UTF-8'
            documentnode['jsonschema'] = METANET_IXSCHEMA
            documentnode['provenance'] = u'BNC:'+self.docid
            documentnode['description'] = self.title
            documentnode['sentences'] = self.sentlist
            ofname = u'BNC_%s.json'%(self.docid)
            writefile(ofname,documentnode)
    def characters(self, content):
        if self.sentcontent is not None:
            self.sentcontent.append(content)

class ENGWXMLHandler(sax.ContentHandler):
    
    def __init__(self, infilename, outputdir, maxdocs, corpusname='ENGW_5E', zip=True):
        self.jdata = {u'encoding':u'UTF-8',
                      u'lang':u'en',
                      u'jsonschema':METANET_IXSCHEMA,
                      u'documents':[],
                      u'sentences':[]}
        self.outputdir = outputdir
        self.maxdocs = maxdocs
        self.docchunkno = 0
        self.docno = 0
        self.infbase = os.path.basename(infilename).split('.')[0]
        if zip:
            self.ext = 'json.gz'
        else:
            self.ext = 'json'
        self.corpusname = corpusname
        self.initDoc()
    
    def initDoc(self):
        self.content = None
        self.title = None
        self.docid = None
        self.doctype = None
        self.datestring = None
        self.sentno = 0
    
    def startElement(self, name, attrs):
        try:
            if name==u'DOC':
                self.initDoc()
                self.docid = attrs.getValue('id')
                self.doctype = attrs.getValue('type')
            elif name==u'HEADLINE':
                if self.title is None:
                    self.content = []
            elif name==u'DATELINE':
                if self.datestring is None:
                    self.content = []
            elif name==u'TEXT':
                self.content = []
            elif name==u'P':
                self.content = []
        except:
            print >> sys.stderr, "Error:", self.docid, name
            for attr in attrs.keys():
                print >> sys.stderr, "  ", attr, "=", attrs.getValue(attr)            
            raise
        
    def endElement(self, name):
        if name==u'HEADLINE':
            if self.title is None:
                self.title = u''.join(self.content).strip()
        elif name==u'DATELINE':
            if self.datestring is None:
                self.datestring = u''.join(self.content).strip()
        elif name in [u'TEXT',u'P']:
            if self.content:
                contentstring = u''.join(self.content).strip()
                sents = sent_tokenize(contentstring)
                for sent in sents:
                    senttext = sent.replace('\n',' ').strip()
                    if not senttext:
                        continue
                    self.sentno += 1
                    sentelem = {u'id':u'%s:%s:%s'%(self.corpusname,self.docid,self.sentno),
                                u'doc':self.docid,
                                u'idx':self.sentno-1,
                                u'text':senttext}
                    self.jdata[u'sentences'].append(sentelem)
                self.content = None
        elif name=='DOC':
            # end of document, create the doc json structure
            docHeader = {u'name':self.docid,
                         u'corpus':self.corpusname,
                         u'description':self.title,
                         u'provenance':self.corpusname+u':'+self.docid,
                         u'type':self.doctype,
                         u'size':self.sentno,
                         u'lang':u'en',
                         u'pubdate':self.datestring}
            self.jdata[u'documents'].append(docHeader)
            self.docno += 1
            if self.docno == self.maxdocs:
                # write out the file
                self.docchunkno += 1
                self.docno = 0
                ofname = '%s/%s_%03d.%s' % (self.outputdir,self.infbase,self.docchunkno,self.ext)
                print "trying to write: ",ofname
                writefile(ofname,self.jdata)
                # refresh self.jdata
                self.jdata = {u'encoding':u'UTF-8',
                              u'lang':u'en',
                              u'jsonschema':METANET_IXSCHEMA,
                              u'documents':[],
                              u'sentences':[]}
    
    def characters(self, content):
        if self.content is not None:
            self.content.append(content)
            
    def getDocument(self):
        return self.jdata
    

class ESGWXMLHandler(sax.ContentHandler):
    
    def __init__(self, infilename, outputdir, maxdocs, zip=False):
        self.jdata = {u'encoding':u'UTF-8',
                      u'lang':u'es',
                      u'jsonschema':METANET_IXSCHEMA,
                      u'documents':[],
                      u'sentences':[]}
        self.outputdir = outputdir
        self.maxdocs = maxdocs
        self.docchunkno = 0
        self.docno = 0
        self.infbase = os.path.basename(infilename).split('.')[0]
        if zip:
            self.ext = 'json.gz'
        else:
            self.ext = 'json'
        self.initDoc()
    
    def initDoc(self):
        self.content = None
        self.title = None
        self.docid = None
        self.doctype = None
        self.sentno = 0
    
    def startElement(self, name, attrs):
        try:
            if name==u'DOC':
                self.initDoc()
                self.docid = attrs.getValue('id')
                self.doctype = attrs.getValue('type')
            elif name==u'HEADLINE':
                if self.title is None:
                    self.content = []
            elif name==u'TEXT':
                self.content = []
            elif name==u'P':
                self.content = []
        except:
            print >> sys.stderr, "Error:", self.docid, name
            for attr in attrs.keys():
                print >> sys.stderr, "  ", attr, "=", attrs.getValue(attr)            
            raise
    def endElement(self, name):
        if name==u'HEADLINE':
            if self.title is None:
                self.title = u''.join(self.content).strip()
        elif name in [u'TEXT',u'P']:
            if self.content:
                contentstring = u''.join(self.content).strip()
                sents = sent_tokenize(contentstring)
                for sent in sents:
                    senttext = sent.replace('\n',' ').strip()
                    if not senttext:
                        continue
                    self.sentno += 1
                    sentelem = {u'id':u'ESGW:%s:%s'%(self.docid,self.sentno),
                                u'doc':self.docid,
                                u'idx':self.sentno,
                                u'text':senttext}
                    self.jdata[u'sentences'].append(sentelem)
                self.content = None
        elif name=='DOC':
            # end of document, create the doc json structure
            self.jdata[u'documents'].append({'name':self.docid,
                                            'corpus':u'ESGW',
                                            'description':self.title,
                                            'provenance':u'ESGW:'+self.docid,
                                            'type':self.doctype,
                                            'size':self.sentno})
            self.docno += 1
            if self.docno == self.maxdocs:
                # write out the file
                self.docchunkno += 1
                self.docno = 0
                ofname = '%s/%s_%03d.%s' % (self.outputdir,self.infbase,self.docchunkno,self.ext)
                writefile(ofname,self.jdata)
                # refresh self.jdata
                self.jdata = {u'encoding':u'UTF-8',
                              u'lang':u'es',
                              u'jsonschema':METANET_IXSCHEMA,
                              u'documents':[],
                              u'sentences':[]}
    def characters(self, content):
        if self.content is not None:
            self.content.append(content)
    def getDocument(self):
        return self.jdata

class BNCXMLHandler(sax.ContentHandler):
    
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
                    return
                self.content = []
                rpos = None
                if u'rpos' in attrs:
                    rpos = attrs.getValue(u'rpos')
                self.word = OrderedDict([(u'idx',None),
                                         (u'form',None),
                                         (u'rpos',rpos),
                                         (u'n',attrs.getValue(u'n')),
                                         (u'lem',attrs.getValue(u'lem')),
                                         (u'c5',attrs.getValue(u'c5')),
                                         (u'pos',attrs.getValue(u'pos')),
                                         (u'hw',attrs.getValue(u'hw'))])
            elif name==u'c':
                self.content = []
                self.word = OrderedDict([(u'idx',None),
                                         (u'form',None),
                                         (u'rpos',attrs.getValue(u'rpos')),
                                         (u'n',attrs.getValue(u'n')),
                                         (u'lem',attrs.getValue(u'lem')),
                                         (u'c5',attrs.getValue(u'c5')),
                                         (u'pos',None),
                                         (u'hw',None)])
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
                    self.word = OrderedDict([(u'idx',None),
                                             (u'form',None),
                                             (u'n',attrs.getValue(u'n')),
                                             (u'desc',desc),
                                             (u'lem',attrs.getValue(u'lem')),
                                             (u'rpos',rpos),
                                             (u'resp',resp),
                                             (u'reason',reason)])
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
                self.gritem = OrderedDict([(u'type',attrs.getValue(u'type')),
                                           (u'subtype',subtype),
                                           (u'head',head),
                                           (u'dep',dep)])
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
                        self.words[headidx]['dep'].append(OrderedDict([(u'type',gr[u'type']),
                                                                       (u'subtype',gr[u'subtype'])]))
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
                        self.words[depidx]['dep'].append(OrderedDict([(u'type',gr['type']),
                                                                      (u'subtype',gr['subtype']),
                                                                      (u'head',headidx)]))
                        
                # save the sent element
                sentelem = OrderedDict([(u'id',u'BNC:%s:%s'%(self.docid,self.sentno)),
                                        (u'idx',len(self.sentences)),
                                        (u'text',u''.join(self.senttext)),
                                        (u'word',self.words),
                                        (u'dparse',self.dparse)])
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
        elif name=='bncDoc':
            # end of document, create the doc json structure
            docheader = OrderedDict([('name',self.docid),
                                     ('corpus',u'BNC'),
                                     ('description',self.title),
                                     ('provenance',u'BNC:'+self.docid),
                                     ('type',self.classCode),
                                     ('size',len(self.sentences))])
            self.document = OrderedDict([(u'encoding',u'UTF-8'),
                                         (u'lang',u'en'),
                                         (u'jsonschema',METANET_IXSCHEMA),
                                         (u'documents',[docheader]),
                                         (u'sentences',self.sentences)])
            
    def characters(self, content):
        if self.content is not None:
            self.content.append(content)
    
    def getDocument(self):
        return self.document

def convert_bnctext_to_json(infile):
    """
    Converts running text to json.  Newlines are assumed to mark
    paragraphs, which are indicated in the id string.
    """
    inputhandler = BNCFakeXMLHandler()
    
    # setup a SAX parser
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    # let parser do decoding
    parser.parse(infile)
    
    return 0

def convert_bncxml_to_json(infile):
    """
    Converts RASP-parsed BNC-XML to json.
    """
    inputhandler = BNCXMLHandler()
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    parser.parse(infile)
    
    return inputhandler.getDocument()

def convert_esgw_to_json(infile, outputdir, maxdocs):
    """
    Converts spanish GW (XML) to json.
    """
    inputhandler = ESGWXMLHandler(infile,outputdir,maxdocs,zip=True)
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    try:
        print "parsing ",infile
        parser.parse(infile)
    except:
        traceback.print_exc(file=sys.stderr)
        raise

def convert_engw_to_json(infile, outputdir, maxdocs, corpus, dozip):
    """
    Converts English GW (XML/SGML) to json.
    """
    inputhandler = ENGWXMLHandler(infile,outputdir,maxdocs,corpus, dozip)
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    fixes = [(u'&AMP;',u'&amp;'),
             (u'&AMP\n;',u'&amp;\n'),
             (u'&\nAMP;',u'&amp;\n'),
             (u'&\namp;',u'&amp;\n'),
             (u'&amp\n;',u'&amp;\n'),
             (u'&lt\n;',u'&lt;\n'),
             (u'&\nlt;',u'&lt;\n'),
             (u'&gt\n;',u'&gt;\n'),
             (u'&\ngt;',u'&gt;\n'),
             (u'<3\n',u'&lt;3\n'),
             (u'&#8211;',u'\u2013'),
             (u'&#8217;',u'\u2019'),
             (u'&#8220',u'\u201C'),
             (u'&#8221',u'\u201D'),
             (u'&#8213',u'\u2015'),
             (u'&#8547',u'\u2163')]
    try:
        print "parsing ",infile
        if infile.endswith('.gz'):
            tempfile = '/tscratch/tmp/'+os.path.basename(infile)+'.tmp'
            with codecs.open(tempfile,'w',encoding='utf-8') as tf:
                print >> tf, u'<DOCROOT>'
                with gzip.open(infile,'rb') as f:
                    content = unicode(f.read())
                    for badc, goodc in fixes:
                        content = content.replace(badc, goodc)
                    print >> tf, content
                print >> tf, u'</DOCROOT>'
            parser.parse(tempfile)
            os.remove(tempfile)
        else:
            parser.parse(infile)
    except:
        traceback.print_exc(file=sys.stderr)
        print >> sys.stderr, "Failed to convert:", infile
        raise
    
def convert_jsonsentence_wikiexample(sent):
    lines = []
    lines.append(u'{{TestSentence')
    lines.append(u'|Id='+sent['id'].replace(u'|',u'{{!}}'))
    lines.append(u'|Text='+sent['text'].replace(u'|',u'{{!}}'))
    if 'mtext' in sent:
        lines.append(u'|Match text='+sent['mtext'].replace(u'|',u'{{!}}'))
    if 'comment' in sent:
        lines.append(u'|Comments='+sent['comment'].replace(u'|',u'{{!}}'))
    else:
        lines.append(u'|Comments=')
    if ('lms' in sent) and (len(sent['lms']) > 0):
        lmlist = []
        for lm in sent['lms']:
            if ("rel" in lm["target"]) and (lm["target"]["rel"] == "object"):
                seedsegs = lm["seed"].split()
                namesegs = lm["name"].split()
                seed = u'seed:{0},score:{1}'.format(seedsegs[1] + " " + seedsegs[0],format_score(lm["score"]))
                name = namesegs[1] + " " + namesegs[0]
            else:
                seed = u'seed:{0},score:{1}'.format(lm["seed"],format_score(lm["score"]))
                name = lm["name"]
                if "cxn" in lm:
                    seed = u'cxn:{0},tw:{1},sw:{2},tdom:{3},sdom:{4},score:{5}'.format(lm["cxn"],
                                                                             lm["target"]["mword"],
                                                                             lm["source"]["mword"],
                                                                             lm["target"]["wdomain"],
                                                                             lm["source"]["wdomain"],
                                                                             format_score(lm["score"]))
                    seed = re.sub(r'\|',r'<nowiki>|</nowiki>',seed,0,re.I|re.U)
            lmlist.append(u'{0} ({1})'.format(name,seed))
        lines.append(u'|LMs='+u',<br/>'.join(lmlist))
    else:
        lines.append(u'|LMs=')
    lines.append(u'}}')
    return lines

def format_score(score):
    pscore = "%.2f" % math.log10(float(score))
    return pscore

def sentence_has_lm(sent):
    if ('lms' in sent) and (len(sent['lms']) > 0):
        return True
    return False

def convert_json_wiki(jsondoc, title=u'', logcontent=u'', timestamp=u'',domain=u'',typeinfo=u''):
    numsents = 0
    numsentswlms = 0
    lines = []
    lines.append(u'xxxx')
    lines.append(u'\'\'\''+title+u'\'\'\'')
    examples = []
    # for counts, don't include duplicates
    dupechecker = {}
    if 'sentences' in jsondoc:
        for sent in jsondoc['sentences']:
            if sent['text'] not in dupechecker:
                numsents += 1
                dupechecker[sent['text']] = 1
                if sentence_has_lm(sent):
                    numsentswlms += 1
            examples += convert_jsonsentence_wikiexample(sent)
    percent = 100.0 * (float(numsentswlms) / float(numsents))
    lines.append(u'{{TestSummary')
    if domain:
        lines.append(u'|Domain='+domain)
    if typeinfo:
        lines.append(u'|Type='+typeinfo)
    lines.append(u'|Timestamp='+timestamp)
    lines.append(u'|Number of sentences='+str(numsents))
    lines.append(u'|Number of sentences with LMs='+str(numsentswlms))
    lines.append(u'|Percentage of sentences with LMs=%.1f' % (percent))
    lines.append(u'}}')
    lines += examples
    if logcontent:
        lines.append("<pre>")
        lines.append(logcontent)
        lines.append("</pre>")
    lines.append(u'yyyy')
    return lines

def convert_iarpa_results_wiki(resultsxml,intdir,title=u'',logcontent=u'',timestamp=u'',domain=u'',typeinfo=u''):
    inputhandler = IARPAResultXMLHandler(intdir,timestamp,domain,typeinfo)
        
    # setup a NS enabled SAX parser
    parser = sax.make_parser()
    parser.setContentHandler(inputhandler)
    parser.setFeature(sax.handler.feature_namespaces, 1)
    # let parser do decoding
    parser.parse(resultsxml)
    
    # retrieve subcorpora from inputhandler
    resultlines = inputhandler.getResults()
    lines = []
    lines.append(u'xxxx')
    lines.append(u'\'\'\''+title+u'\'\'\'')
    lines += resultlines
    if logcontent:
        lines.append("<pre>")
        lines.append(logcontent)
        lines.append("</pre>")
    lines.append(u'yyyy')
    return lines
    
def convert_json_html(jsondoc,title=""):
    html = []
    table = []
    html.append('<?xml version="1.0" encoding="UTF-8"?>')
    html.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"')
    html.append(' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
    html.append(u'<html><head><title>{0}</title></head>'.format(title))
    html.append(u'<body><h1>{0}</h1>'.format(title))
    table.append('<table border="1">');
    sentlookup = {}
    numdupes = 0
    numsents = 0
    nummetsents = 0
    for sent in jsondoc['sentences']:
        if sent['text'] in sentlookup:
            numdupes += 1
            continue
        else:
            sentlookup[sent['text']] = 1
        numsents += 1
        # check if it has a metaphor
        lmlist = set()
        if ("lms" in sent) and (len(sent["lms"]) > 0):
            nummetsents += 1
            for lm in sent['lms']:
                if lm["target"]["rel"] == "object":
                    seedsegs = lm["seed"].split()
                    namesegs = lm["name"].split()
                    seed = seedsegs[1] + " " + seedsegs[0]
                    name = namesegs[1] + " " + namesegs[0]
                else:
                    seed = lm["seed"]
                    name = lm["name"]
                lmlist.add(u'{0} ({1})'.format(name,seed))
        if 'comment' in sent:
            tblock = u'{0}<br /><font color="blue">{1}</font>'.format(sent['text'],sent['comment'])
        else:
            tblock = sent['text']
        table.append(u'<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(sent['id'],
                                                                           tblock,
                                                                           u'<br />'.join(lmlist)))
    table.append("</table>");
    html.append(u'<p># Sents with LMs: {0} / {1} ({2} duplicates)</p>'.format(nummetsents,
                                                                          numsents,
                                                                          numdupes))
    html += table
    html.append("</body></html>")
    return html

