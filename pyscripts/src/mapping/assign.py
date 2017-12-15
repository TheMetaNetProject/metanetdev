"""
.. module:: assign
    :platform: Unix
    :synopsis: Assignment of relations given source and target base forms. 

Assignment of relations given source and target base forms. 
Created on Nov 4, 2013. 

.. moduleauthor:: Luca Gilardi <lucag@icsi.berkeley.edu>

.. note:: 
    This only applies to English, Spanish and Russian.
    
"""

from __future__ import print_function

import os, json, gzip, sys, sqlite3
from depparsing.util import Environment, uopen, uwriter, ureader, update
from pprint import pprint
from textwrap import dedent

# Only change this
env = Environment(CL='/u/metanet/corpolexica', 
                  BNC='/u/metanet/corpolexica/EN/bnc', 
                  MAPPINGS='/n/banquet/dc/lucag/metanet/AssignMappings',
                  SD='{CL}/{lang}/m4mapping/Source_Domains_{lang}',
                  CACHE='{CL}/{lang}/m4mapping/cache',
                  REL='{CL}/{lang}/m4mapping/relations.db',
                  dobj='{BNC}/DirectObjRels.txt-uniqed-sorted', 
                  iobj='{BNC}/IndirectObjRels.txt-underscore-uniqed-sorted', 
                  ncsubj='{BNC}/SubjectRels.txt-uniqed-sorted', 
                  ncmod='{BNC}/NounModifierRels.txt-uniqed-sorted')


def verb2nouns(triples, reverse=False):
    """Create a mapping of verbs to nouns.
    
    :param triples: the input (count, noun, verb) tuples. 
    :returns: a verb -> [(noun, count)] mapping object.
    
    """
    m = dict()
    if not reverse:
        for f, n, v in triples:
            m.setdefault(v, []).append((n, int(f)))
    else:
        for f, n, v in triples:
            m.setdefault(n, []).append((v, int(f)))
    return m 


def noun2source(dnlists):
    """Find the source domain given a noun.
    
    :param dnlists: (domain, noun*) elements.
    :returns: a map noun -> domain name.
    
    """
    return dict((n, l[0]) for l in dnlists for n in l)
    
def as_var(s): 
    return '{%s}' % s 

class Assigner(object):
    """Assign a source (noun) word from a target (i.e. verb)-relation pair.
    """
    def __init__(self, lang):
        lang = lang.upper()
        db = env('{REL}', lang=lang)
        update(self, conn=sqlite3.connect(db), lang=lang)
        with uopen(env('{SD}', lang=lang)) as domf:
            records = (l.strip().split() for l in domf)
            self.sources = noun2source(records)
        
    def get_verb2nouns(self, verb, relation):
        assert verb.islower() and relation.islower(), (verb, relation)
        
        cachefn = env('{CACHE}/{verb}-{relation}.json.gz', verb=verb, relation=relation)     
        if os.access(cachefn, os.R_OK):
            with ureader(gzip.open(cachefn, 'rb')) as cachef:        
                return json.load(cachef)
        else:
            relfn = env(as_var(relation))
            reverse = relation == 'iobj' # XXX
            with uwriter(gzip.open(cachefn, 'wb')) as cachef, uopen(relfn) as relf:
                # Some lines do not contain three fields, so...
                triples = (r for r in (l.rstrip().split() for l in relf) if len(r) == 3)
                m = verb2nouns(triples, reverse)
                json.dump(m, cachef, encoding='utf8', ensure_ascii=False, indent=2)
                return m
    
    def assign2(self, verb, relation):
        """Assign a noun from a verb-relation pair, using a a database. Fast. 
        
        :param verb: a verb or target word.
        :param relation: a relation name. 
        :type relation: a string, as specified by the parser used. 
        
        """
        sql = """\
            select noun from nvrel 
            where verb='%s' and reltype='%s' 
            order by n desc 
            """
#         pprint(nouns)
        ss = []
        for n, in self.conn.execute(sql % (verb, relation)):
            s = self.sources.get(n)
            if s: ss.append(s) 
        return ss
                
    def assign(self, verb, relation):
        """Assign a noun from a verb-relation pair, creating a cache. Relatively slow. 
        
        :param verb: a verb or target word.
        :param relation: a relation name. 
        :type relation: a string, as specified by the parser used. 
        
        """
        nouns = self.get_verb2nouns(verb, relation)
        ss = []
        for n, _ in sorted(nouns.get(verb, ()), key=lambda (n, f): (f, n), reverse=True):
            s = self.sources.get(n)
            if s: 
                ss.append(s) 
        return ss

    def relation(self, verb, noun):
        sql = """\
            select     n, reltype 
            from       nvrel where verb='%s' and noun='%s'
            order by   n desc 
            """
        rr = [r for r in self.conn.execute(sql % (verb, noun))]
        return rr

    def gassign(self, verb, noun):
        """Guess most likely relation form target and source.
        
        :param verb: the target word.
        :param noun: the source word:
        
        """
        r = self.relation(verb, noun)
        return self.assign2(verb, r[0][1]) if r else None 
    

def domain(lang, verb, relation):
    nouns2 = Assigner(lang).assign2(verb, relation)
#     print('assign2:')
#     pprint(nouns2[:10], stream=uwriter(sys.stdout))
#     nouns = Assigner().assign(verb, relation)
#     print('assign:')
#     pprint(nouns[:10], stream=uwriter(sys.stdout))
    print('Source (new alg.):', nouns2[0])
#     print('Source:', nouns[0])
    return 0

def gdomain(lang, verb, noun):
    d = Assigner(lang).gassign(verb, noun)
    print('Guessed source:', d[0] if d else '<unknown>')
    return 0
    
def relation(lang, noun, verb):
    assigner = Assigner(lang)
    rels = assigner.relation(verb, noun)
    print('Possible relations:', u', '.join('%s [%s]' % (r, c) for c, r in rels), 
          file=uwriter(sys.stdout))
    return 0

def usage(args):
    from os.path import basename
    msg = """\
        Usage: {0} -l en|es|ru -r <verb-or-noun> <noun> 
               {0} -l en|es|ru -g <verb-or-noun> <noun>
               {0} -l en|es|ru -d <verb-or-noun> <relation>""".format(basename(args[0]))
    print(dedent(msg), file=sys.stderr)
    return -1
    
def getarg(args, opt, arity=1):
    try:
        i = 1 + args.index(opt)
        arg = args[i:i + arity]
        if len(arg) < arity:
            sys.exit(usage)
        return arg[0] if arity == 1 else arg
    except:
        sys.exit(usage(args))
        
def main(args):
    lang = getarg(args, '-l')
    if '-r' in args:
        verb, noun = getarg(args, '-r', 2)
        return relation(lang, noun, verb)
    elif '-d' in args:
        verb, rel = getarg(args, '-d', 2)
        return domain(lang, verb, rel)
    elif '-g' in args:
        verb, rel = getarg(args, '-g', 2)
        return gdomain(lang, verb, rel)
    else:
        return usage(sys.argv)

if __name__ == '__main__':
    sys.exit(main(sys.argv))