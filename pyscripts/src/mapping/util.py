# -*- coding: UTF-8 -*-

from __future__ import print_function

import sys
import os
from depparsing.util import uopen, uwriter
from assign import env
import subprocess
import cStringIO

def relations(rel, tuples, reverse=False):
    for t in tuples: 
        if len(t) == 3:
            cnt, noun, verb = t
            if not reverse:
                yield cnt, rel, noun, verb  
            else:
                yield cnt, rel, verb, noun 
        elif len(t) == 4: # RU
            cnt, verb, _, noun = t
            yield cnt, rel, noun, verb 
        else:
            print(u'ignoring', t, file=uwriter(sys.stderr))
    
CREATE_DB = """\
    CREATE TABLE IF NOT EXISTS nvrel (n int, reltype string, noun, verb);
    CREATE INDEX  IF NOT EXISTS nvidx on nvrel (noun, verb);
    CREATE INDEX  IF NOT EXISTS vridx on nvrel (verb, reltype);
    """.splitlines()

IMPORT = r"""\
    .separator \t
    .import %s nvrel
    """
     
if __name__ == '__main__':
    # This describes the command line:
    #  1. language (one in EN, ES, RU);
    #  2. relation type, as specified by the parser; 
    #  3. input file; 
    #  4. output index file (SQLite3 .db file).  
    lang, rel, inn, outn = sys.argv[1:5]
    
    tempn = os.tempnam()
    with uopen(inn) as inf, uopen(tempn, 'w+') as outf:
        for r in relations(rel, (l.rstrip().split() for l in inf)):
            print(u'\t'.join(r), file=outf)
    
    subprocess.call('sqlite3 %s %s' % (outn, ' '.join(CREATE_DB)))
    subprocess.Popen(['sqlite3', outn], stdin=cStringIO(IMPORT % tempn))
    