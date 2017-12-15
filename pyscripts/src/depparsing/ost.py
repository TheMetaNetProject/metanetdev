from __future__ import print_function

"""Created on Apr 13, 2012, @author: lucag
"""

import codecs, sys

from os.path import join, dirname, sep, exists
from os import makedirs
from itertools import groupby
from util import uopen

def scatter(lines, name, target_dir, files_per_dir, chunk_size, ext='ss'):
    lines_per_dir = files_per_dir * chunk_size
    line_groups = groupby(enumerate(lines), lambda (c, _): int(c / lines_per_dir))
    for d, enum_lines in line_groups: 
        dirname = join(target_dir, '%.2x' % d)
        if not exists(dirname):
            makedirs(dirname)
        file_groups = groupby(enum_lines, lambda (c, _): int(c / chunk_size))
        for f, enum_lines_in_file in file_groups:
            target = join(dirname, '%.4x.%s' % (f, ext))
            if True:
                with uopen(target, 'w') as outs:
                    print('writing', target)
                    outs.writelines(l.decode('utf8') for _, l in enum_lines_in_file)
            else:
                print(target)

def cleaned(word):
    w = word.replace('\xc2\x85', '?')
    w = word.replace('\xe2\x80\xa8', '?')
#             if w != word:
#                 print('replaced!', file=sys.stderr)
    return w

def main(args):
    import gzip, re
    from pprint import pformat
    from itertools import ifilter
    from malt.util import takewhile
    
    if len(args) not in (5, 6):
        print('Usage: %s -s|-m <source> <dest-dir> <max-files-per-dir> <chunk-size>' % args[0])
        return -1

    # is it a Malt Parser output?
    malt = '-m' in args
    
    source, target_dir = args[2:4]
    name = dirname(source).split(sep)[-1]
    files_per_dir, chunk_size = map(int, args[4:])
    
    if malt:
        tag = re.compile(r'<[^>]+>', re.UNICODE)
        def split(it):
            while True:
                goodones = ifilter(lambda (_, l): not tag.findall(' '.join(l)), it)
                try:
                    b = [line for n, line in takewhile(lambda (_, l): l[1] != 'SENT', goodones)]
                except IndexError:
                    print ('Problem in', n, pformat(line)) 
                    raise
                if len(b): 
                    yield cleaned('\n'.join('\t'.join(w) for w in b)) + '\n'
                else:
                    return
            
        def lines(*filenames):
            for filename in filenames:
#                 with codecs.getreader('utf-8')(gzip.open(filename, 'rb')) as f:
                source = open(filename, 'rb') if filename != '-' else sys.stdin
#                 with codecs.getreader('utf-8')(source) as f:
                with source as f:
                    for block in split(enumerate((l.rstrip().split() for l in f), 1)):
#                         pprint(block)
                        yield block
    else:
        def lines(*filenames):
            for filename in filenames:
                with codecs.getreader('utf-8')(gzip.open(filename, 'rb')) as f:
                    for line in f:
                        yield line
             
    join = '\n'.join
    scatter(lines(source), name, target_dir, files_per_dir, chunk_size, 'dep' if malt else 'ss')
        
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
