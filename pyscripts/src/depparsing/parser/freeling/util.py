# -*- coding: UTF-8 -*-

"""Created on Oct 3, 2014 by @author: lucag@icsi.berkeley.edu
"""

from __future__ import print_function

from pprint import pprint
from string import split
from textwrap import dedent
import re
import sys

from depparsing.util import update, Struct, ureader, uwriter, blocks, lines
fields_re = re.compile(
    r'^(?P<sent_id>\d+):(?P<indent> *)[\w-]+/(?P<rel>[\w-]+)/\((?P<word>[^ ]+) (?P<lemma>[^ ]+) (?P<pos>[^ ]+) (?P<beg>\d+) (?P<end>\d+) ?[^ ]\) ?(?P<bracket>\[)?',
    re.UNICODE)
depth_re = re.compile(r'^(?P<sent_id>\d+):(?P<indent> *)(?P<bracket>\])', re.UNICODE)


class Node(Struct):
    def __init__(self, match):
        update(self, match.groupdict())

    def __repr__(self):
        return '%s %s' % (self.__class__.__name__, self.word if 'word' in self else ']')
    
    def depth(self):
        return len(self.indent) / 2

class FieldNode(Node): pass

class DepthNode(Node): pass

class RootNode(Node):
    def __init__(self):
        update(self, n=0, beg=-1, indent='', bracket='[', word='<root>')

def to_nodelist(block):
    def node(line=None):
        if line == None:
            return RootNode()
        else:
            fs = fields_re.match(line)
            d = depth_re.match(line)
        return FieldNode(fs) if fs else DepthNode(d) 

    nodes = map(node, block)
    fnodes = filter(lambda n: isinstance(n, FieldNode), nodes)
    snodes = sorted(fnodes, key=lambda n: int(n.beg))
    for n, node_ in enumerate(snodes, start=1):
        update(node_, n=n)
    
    def traverse(pairs, parent, children, d=0):
        if len(children) > 0:
            node, rest = children[0], children[1:]
#             print('d:', d, node, node.depth(), 'p:', parent, node.bracket)
            if node.bracket == '[':
                assert d == node.depth()
                node.parent = parent
                pairs.append((node, parent))
                traverse(pairs, node, rest, d + 1)
            elif node.bracket == ']':
                assert d - 1 == node.depth()
                p = parent.parent
                node.parent = p
                traverse(pairs, p, rest, d - 1)
            else:
                assert d == node.depth()
                pairs.append((node, parent))
                # node.bracket == ''
                node.parent = parent
                traverse(pairs, parent, rest, d)
  
    pairs = []
    traverse(pairs, node(), nodes)
    for d, h in pairs: assert d.parent == h
    return snodes
    
def to_conllx(block):
    return [(d.n, d.word, d.lemma, d.pos[0].lower(), d.pos, '_', d.parent.n, d.rel, '_', '_')
             for d in to_nodelist(block)]

def test_0():
    u"""
    >>> from pprint import pprint
    >>> pprint(test_0())
    [(1, u'El', u'el', u'd', u'DA0MS0', '_', 2, u'espec', '_', '_'),
     (2, u'dinero', u'dinero', u'n', u'NCMS000', '_', 3, u'subj', '_', '_'),
     (3, u'corrompe', u'corromper', u'v', u'VMIP3S0', '_', 0, u'top', '_', '_'),
     (4, u',', u',', u'f', u'Fc', '_', 3, u'term', '_', '_'),
     (5, u'no', u'no', u'r', u'RN', '_', 6, u'espec', '_', '_'),
     (6, u'tiene', u'tener', u'v', u'VMIP3S0', '_', 3, u'modnomatch', '_', '_'),
     (7, u'salida', u'salida', u'n', u'NCFS000', '_', 6, u'dobj', '_', '_'),
     (8, u'.', u'.', u'f', u'Fp', '_', 6, u'term', '_', '_')]
     """
    block = split(dedent(u"""\
        3:grup-verb/top/(corrompe corromper VMIP3S0 93 101 -) [
        3:  sn/subj/(dinero dinero NCMS000 86 92 -) [
        3:    espec-ms/espec/(El el DA0MS0 83 85 -)
        3:  ]
        3:  Fc/term/(, , Fc 101 102 -)
        3:  grup-verb/modnomatch/(tiene tener VMIP3S0 106 111 -) [
        3:    neg/espec/(no no RN 103 105 -)
        3:    sn/dobj/(salida salida NCFS000 112 118 -)
        3:    F-term/term/(. . Fp 118 119 -)
        3:  ]
        3:]"""), sep=u'\n')
    return to_conllx(block)

