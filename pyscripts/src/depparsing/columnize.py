#/home/lucag/local/bin/python

import codecs, re
from functools import partial

uopen = partial(codecs.open, encoding='utf-8')

def make_split():
    def split(line):
        return re.findall(boundaries, line)
    boundaries = re.compile('\w+|\S', re.UNICODE)
    return split
    
def main(args):
    split = make_split()
    with uopen(args[1]) as lines, uopen(args[2], mode='wb') as out:
        for line in lines:
            out.write('\n'.join(split(line)) + '\n')
            
            
if __name__ == '__main__':
    import sys
    
    main(sys.argv)