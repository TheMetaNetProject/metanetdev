'''Created on 02 Oct 2014 @author: lucag
'''
from __future__ import print_function

from depparsing.util import ureader, uwriter, blocks, lines
from depparsing.parser.malt.util import as_conllx
from pprint import pprint

import sys
from depparsing.columnize import uopen

def main(args):
    stdin, stdout = ureader(sys.stdin), uwriter(sys.stdout)
    sin = uopen(args[1]) if len(args) == 2 else stdin
    records = (l.split() for l in lines(sin))
    for b in blocks(lambda l: len(l) > 0, records):
        assert len(b) > 0, 'len(b) is %d' % len(b)
        for i, rec in enumerate(map(as_conllx, b), start=1):
            print(u'\t'.join((unicode(i),) + rec + ('_',) * 5), file=stdout)
        print(file=stdout)
            
if __name__ == '__main__':
    main(sys.argv)