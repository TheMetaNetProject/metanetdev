"""Created on Mar 27, 2013 by @author: lucag@icsi.berkeley.edu
"""
from __future__ import print_function

import sys, re
from ..util import uwriter, uopen, Lemmatizer, freelingsh, update
from string import split
# from pprint import pprint

def usage(args):
    from os.path import basename
    print('Usage: {} -l en|es|ru [-i <input>] [-o <output>]'.format(basename(args[0])))
    sys.exit(-1)
    
class Splitter(object):
    def __init__(self, sep='\w+', trans=None):
        update(self, sep=re.compile(sep), trans=trans)
    def split(self, s):
        return self.sep.split(self.trans(s) if self.trans else s)

   
def main(args):
    if '-l' not in args: usage(args)
        
    stdin, stdout, stderr = sys.stdin, uwriter(sys.stdout), uwriter(sys.stderr)
    lang = args[args.index('-l') + 1]
    lemmatizer = Lemmatizer(uopen(freelingsh(lang, 'dicc.src')))
    infile = open(args[args.index('-i') + 1], mode='rb') if '-i' in args else stdin
    outfile = uopen(args[args.index('-o') + 1], 'wb') if '-o' in args else stdout
    splitter = Splitter('\t')
    tabjoin = u'\t'.join
    # Corrections to POS set
    corr = dict(NNP='NN')
    for l in (l.decode('utf8') for l in infile):
        try:
            text, tags, _, _ = splitter.split(l)
        except ValueError:
            print(u'>>', repr(l), file=stderr)
            continue
        if text and tags:
            for w, t in zip(split(text), split(tags)): 
                lemma, _ = lemmatizer.get(w.lower(), corr.get(t, t))[0]
                print(tabjoin((w, t, lemma)), file=outfile)
            else:
                print(u'<eos>', file=outfile)
        
        
if __name__ == '__main__':
    main(sys.argv)
