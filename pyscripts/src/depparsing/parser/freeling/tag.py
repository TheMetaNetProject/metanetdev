"""Created on Dec 19, 2012 by @author: lucag@icsi.berkeley.edu

Convert freeling tagged files to our format: 
The_DET lecturer_NOUN gave_VERB a_DET good_ADJ lecture_NOUN . . . 
"""

import sys
from depparsing.util import ureader, uwriter

stdin, stdout, stderr = ureader(sys.stdin), uwriter(sys.stdout), uwriter(sys.stderr)

for l in stdin:
    if len(l) > 1:
        try:
            word, lemma, pos, prob = line = l[:-1].split()[0:4]
            print >> stdout, u'{}_{}'.format(word, pos), 
        except ValueError:
            print >> stderr, l
    else:
        print >> stdout 
        
    