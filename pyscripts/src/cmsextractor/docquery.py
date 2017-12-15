"""
.. module:: docquery
   :platform: Unix
   :synopsis: Module to query documents (e.g. lists of sentences and properties thereof) via RDF

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

Module for querying sentences in a document via their grammatical properties.
Converts documents (lists of sentences) to RDF, for querying, with rdflib,
redland librdf, or a Sesame SPARQL Endpoint.  Reads construction queries from
external files and allows for searches on the documents.

By default the constructions are read from file paths of the form:

``/u/metanet/extraction/cxns/LANG/cxn_queries.txt``

This can be overridden via an environment variable ``MNEXTRACTPATH`` which when
set causes the constructions to be read from paths of the form:

``$MNEXTRACTPATH/cxns/LANG/cxn_queries.txt``

Constructions are captured as either SPARQL queries or as regular expressions
on form, lemma, and POS tag sequences.  The following are examples from English
of the 's possessive::

    # =========================================================
    # 's Posessives: poverty's undertow
    #
    START CXN: **T-noun_poss_S-noun
    SELECT ?tlemma ?slemma ?sentidx ?tidx ?sidx
    WHERE {
        ?sent rdf:type doc:Sentence .
        ?sent doc:hasIdx ?sentidx .
        ?target rdf:type doc:Word .
        ?target doc:hasIdx ?tidx .
        ?target doc:hasLemma ?tlemma .
        ?source rdf:type doc:Word .
        ?source doc:hasIdx ?sidx .
        ?source doc:hasLemma ?slemma .
        ?target doc:inSentence ?sent .
        ?source doc:inSentence ?sent .
        ?target doc:poss ?source .
    }
    END CXN
    
    # =========================================================
    # 's Posessives: poverty's morass
    #
    START CXN: **T-noun_poss_S-noun.POSseq
    REGEXP: \b[^=]+=(?P<tlemma>[^=]+)=[^=]+=(?P<tidx>\d+) 's='s=POS=\d+ [^=]+=(?P<slemma>[^=]+)=[^=]+=(?P<sidx>\d+)\b

Note that regular expression queries must define named match groups ``tlemma``,
``slemma``, ``tidx``, and ``sidx``.

"""
import logging, os, time, random, traceback
import cPickle as pickle
import string, sys, json, re, itertools, string
import codecs, logging, pprint
from cStringIO import StringIO
import sparrow
from sparrow.error import QueryError

TRIPLES_PER_INSERT = 150000
    
