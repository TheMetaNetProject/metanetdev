'''
Created on Apr 13, 2012

@author: lucag
'''

import codecs, sys

from os.path import join, basename, dirname, sep
from itertools import groupby, ifilter
from util import good

def splitlines(source_file, target_dir, chunk_size):
    with codecs.open(source_file, 'r', 'utf-8') as source:
        joinlines(ifilter(good, source), basename(source_file), target_dir, chunk_size)


def joinlines(lines, name, target_dir, chunk_size):
    groups = groupby(enumerate(lines), lambda (c, _): int(c // chunk_size))
    for c, group in ((c, list(pairs)) for c, pairs in groups):
        i = 1 + c * chunk_size
        target = join(target_dir, name + '#%.10d-%.10d.ss' % (i, i + len(group)))
        if True:
            with codecs.open(target, 'w', 'utf-8') as d:
                print 'writing', target
                d.writelines([l for _, l in group])
        else:
            print target


def lines(*filenames):
    for filename in filenames:
        with codecs.open(filename, 'r', 'utf-8') as f:
            for line in f:
                yield line


def main(args):
    from glob import iglob
    
    if len(args) != 4:
        print 'Usage: %s <source> <dest-dir> <chunk-size>' % args[0]
        return -1

    source = args[1]
    name = dirname(source).split(sep)[-1]
    chunk_size = int(args[3]) 
    joinlines(ifilter(good, lines(*iglob(source))), name, args[2], chunk_size)
#    splitlines(args[1], args[2], int(args[3]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))