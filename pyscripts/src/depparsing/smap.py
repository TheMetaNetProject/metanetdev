'''Created on Oct 3, 2012
@author: lucag
'''

import sys
from itertools import izip
from util import uopen 

if __name__ == '__main__':
    src, tgt = map(uopen, sys.argv[1:3])
    with src, tgt:
        giza_id = 0
        for i, (s, t) in enumerate(izip(src, tgt), start=1):
            if s.strip() and t.strip():
                giza_id += 1
                print giza_id, i