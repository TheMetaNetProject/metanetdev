# coding=utf-8
"""Created on May 3, 2012 @author: lucag
"""

from __future__ import print_function

import sys, re
from util import uopen, uwriter
from pprint import pprint

def find(relation, stream):
    """Finds <relation> in <stream>.
    """ 
    rel_re = re.compile(r'%s:\d+ %s:\d+' % relation, re.UNICODE)
    print(rel_re)
    
    for line in stream:
        if rel_re.match(line):
            rels, sent = line.split('|') 
            yield rels, sent[:-1]
        
        
def main(indexname, verb, noun):
    with uopen(indexname, 'r') as stream:
        for i, (_, sentence) in enumerate(find((verb, noun), stream)):
            print(i + 1, sentence)
        
tabjoin = u'\t'.join
nljoin = u'\n'.join

def findm(index, relations, outs):
    for record in index:
        try: 
            sent_id, _, _, k, n, v = record
        except ValueError:
            print(u'problem with', tabjoin(record), file=uwriter(sys.stderr))
        if (k, n, v) in relations:
            print(sent_id, k, n, v, sep=u'\t', file=outs)
            print(sentence(int(sent_id)), file=outs)

def read(vnpairs, kind):
    return set((kind, n, v) for v, n in vnpairs)
 
def split(f, decode=False, sep=None):
    return (l.decode('utf8').rstrip().split(sep) for l in f) if decode else (l.rstrip().split(sep) for l in f)

from os import path
from itertools import islice

def sentence(sent_id, files=512, chunk=4096):
    fn, pos = divmod(sent_id - 1, chunk)
    dn = fn // files
    with uopen(path.join('%.2x' % dn, '%.4x.ss' % fn)) as f:
        return islice(f, pos, pos + 1).next()
    
if __name__ == '__main__':
    args = sys.argv[1:]
    
    multiple = '-m' in args
    if not multiple:
        main(*args)
    else:
        index, vs, vo = args[1:5]
        r = dict(vo=u'1-компл', vs=u'предик') 
        outs = uwriter(sys.stdout)
        with uopen(vs) as vss, uopen(vo) as vos, open(index) as indexs:
            relations = read(split(vss), r['vs']) | read(split(vos), r['vo']) 
#             for k, n, v in relations:
#                 print(k, n, v, sep=u'\t', file=uwriter(sys.stderr))
                
            findm(split(indexs, decode=True, sep=u'\t'), relations, outs)