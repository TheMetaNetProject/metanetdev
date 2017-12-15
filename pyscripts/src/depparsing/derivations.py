import sys
from util import derivations

def usage(args):
    print 'Usage: {0[0]} <word>'.format(args)
    sys.exit(-1)
    
if len(sys.argv) != 2:
    usage(sys.argv)
    
for l in derivations(sys.argv[1]):
    print '{}.{}'.format(l.name, l.synset.pos)