"""Created on Jan 25, 2013 by @author: lucag@icsi.berkeley.edu
"""

import sys
from depparsing.util import ureader, uwriter, uopen, Lemmatizer, freelingsh

def usage(args):
    from os.path import basename
    print 'Usage: {} -l en|es [-i <input>] [-o <output>]'.format(basename(args[0]))
    sys.exit(-1)
    
def main(args):
    if '-l' not in args: usage(args)
        
    stdin, stdout, stderr = ureader(sys.stdin), uwriter(sys.stdout), uwriter(sys.stderr)
    lang = args[args.index('-l') + 1]
    lemmatizer = Lemmatizer(uopen(freelingsh(lang, 'dicc.src')))
    infile = uopen(args[args.index('-i') + 1]) if '-i' in args else stdin
    outfile = uopen(args[args.index('-o') + 1], 'wb') if '-o' in args else stdout
    
    def spair(s, c='_'):
        r = s.rfind(c)
        return (s[:r], s[r+1:])
    
    for pp in (l[:-1].split() for l in infile):
        for w, t in (spair(p) for p in pp): 
            try:
                lemma, _ = lemmatizer.get(w.lower())[0]
                print >> outfile, u'{}_{}'.format(lemma, t),
            except:
                print >> stderr, 'problems with', w 
                print >> outfile, u'{}_{}'.format(w, t),
        print >> outfile
        
if __name__ == '__main__':
    main(sys.argv)
