from __future__ import print_function

"""A replacement for ~katia/JuneSystem/June.sh
@author lucag@icsi.berkeley.edu
"""

from util import uopen, Environment

expand = Environment(BASE='/n/shokuji/dc/katia',
                     BNC='/u/metanet/corpolexica/EN/bnc-relations',
                     ADJ='{BNC}/AdverbialModifierForAdjRels.txt-uniqed-sorted',
                     DOBJ='{BNC}/DirectObjRels.txt-uniqed-sorted',
                     SUBJ='{BNC}/SubjectRels.txt-uniqed-sorted',
                     IOBJ='{BNC}/IndirectObjRels.txt-underscore-uniqed-sorted')


_SCOREF = expand('{BASE}/MRC_Conc_All')
score = dict(l.rstrip().split() for l in uopen(_SCOREF))

def concreteness(target):
    return score[target]

def main(relation, target, source):
    pass