# -*- encoding: UTF-8 -*-

from __future__ import print_function

import sys
from subdims_matcher import subdim_match
from os.path import basename


def usage(args):
    print('Usage: %s en|es|ru <source> <target> <source-dimension>' % basename(args[0]))
    sys.exit(-1)
    
    
def main(args):
    if len(args) != 5: 
        usage(args)
    
    _lang = dict(en='english', es='spanish', ru='russian')
    
    lang, source, target, dim = args[1:5]
    _, dim, sdim = subdim_match(_lang[lang], source, target, dim)
    print('Dimension: %s.%s' % (dim.upper(), sdim.capitalize()))
    
    
if __name__ == '__main__':
    main(sys.argv)