class DocumentRepository:
    """
    May be more appropriate to rename this DocumentGraph.  It converts sentences,
    along with lemma, pos tags, and dependency parse into an RDF representation
    which can then be searched using SPARQL.
    """
    queryBaseDir = '/u/metanet/extraction/cxns'
    ascii_letters_digits = string.ascii_letters + string.digits
        
    def __init__(self,lang,posf='pos', lemf='lem', rposf='rpos', rlemf='rlem', engine='rdflib', name=None):
        """ Initializes the document repository.
        
        :param lang: language
        :type lang: str
        :param posf: POS field to map to hasPOS
        :type posf: str
        :param lemf: Lemma field to map to hasLemma
        :type lemf: str
        :param rposf: auxiliary POS field to map to hasRPOS
        :type rposf: str
        :param rlemf: auxiliary Lemma field to map to hasRLemma
        :type rlemf: str
        :param engine: query engine type (rdflib, redland, sesame).
            Sesame should be appended with ':' + repository server name (localhost, or DNS)
        :type engine: str
        :param name: name of graph in the triplestore
        :type name: str
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing Document Repository...')
        if 'MNEXTRACTPATH' in os.environ:
            self.queryBaseDir = os.environ['MNEXTRACTPATH']+'/cxns'
        self.lang = lang
        self.pfield = posf
        self.lfield = lemf
        self.rpfield = rposf
        self.rlfield = rlemf
        self.defaultCxnQueryFile = '%s/%s/cxn_queries.txt' % (self.queryBaseDir,self.lang)
        self.nonWre = re.compile(ur'\W',flags=re.U)
        self.engine = engine
        if engine=='rdflib':
            self.tstore = sparrow.database('rdflib','memory')
        elif engine=='redland':
            self.tstore = sparrow.database('redland','memory')
        elif engine.startswith('sesame'):
            eng, server = engine.split(':',1)
            self.engine = eng
            self.repnum = random.randint(0,7)
            self.repname = 'dproc%d' % (self.repnum)
            serverstr = 'http://%s:8080/%s' % (server, self.repname)
            self.tstore = sparrow.database('sesame', serverstr)
        else:
            self.logger.error('Unsupported query engine: %s', engine)
            raise
        self.tstore.register_prefix('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.tstore.register_prefix('xsd','http://www.w3.org/2001/XMLSchema#')
        self.tstore.register_prefix('doc','https://metaphor.icsi.berkeley.edu/metaphor/DocumentOntology.owl#')
        self.tstore.register_prefix('dr','https://metaphor.icsi.berkeley.edu/metaphor/DocumentRepository.owl#')
        self.tstore.compute_query_header()
        self.turtleHeader = self.tstore.get_turtle_header()
        if not name:
            name = self.random_str(32)
        self.gnameiri = self.tstore.get_ns('dr')[:-1]+'/d_'+name
        
    def loadCXNQueries(self, infname=None):
        """ Method that parses and loads cxn query specification files.
        :param infname: file path to query file
        :type infname: str
        """
        if not infname:
            infname = self.defaultCxnQueryFile
        cxnname = None
        cxnqueries = {}
        cxnregexps = {}
        linebuffer = []
        with codecs.open(infname, encoding='utf-8') as f:
            for line in f:
                # skip comments / blanks
                if line.startswith('#') or (not line.strip()):
                    continue
                if line.startswith('START CXN:'): # read CXN name
                    cxnname = line[10:].strip()
                    continue
                if line.startswith('END CXN'):
                    if linebuffer:
                        cxnqueries[cxnname] = u''.join(linebuffer)
                        linebuffer = []
                    continue
                if line.startswith('REGEXP:'):
                    cxnregexps[cxnname] = line[7:].strip()
                    continue
                if (self.engine != 'rdflib') and line.startswith('WHERE'):
                    linebuffer.append(u'FROM <%s>\n' % (self.gnameiri))
                linebuffer.append(line)

        self.cxnQueries = {}
        for cxnname, qstr in cxnqueries.iteritems():
            try:
                self.cxnQueries[cxnname] = u'%s\n%s' % (self.tstore.get_query_header(),
                                                        qstr)
                self.tstore.add_pquery(cxnname, qstr)
            except:
                self.logger.error("Error in cxn query %s: %s" % (cxnname,qstr))
                raise
        
        self.cxnRegexps = {}
        for cxnname, restr in cxnregexps.iteritems():
            try:
                self.cxnRegexps[cxnname] = re.compile(restr, flags=re.U|re.I)
            except:
                self.logger.error("Error in cxn regexp %s: %s" % (cxnname,restr))
                raise
        self.cxnRegexpStrings = cxnregexps
        self.logger.info('Loaded %d sparql and %d regexp cxn queries from %s.',
                         len(self.cxnQueries),len(self.cxnRegexps),infname)
            
    def getCXNRelatedPairs(self, cxns=None, allcxns=False):
        """
        Iterates through the queries in self.qlookup, which for
        now contains construction matching queries.  One or the
        other argument, or both, can be specified to narrow
        the search.
        
        Returns a list of tuples:
        (cxn_name, tlemma, slemma, sent_index, target_word_index, source_word_index)
        
        The indices are numerical and represent the index of the
        sentence in sentences list, or the index of the words
        in the sentence's word list.
        :param cxns: list of cxn names
        :type cxns: list
        :param allcxns: flag to ignore cxn names and search for all cxns
        :type allcxns: bool
        """
        rset = set()

        if not allcxns:
            # by default, only do the privileged cxns
            qcxnlist = filter(lambda cname: cname.startswith('**'), self.cxnQueries.keys())
            rcxnlist = filter(lambda cname: cname.startswith('**'), self.cxnRegexps.keys())
        else:
            qcxnlist = self.cxnQueries.iterkeys()
            rcxnlist = self.cxnRegexps.iterkeys()
            if cxns:
                qcxnlist = filter(lambda cname: cname in cxns, self.cxnQueries.keys())
                rcxnlist = filter(lambda cname: cname in cxns, self.cxnRegexps.keys())

        for cxn in qcxnlist:
            self.logger.info('searching for cxn %s', cxn)
            #self.logger.info('query:\n%s',self.cxnQueries[cxn])
            try:
                for row in self.tstore.pselect(cxn):
                    rset.add((cxn, row['tlemma']['value'],row['slemma']['value'],
                              int(row['sentidx']['value']),
                              int(row['tidx']['value']), int(row['sidx']['value'])))
            except QueryError:
                self.logger.error(u'Error in cxn query: %s',self.cxnQueries[cxn])
                raise
                    
        for cxn in rcxnlist:
            self.logger.debug('searching for cxn %s'%(cxn))
            for sent in self.sentences:
                #print "Cxn:",cxn,"  Regexp:,", self.cxnRegexpStrings[cxn]
                #print "MText", sent['mtext']
                for matches in self.cxnRegexps[cxn].finditer(sent['mtext']):
                    #pprint.pprint((cxn, matches.group('tlemma'), matches.group('slemma'),
                    #          int(sent['idx']), int(matches.group('tidx')), int(matches.group('sidx'))))
                    rset.add((cxn, matches.group('tlemma'), matches.group('slemma'),
                              int(sent['idx']), int(matches.group('tidx')), int(matches.group('sidx'))))
        return sorted(rset, key=lambda rtuple: rtuple[5])
                
    def newSentence(self, sent):
        """ Create a new graph containing one new sentence.  This method is used by the
        rdflib based CMS execution mode which builds graphs for each sentence separately
        for cxn searching (for rdflib performance reasons).
        
        :param sent: a sentence dict as per the JSON format
        :type sent: dict
        """
        self.deleteSentencesGraph()
        self.sentences = []
        self.numsents = 1
        self.numwords = 0
        self.addSentence(sent)
                
    def createSentencesGraph(self, sentences):
        """ Create a graph containing all the sentences provided.  This is used by the
        sesame CMS execution mode which builds a graph for a set of sentences.
        
        :param sentences: list of sentences (JSON structs)
        :type sentences: list
        """
        global TRIPLES_PER_INSERT
        
        # note sentences are added to this list later as triples are computed
        self.sentences = []
        # numbers for stats
        self.numsents = len(sentences)
        self.numwords = 0
        self.logger.info("Inserting %s sentences into triplestore",self.numsents)
        self.logger.info("Graph name <%s>",self.gnameiri)
        triplestrings = []
        ntriples = 0
        for sent in sentences:
            triples = self.getSentenceTriples(sent)
            triplestrings.extend(triples)
            ntriples += len(triples)
            while len(triplestrings) > TRIPLES_PER_INSERT:
                triplestoinsert = triplestrings[:TRIPLES_PER_INSERT]
                triplestrings = triplestrings[TRIPLES_PER_INSERT:]
                updatedata = u'%s\n%s' % (self.turtleHeader, u'\n'.join(triplestoinsert))
                self.tstore.add_turtle(StringIO(updatedata), self.gnameiri)
                self.logger.info('added %d triples'%(ntriples))
        if triplestrings:
            updatedata = u'%s\n%s' % (self.turtleHeader, u'\n'.join(triplestrings))
            self.tstore.add_turtle(StringIO(updatedata), self.gnameiri)
            self.logger.debug(updatedata)
        self.logger.info("Done %d triples into triplestore",ntriples)
        self.logger.info("Contexts in the repository: %s",pprint.pformat(self.tstore.contexts()))
        if self.numsents:
            self.logger.info("Stats: %d sentences, %.1f words/sent, %.1f triples/sent",
                             self.numsents,float(self.numwords)/float(self.numsents),
                             float(ntriples)/float(self.numsents))
        else:
            self.logger.info("Stats: 0 sentences.")
    
    def random_str(self, n):
        """ Return a random alpha numeric ascii string of the given length.
        
        :param n: length of string
        :type n: int
        :returns: string of length n
        """
        return "".join([random.choice(self.ascii_letters_digits) for x in xrange(n)])

    def deleteSentencesGraph(self):
        """ Delete the sentences graph.
        """
        self.logger.info("Deleting graph")
        self.tstore.clear(self.gnameiri)
        self.logger.info("Done deleting graph")
    
    def getLit(self, raw):
        """ Given a raw value and optional type information, return an RDF Literal.
        """
        if type(raw) is int:
            return u'"%d"^^xsd:integer'%(raw)
        if type(raw) is bool:
            return u'"%s"^^xsd:boolean'%(str(raw).lower())
        if type(raw) is float:
            return u'"%f"^^xsd:float'%(raw)
        return u'"%s"'%(raw.replace('\\','\\\\').replace('"',ur'\"'))
        
             
    def getDepTriples(self, sent, w, wbyn):
        """ Generate and return RDF triples for dependency relations in the sentence.
        
        :param sent: sentence structure
        :type sent: dict
        :param w: list of word nodes in the graph
        :type w: list
        :param wbyn: dict of word nodes indexed by n (rank)
        :type wbyn: dict
        :returns: list of triples
        """
        triples = []
        # third pass, dep relations
        if 'dparse' in sent:
            for dep in sent[u'dparse']:
                if dep[u'type']==u'passive':
                    try:
                        triples.append(u'%s doc:isPassive %s .' % (wbyn[dep[u'head']],self.getLit(True)))
                    except:
                        # if it doesn't work, forget it
                        pass
                    continue
                try:
                    # problem here that prevents it from working on Spanish, Russian, Persian--
                    # the dependency relation type labels are not the same
                    #print >> sys.stderr, wbyn[dep[u'dep']], self.getRelURI(dep[u'type']), wbyn[dep['head']]
                    #print >> sys.stderr, sent[u'word'][int(dep[u'dep'])-1][self.lfield], dep[u'type'], sent[u'word'][int(dep[u'head'])-1][self.lfield]
                    if (dep[u'type']==u'ncmod') and ('subtype' in dep) \
                            and (dep['subtype']=='poss'):
                        typestr = 'poss'
                    else:
                        typestr = dep['type'].replace(u'-',u'')
                    triples.append(u'%s doc:%s %s .' % (wbyn[dep[u'dep']],typestr,wbyn[dep['head']]))
                except KeyError:
                    # skip these
                    pass
            return triples

        # No dparse element: use the ones in word instead
        for word in sent[u'word']:
            idx = word[u'idx']
            if 'dep' not in word:
                continue
            headn = word['dep']['head']
            if int(headn) == 0:
                continue
            try:
                #print >> sys.stderr, w[idx], self.getRelURI(word['dep']['type']), w[headidx]
                #print >> sys.stderr, word[self.lfield], word['dep']['type'], sent[u'word'][headidx][self.lfield]
                if (word['dep']['type']=='ncmod') and ('subtype' in word['dep']) \
                        and (word['dep']['subtype']=='poss'):
                    typestr = 'poss'
                else:
                    typestr = word['dep']['type'].replace(u'-',u'')
                triples.append(u'%s doc:%s %s .' % (w[idx], typestr, wbyn[headn]))
            except KeyError:
                # skip these
                pass
            except TypeError:
                pass
        return triples

    def getWordTriples(self, sent, sid, snode):
        """ Generate and return triples that capture per-word properties of the sentence.
        
        :param sent: sentence structure (JSON)
        :type sent: dict
        :param sid: sentence id that identifies the sentence node in the graph
        :type sid: str
        :param snode: URI of the sentence node in the graph
        :type snode: str
        :returns: list of triples
        """
        # first pass, add words & word properties
        triples = []
        w = []
        wbyn = {}
        if u'word' in sent:
            self.numwords += len(sent[u'word'])
        else:
            return triples, w, wbyn
        for word in sent[u'word']:
            idx = word[u'idx']
            w.append(u'dr:w_%s_%d'%(sid,idx))
            if u'n' not in word:
                word[u'n'] = str(idx+1)
            try:
                wbyn[word[u'n']] = w[idx]
            except IndexError:
                self.logger.error(u'Word index error: \nword=%s\nw=%s\n%s',
                                  pprint.pformat(sent['word']),
                                  pprint.pformat(w),
                                  traceback.format_exc())
                raise
            triples.append(u'%s doc:hasIdx %s; rdf:type doc:Word; doc:inSentence %s .' % (w[idx],
                                                                                          self.getLit(idx),
                                                                                          snode))
            if word[self.pfield] != None:
                triples.append(u'%s doc:hasPOS %s .' % (w[idx], self.getLit(word[self.pfield])))
            triples.append(u'%s doc:hasForm %s .' % (w[idx], self.getLit(word[u'form'])))
            if word[self.lfield] != None:
                triples.append(u'%s doc:hasLemma %s .' % (w[idx], self.getLit(word[self.lfield])))
            # add secondary lem/pos tags too
            if self.rlfield in word:
                triples.append(u'%s doc:hasRLemma %s .' % (w[idx], self.getLit(word[self.rlfield])))
            if self.rpfield in word:
                triples.append(u'%s doc:hasRPOS %s .' % (w[idx], self.getLit(word[self.rpfield])))
            if idx > 0:
                triples.append(u'%s doc:follows %s .' % (w[idx], w[idx-1]))
        
        # second pass, precedes relations
        for word in sent[u'word']:
            idx = word[u'idx']
            if idx < len(w)-1:
                triples.append(u'%s doc:precedes %s .' % (w[idx], w[idx+1]))
        return triples, w, wbyn
    
    def getSentTriples(self, sent):
        """ Generate and return triples pertaining just to the sentence.
        """
        sid = self.nonWre.sub('_',sent[u'id'])
        snode = u'dr:s_'+sid
        triples = []
        triples.append(u'%s rdf:type doc:Sentence; doc:hasIdx %s .' % (snode,
                                                                       self.getLit(sent[u'idx'])))
        #triples.append(u'%s doc:hasText ""'%(snode, self.getLit(sent[u'text'])))
        return triples, sid, snode
        
    def addSentence(self, sent):
        """ Add a sentence to the graph
        
        :param sent: a sentence dict as per the JSON format
        :type sent: dict
        """
        striples, sid, snode = self.getSentTriples(sent)     
        self.sentences.append(sent)
        # add word tripes
        wtriples, w, wbyn = self.getWordTriples(sent, sid, snode)
        # dep relations
        deptriples = self.getDepTriples(sent, w, wbyn)
        updatedata = u'%s\n%s' % (self.turtleHeader,
                                  u'\n'.join(itertools.chain(striples,wtriples,deptriples)))
        self.tstore.add_turtle(StringIO(updatedata), self.gnameiri)
    
    def getSentenceTriples(self,sent):
        """ Generate and return triples for the sentence, including words, and dependencies.
        """
        striples, sid, snode = self.getSentTriples(sent)     
        self.sentences.append(sent)
        # add word tripes
        wtriples, w, wbyn = self.getWordTriples(sent, sid, snode)
        # dep relations
        deptriples = self.getDepTriples(sent, w, wbyn)
        return striples + wtriples + deptriples
        
def main():
    """ Main function for testing.
    """
    sg = SentenceGraph("en","rpos","lem")
    infile = sys.argv[1]
    jdata = json.load(file(infile),encoding="utf-8")
    for sent in jdata['sentences']:
        sg.addSentence(sent)
    for (cxn,tlemma, slemma) in sg.getRelatedWords(targetlemma='poverty'):
        print cxn, tlemma, slemma
    
    #for mrow in sg.searchMetCxn('subj-v'):
    #    print "target-subj:",mrow.tlemma, "   source-v:",mrow.slemma
    #for mrow in sg.searchMetCxn('v-dobj'):
    #    print "source-v",mrow.slemma, "    target-dobj:",mrow.tlemma
    
if __name__ == "__main__":
    status = main()
    sys.exit(status)
