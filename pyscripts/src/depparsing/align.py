'''
Created on Oct 4, 2012

@author: lucag
'''

import re, sys
from itertools import islice, izip, imap
from util import uopen, grouped
from string import split

def converted(sent, reverse=False):
    pair_re = re.compile(r'(\S+)\s\(\{([^}]*)\}\)')
    for s, (_, tt) in enumerate(islice(((w, tt.split()) for w, tt in pair_re.findall(sent)), 1, None)):
#        print s, w, tt
        if tt:
            for t in (int(t) - 1 for t in tt):
                assert t > 0
                yield s, t if not reverse else t, s

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >> sys.stderr, 'Usage: %s -{d,r} <missing sentence map> <A3 file>'
        sys.exit(-1)
            
    sent_map, a3_input = map(uopen, sys.argv[2:4])
    reverse = sys.argv[1] == '-r'
    
    with sent_map, a3_input:
        spacejoin = ' '.join
        sentence_id = 1
    #    for hdr, tgt, src in islice(grouped(a3_input, 3), 10):
        for (s_id, o_id), (hdr, tgt, src) in izip(imap(split, sent_map), grouped(3, a3_input)):
    #        print tgt.split()
            e_id = hdr.split()[3][1:-1]
            assert s_id == e_id, 's_id %, effective %s' % (s_id, e_id)
            fill = int(o_id) - sentence_id
            for i in range(fill):
                print 
            sentence_id += fill + 1
            print spacejoin('{0[0]}-{0[1]}'.format(p) for p in converted(src, reverse))