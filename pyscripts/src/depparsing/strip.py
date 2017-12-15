# coding=utf-8
"""Created on Dec 4, 2012 by @author: lucag@icsi.berkeley.edu
"""

import sys, string
#from itertools import ifilter
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from util import update
#from pprint import pprint 

def good(line):
    return len(line) and line[0] in string.ascii_letters and line.rstrip()[-1] == u'.'

#tt = string.maketrans(u"’", u"'")

class HTMLStripper(HTMLParser):
    def __init__(self, keep):
        HTMLParser.__init__(self)
        update(self, keep=keep, status=None, data=[])
    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.keep: 
            self.status = tag
            self.data.append('')
    def handle_endtag(self, tag):
        if tag == self.status:
            self.status = None
    def handle_data(self, data):
        if self.status:
            self.data[-1] += data
    def handle_entityref(self, name):
        if self.status:
            try:
                self.data[-1] += unichr(name2codepoint[name])
            except KeyError:
                # Ignore it
                pass
                    
def strip(text, keep='p'):
    s = HTMLStripper(keep)
    s.feed(text)
    return cleaned(s.data)

import re
word = re.compile(r'\w+', re.UNICODE)
nonword = re.compile(r'\W\W\W+', re.UNICODE)

def cleaned(it):
    cleaned = []
#    for line in filter(good, stdin):
    for line in it:
        line = line.replace(u"’", u"'")
        line = line.replace(u'“', u'"')
        line = line.replace(u'”', u'"')

        # Graphical characters
        line = line.replace(u'\xb4', u"'")
        line = line.replace(u'\xb7', u'-')

        # Em and en dashes
        line = line.replace(u'\u2011', u"-")
        line = line.replace(u'\u2013', u'-')
        line = line.replace(u'\u2014', u'-')
        
        line = line.replace(u'\u2018', u"'")
        line = line.replace(u'\u2022', u"-")
        line = line.replace(u'\u2212', u'-')
        line = line.replace(u'\u2032', u"'")
        line = line.replace(u'\u2026', u'...')
        
        for l in re.split('\n+', line):
            if len(l) > 20: 
                w = float(len(word.findall(l)))
                n = float(len(nonword.findall(l)))
                t = max(1.0, float(len(l.split())))
                if w / t > .5 and w > 10 and n == 0:
                    cleaned.append(l.strip())
            
    return cleaned


def usage(args):
    from os.path import basename
    print '{} -t tag [-e encoding]'.format(basename(args[0]))
    sys.exit(-1)

    
def main(args):
    import codecs
    from util import ureader, uwriter, uopen
    
    def handler(x):
        v = x.object[x.start:x.end]
        print >> stderr, repr(v), v
        return (u'', x.end)
    
    codecs.register_error('clear', handler)
    
    if '-t' not in args:
        usage(args)
        
    tag = map(string.lower, args[1 + args.index('-t')].split(','))
    enc = args[1 + args.index('-e')] if '-e' in args else 'utf8' 
    stdin = ureader(sys.stdin) if '-i' not in args else uopen(args[1 + args.index('-i')])
#     stdout = codecs.getwriter(enc)(sys.stdout if '-o' not in args else open(args[1 + args.index('-o')], 'wb'), errors='clear')
    stdout = codecs.getwriter(enc)(sys.stdout if '-o' not in args else open(args[1 + args.index('-o')], 'wb'))
    stderr = uwriter(sys.stderr)
    for l in strip(stdin.read(), keep=tag):
        try:
            print >> stdout, l
        except UnicodeDecodeError:
            print 'problem with', l
        
if __name__ == '__main__':
    main(sys.argv)