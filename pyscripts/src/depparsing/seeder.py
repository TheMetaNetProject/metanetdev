"""Created on Apr 23, 2013 by @author: lucag@icsi.berkeley.edu
"""

import sys
from util import uopen, update, derivations
from string import join
from pprint import pprint

def usage(args):        
    from textwrap import dedent
    print dedent("""\
        Usage: {} -i <input seed file> -o <output>\
        """.format(args)) 
    sys.exit(-1)

class Seed(object):
    def __init__(self, noun, verb): update(self, noun=noun, verb=verb)

class SV(Seed): 
    def __str__(self): return 'subject-verb %s.n %s.v' %(self.noun, self.verb)
    __repr__ = __str__

class VO(Seed):
    def __str__(self): return 'verb-object %s.n %s.v' %(self.noun, self.verb)
    __repr__ = __str__

def rseed(f):
    elts = (l.rstrip().split() for l in f)
    return [SV(a, b) if c == '-' else VO(c, b) for a, b, c in elts] 
         
def main(args):
    # 1. Read in the seed file
    seeds = rseed(uopen(args[1 + args.index('-i')]))
#     outs = uopen(args[1 + args.index('-o')], mode='w+')
    
    for s in seeds: 
        print s
        pprint(['%s.%s' % (l.name, l.synset.pos) for l in derivations(s.noun)])
        pprint(['%s.%s' % (l.name, l.synset.pos) for l in derivations(s.verb)])
        
    # 2. Generate extensions
    # 3. Write seed file
    
    
    
if __name__ == '__main__':
    main(sys.argv)