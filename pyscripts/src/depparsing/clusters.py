"""Created on May 3, 2013 by @author: lucag@icsi.berkeley.edu
"""

from __future__ import print_function

from findmet import cluster, read_clusters
from util import uopen, derivations

INDENT = ' ' * 2

def out(cluster, pos):
    def tag(word, pos):
        return '%s.%s' % (word, pos)
    
    print('cluster type', pos)
    for name, words in cluster.iteritems():
        print(INDENT, 'cluster', name)
        for w in sorted(words):
            print(INDENT * 2, tag(w, pos))
            for l in (d for d in sorted(derivations(w), key=lambda l: l.name)):
                print(INDENT * 3, '(d)', tag(l.name, l.synset.pos))
    
def main(args):
    lang = args[1 + args.index('-l')]
    nc, vc = [read_clusters(uopen(fname)) for fname in cluster[lang]]
    out(nc, 'n')
    out(vc, 'v')
    

if __name__ == '__main__':
    import sys
    main(sys.argv)