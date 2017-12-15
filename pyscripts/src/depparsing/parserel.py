"""Created on 5/14/2013 by @author: lucag@icsi.berkeley.edu
"""

from __future__ import print_function

import sys

from parsemet import Parser, expand
from itertools import groupby
from util import normalized
from functools import partial

def tag(pos):
    if pos[0:2] == 'NN': return 'n'
    elif pos[0] == 'V': return 'v'
    elif pos[0] == 'R': return 's'
    elif pos[0] == 'J': return 'a'
    else: raise TypeError('%s: UNK' % pos)
    
def tagrel(dep):
    """Tag a relation as Adj, Dobj, Subj, Iobj, AdvAdj, AdvVerb.
    """
    if dep.rel in ('ncsubj', 'subj'):
        return 'Subj'
    elif dep.rel == 'obj2':
        return 'Iobj' 
    elif dep.rel == 'dobj':
        return 'Dobj' 
    elif dep.rel == 'ncmod':
        if dep.pos[0] == 'R':
            if dep.head.head.pos[0] == 'V':
                return 'AdvVerb'
            elif dep.head.pos[0] == 'J':
                return 'AdvAdj'
        elif dep.pos[0:2] == 'NN' and dep.head.pos[0:2] == 'NN':
            return 'NomMod'
        elif dep.pos[0] == 'J' and dep.head.pos[0:2] == 'NN':
            return 'Adj'
        else:
            return '**UNK**'
#             raise TypeError('%s: impossible to categorize (1)' % str(dep))
    else:
        raise TypeError('%s: impossible to categorize (2)' % str(dep))
    
def process_rasp_relation(dep):
    if dep.rel in ('subj', 'ncsubj', 'obj2'):
        return unicode(dep.wordn - 1), unicode(dep.head.wordn - 1), tagrel(dep), (dep.lemma, tag(dep.pos)), (dep.head.lemma, tag(dep.head.pos)),
    elif dep.head.pos[0] == 'I':
        v = dep.head.head
        return unicode(dep.wordn - 1), unicode(v.wordn - 1), tagrel(dep), (dep.lemma, tag(dep.pos)), (v.lemma, tag(v.pos))
    else:
        return unicode(dep.wordn - 1), unicode(dep.head.wordn - 1), tagrel(dep), (dep.lemma, tag(dep.pos)), (dep.head.lemma, tag(dep.head.pos))

def rasp_keep(dep):
    if dep.rel in ('subj', 'ncsubj', 'obj2', 'ncmod'):
        if dep.pos[0:2] == 'NN':
            return dep.head.pos[0] == 'V' or dep.head.pos[0:2] == 'NN'
        if dep.pos[0] == 'J':
            return dep.head.pos[0:2] == 'NN'
    if dep.rel == 'dobj' and dep.pos[0:2] == 'NN':
        if dep.head.pos[0] == 'V':
            return True
        if dep.head.pos[0] == 'I':
            return dep.head.head and dep.head.head.pos[0] == 'V'
    return False


config = {'rasp': (process_rasp_relation, rasp_keep, None, None), }

_parser = {'en': Parser(name='rasp',
                        config=config['rasp'],
                        command=expand(['{TOOLS}/rasp3os/scripts/rasp.sh', '-m']),
                        encoding='utf-8'),
#            'es': Parser(name='freeling',
#                         config=config['freeling'],
#                         command=expand(['{TOOLS}/bin/analyzer', '--nec', '-f', '{TOOLS}/etc/dep.cfg']),
#                         encoding='utf-8'), 
           }

from itertools import izip

def parse(infile, lang):
    assert lang in ('en', 'es')
    ss, deps = _parser[lang].parse(infile)
    def key((sid, t)): 
        return sid
    by_sid = normalized(groupby(deps, key), key=key, filler=lambda sid: (sid, ()), start=1)
    return izip(ss, by_sid)


def usage():
    print('Usage: {} -l en|es ...')
    sys.exit(-1)
    

def main(args):
    from util import ureader, uwriter#, tag, untag

    if '-l' not in args:
        usage()
        
    lang = args[1 + args.index('-l')] 
    
#     do_tag = '-t' in args
#     maybe_tag = tag if do_tag else lambda x: x
    
#     valid_rels = ('Adj', 'Dobj', 'Subj', 'Iobj', 'AdvAdj', 'AdvVerb')
     
    stdin, stdout = ureader(sys.stdin), uwriter(sys.stdout) 
    uprint = partial(print, file=stdout)    
    for s, (sid, relations) in parse(stdin, lang):
        uprint(u'[{}] {}'.format(sid, s))
        for sid, (_, _, r, d, h) in relations:
            if r != '**UNK**':
#                 uprint(u'[{0}] {1} {2[0]}.{2[1]} {3[0]}.{3[1]}'.format(sid, r, d, h))
                if r == 'Adj':
                    uprint(u'[{0}] {1} {2[0]} {3[0]}'.format(sid, r, h, d))
                else:
                    uprint(u'[{0}] {1} {2[0]} {3[0]}'.format(sid, r, d, h))
        uprint()
        

if __name__ == '__main__':
    main(sys.argv)
    