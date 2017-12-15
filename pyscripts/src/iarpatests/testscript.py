#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re, pprint
from mnformats import mnjson
from depparsing.dep2json import parse
from depparsing.parsemet import sanitized


ntdotre = re.compile(ur'[.]([^0-9])', flags=re.U)
ntmarkre = re.compile(ur'[!?](.)', flags=re.U)
endre = re.compile(ur'([.!?])+$', flags=re.U)
        
print sys.argv[1]
jdata = mnjson.loadfile(sys.argv[1])
in_sentences = jdata['sentences']
# out_jdata = parse(jdata['lang'],
#                   [ntmarkre.sub(r',\1,',
#                                 ntdotre.sub(r',\1',
#                                             endre.sub(r'\1',sanitized(s['text'])))) for s in in_sentences])
out_jdata = parse(jdata['lang'], [s['ctext'] for s in in_sentences])
pprint.pprint(out_jdata)