def test_1():
    u"""
    >>> print(u'\\n'.join(u'    '.join(unicode(f) for f in l) for l in test_1()))
    1    Además    además    r    RG    _    4    ador    _    _
    2    ,    ,    f    Fc    _    1    term    _    _
    3    Viñals    viñals    n    NC00000    _    4    subj    _    _
    4    consideró    considerar    v    VMIS3S0    _    0    top    _    _
    5    que    que    c    CS    _    4    modnomatch    _    _
    6    ,    ,    f    Fc    _    4    term    _    _
    7    en    en    s    SPS00    _    4    cc    _    _
    8    términos    término    n    NCMP000    _    7    obj-prep    _    _
    9    generales    general    a    AQ0CP0    _    8    adj-mod    _    _
    10    "    "    f    Fe    _    4    modnomatch    _    _
    11    los    el    d    DA0MP0    _    12    espec    _    _
    12    mercados    mercado    n    NCMP000    _    16    subj    _    _
    13    emergentes    emergente    a    AQ0CP0    _    12    adj-mod    _    _
    14    se    se    p    P00CN000    _    16    es    _    _
    15    han    haber    v    VAIP3P0    _    16    aux    _    _
    16    mantenido    mantener    v    VMP00SM    _    4    modnomatch    _    _
    17    bastante    bastante    r    RG    _    18    espec    _    _
    18    resistentes    resistente    a    AQ0CP0    _    16    pred    _    _
    19    ,    ,    f    Fc    _    16    term    _    _
    20    aun    aun    r    RG    _    16    espec    _    _
    21    con    con    s    SPS00    _    16    cc    _    _
    22    incertidumbre    incertidumbre    n    NCFS000    _    21    obj-prep    _    _
    23    en_la_zona_de    en_la_zona_de    s    SPS00    _    16    sp-obj    _    _
    24    el    el    d    DA0MS0    _    25    espec    _    _
    25    euro    euro    n    NCMS000    _    23    obj-prep    _    _
    26    "    "    f    Fe    _    4    modnomatch    _    _
    27    ,    ,    f    Fc    _    4    term    _    _
    28    y    y    c    CC    _    4    modnomatch    _    _
    29    que    que    c    CS    _    4    modnomatch    _    _
    30    "    "    f    Fe    _    4    modnomatch    _    _
    31    el    el    d    DA0MS0    _    4    modnomatch    _    _
    32    capital    capital    n    NCFS000    _    35    subj    _    _
    33    ha    haber    v    VAIP3S0    _    35    aux    _    _
    34    continuado    continuar    v    VMP00SM    _    35    dverb    _    _
    35    fluyendo    fluir    v    VMG0000    _    4    modnomatch    _    _
    36    "    "    f    Fe    _    4    modnomatch    _    _
    37    hacia    hacia    s    SPS00    _    4    cc    _    _
    38    éstos    este    p    PD0MP000    _    37    obj-prep    _    _
    39    .    .    f    Fp    _    37    term    _    _
    """
    block = split(dedent(u"""\
        6:grup-verb/top/(consideró considerar VMIS3S0 224 233 -) [
        6:  sadv/ador/(Además además RG 209 215 -) [
        6:    Fc/term/(, , Fc 215 216 -)
        6:  ]
        6:  sn/subj/(Viñals viñals NC00000 217 223 -)
        6:  conj-subord/modnomatch/(que que CS 234 237 -)
        6:  Fc/term/(, , Fc 237 238 -)
        6:  grup-sp/cc/(en en SPS00 239 241 -) [
        6:    sn/obj-prep/(términos término NCMP000 242 250 -) [
        6:      s-a-mp/adj-mod/(generales general AQ0CP0 251 260 -)
        6:    ]
        6:  ]
        6:  F-no-c/modnomatch/(" " Fe 261 262 -)
        6:  grup-verb/modnomatch/(mantenido mantener VMP00SM 293 302 -) [
        6:    morfema-verbal/es/(se se P00CN000 286 288 -)
        6:    vaux/aux/(han haber VAIP3P0 289 292 -)
        6:    sn/subj/(mercados mercado NCMP000 266 274 -) [
        6:      espec-mp/espec/(los el DA0MP0 262 265 -)
        6:      s-a-mp/adj-mod/(emergentes emergente AQ0CP0 275 285 -)
        6:    ]
        6:    s-adj/pred/(resistentes resistente AQ0CP0 312 323 -) [
        6:      sadv/espec/(bastante bastante RG 303 311 -)
        6:    ]
        6:    Fc/term/(, , Fc 323 324 -)
        6:    sadv/espec/(aun aun RG 325 328 -)
        6:    grup-sp/cc/(con con SPS00 329 332 -) [
        6:      sn/obj-prep/(incertidumbre incertidumbre NCFS000 333 346 -)
        6:    ]
        6:    grup-sp/sp-obj/(en_la_zona_de en_la_zona_de SPS00 347 359 -) [
        6:      sn/obj-prep/(euro euro NCMS000 362 366 -) [
        6:        espec-ms/espec/(el el DA0MS0 360 361 -)
        6:      ]
        6:    ]
        6:  ]
        6:  F-no-c/modnomatch/(" " Fe 366 367 -)
        6:  Fc/term/(, , Fc 368 369 -)
        6:  coord/modnomatch/(y y CC 370 371 -)
        6:  conj-subord/modnomatch/(que que CS 372 375 -)
        6:  F-no-c/modnomatch/(" " Fe 376 377 -)
        6:  espec-ms/modnomatch/(el el DA0MS0 377 379 -)
        6:  grup-verb/modnomatch/(fluyendo fluir VMG0000 402 410 -) [
        6:    vaux/aux/(ha haber VAIP3S0 388 390 -)
        6:    VMP00SM/dverb/(continuado continuar VMP00SM 391 401 -)
        6:    sn/subj/(capital capital NCFS000 380 387 -)
        6:  ]
        6:  F-no-c/modnomatch/(" " Fe 410 411 -)
        6:  grup-sp/cc/(hacia hacia SPS00 412 417 -) [
        6:    sn/obj-prep/(éstos este PD0MP000 418 423 -)
        6:    F-term/term/(. . Fp 423 424 -)
        6:  ]
        6:]"""), sep=u'\n')
    return to_conllx(block)   

if __name__ == '__main__':
    if '-t' in sys.argv:
        import doctest
        doctest.testmod()
    else:
        uin, uout = ureader(sys.stdin), uwriter(sys.stdout)
        for block in blocks(lambda l: len(l) > 0, lines(uin)):
            print(u'\n'.join(u'\t'.join(unicode(f) for f in line) for line in to_conllx(block)), u'\n', file=uout)
