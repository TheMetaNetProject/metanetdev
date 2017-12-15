"""Created on July 20, 2013 by @author: lucag@icsi.berkeley.edu
"""

from __future__ import print_function

import re

from collections import OrderedDict, namedtuple
from ...util import takewhile, uopen, ureader, uwriter 
from pprint import pformat
from itertools import ifilter 

tag = re.compile(r'<[^>]+>', re.UNICODE)

ConllxRecord = namedtuple('ConllxRecord', ['id', 'form', 'lemma', 'cpostag', 'postag', 'feats', 'head', 'deprel', 'phead', 'pdeprel'])

def as_conll(records):
    """Input: <word, tag> records; output structure:
    1    Pierre    _    NNP    NNP    _
    """
    for r in records:
        l = len(r)
        if l == 1:
            yield ()
        elif l == 2:
            w, t = r
            yield (unicode(1), w, u'_', t, t, u'_')
        elif l == 3:
            word, pos, lemma = r
            p = pos[0]
            yield (unicode(1), word, lemma, p, p, pos)
        elif l == 4:
            word, pos, lemma, _ = r
            p = pos[0]
            yield (unicode(1), word, lemma, p, p, pos)
        else:
            raise RuntimeError('r is %s' % r)


#def as_conllx((form, lemma, pos, prob)):
def as_conllx(r):
    (form, lemma, pos, _) = r[0:4]
    return (form, lemma, pos[0].lower(), pos)
            
def parse(it):
    while True:
        goodones = ifilter(lambda (_, l): not tag.findall(' '.join(l)), it)
        try:
            b = [line for n, line in takewhile(lambda (_, l): l[1] != 'SENT', goodones)]
        except IndexError:
            print('Problem in', n, pformat(line))
            raise
        if len(b): 
            yield b
        else:
            break


import sys
from depparsing import split 
from depparsing.util import uwriter

def checker(parser):
    """Returns a function that checks whether a sentence is good for Malt parsing.
    """    
    # Sentence splitter
    split_re = split.splitter(parser)
    terms = set(u'.!?')
    uerr = uwriter(sys.stderr)
    
    def term_count(sent):
        "Return the number of sentence terminators."
        return sum(map(lambda t: len(set(t) & terms), split_re.findall(sent)))
    
    def is_good(sent):
        if term_count(sent) > 1:
            print(u'parsemet: more than 1 sentence terminator: |{}|'.format(sent), file=uerr)
            return False
        return True
    return is_good
        
def sentence(block):
    return OrderedDict((l[4], l[0]) for l in block)

def main(args):
    ins = ureader(sys.stdin) if args.in_fn == '-' else uopen(args.in_fn)
    outs = uwriter(sys.stdout) if args.out_fn == '-' else uopen(args.out_fn, 'w+b')
    tabjoin = u'\t'.join
#     with ins, outs:
    for b in as_conll(l.rstrip().split(u'\t') for l in ins):
        print(tabjoin(b), file=outs)
        
def argparser():
    from argparse import ArgumentParser
    p = ArgumentParser(description='Output CONNL format file as input to MALT.')
    p.add_argument('-i', dest='in_fn', default='-', metavar='<filename>', help='Input file')
    p.add_argument('-o', dest='out_fn', default='-', metavar='<filename>', help='Output file')
    return p
    
if __name__ == '__main__':
    main(argparser().parse_args())