'''
Created on Apr 27, 2012

@author: lucag
'''

import sys, codecs
import xml.parsers.expat

from xml.dom.pulldom import START_ELEMENT, END_ELEMENT, parse
from xml.sax.saxutils import unescape
from pprint import pprint
from itertools import chain, izip, ifilter


def relindex(stream):
    """Generate a map rel --> *sentence from stream.
    """
    def traverse(sentence_node):
        for c in sentence_node.childNodes:
            yield c
            for cc in traverse(c):
                yield cc
    
    # Elements in the xml tree 
    S, W, C, GAP, GR = 's', 'w', 'c', 'gap', 'gr' 
    MB = 2** 20
    doc = parse(stream, bufsize=10 * MB)
    for event, sentence_node in doc:
        if event == START_ELEMENT and sentence_node.localName == S:
            doc.expandNode(sentence_node)
            # Gather the w and p elements (words and punctuation).
            relations = []
            words = []
            for node in ifilter(lambda n: n.localName in (W, C, GAP, GR), traverse(sentence_node)):
                name = node.localName
                attr = node.getAttribute
                if name in (W, C, GAP):
                    lem, pos, n = (attr(a) for a in ('lem', 'pos', 'n'))
                    for nn in n.split():
                        words.append((node, lem, pos, int(nn) - 1))
                if name == GR and attr('type') in ('ncsubj', 'dobj'):
                    # We should have seen all the w and c nodes when we get here...
                    try:
                        rels = [words[int(attr(r)) - 1] for r in ('head', 'dep')]
                    except IndexError:
                        # Debug
                        pprint(words)
                        print [int(attr(r)) - 1 for r in ('head', 'dep')]
                        raise
                    relpairs = tuple((lem.lower(), n) for node, lem, pos, n in rels if pos in ('SUBST', 'VERB'))
                    if len(relpairs) == 2:
                        relations.append(relpairs)
            yield tuple(node.data for node in chain.from_iterable(node.childNodes for node, _, _, _ in words)), relations


# Elements in the xml tree 
S, W, C, GAP, GR, SKIP = 's', 'w', 'c', 'gap', 'gr', '**skip**' 

def update(obj, **kw):
    obj.__dict__.update(kw)
    
    
class Handler(object):
    """Expat handler: closure bug workaround.
    """
    def __init__(self):
        update(self, text=[], words=[], relations=[], results=[], status=None)
        
    def start_element(self, name, attr):
        if name == S:
            update(self, text=[], words=[], relations=[], s_n=attr['n'], status=S)
        if self.status == S:
            if name in (W, C, GAP) and attr:
                try:
                    lem, pos, n = (attr.get(a) for a in ('lem', 'pos', 'n'))
                    if not n:
                        print >> sys.stderr, "Skipping element %s, %s" % (name, attr)
                        if name == GAP:
                            self.status = SKIP
                            print >> sys.stderr, "Skipping sentence %s" % self.s_n
                    else:
                        for nn in n.split():
                            self.words.append((lem, pos, int(nn) - 1))
                except KeyError:
                    pprint(self.words)
                    pprint(self.text)
                    pprint(name)
                    pprint(attr)
                    print 's.n', self.s_n
                    raise
                except AttributeError:
                    pprint(self.words)
                    pprint(self.text)
                    pprint(name)
                    pprint(attr)
                    print 's.n', self.s_n
                    raise
            elif self.status != SKIP and name == GR:
                    reltype = attr['type']
                    if reltype in ('ncsubj', 'dobj'):
                        try:
                            rels = [self.words[int(attr[r]) - 1] for r in ('head', 'dep')]
                            relpairs = tuple((lem.lower(), n) for lem, pos, n in rels if pos in ('SUBST', 'VERB'))
                            if len(relpairs) == 2:
                                self.relations.append((reltype,) + relpairs)
                        except IndexError:
                            # Debug
                            pprint([e for e in enumerate(self.words)])
                            pprint([e for e in enumerate(self.text)])
                            print [int(attr[r]) - 1 for r in ('head', 'dep')]
                            print '>> skipping sentence', self.s_n
         
    def end_element(self, name):
        if name == S:
            self.status = None
            self.results.append((tuple(self.text), self.relations))
    
    def char_data(self, data):
        if data != '\n':
            self.text.append(data) 
        
M = 2 ** 20
def relindex2(stream, words=[]):
    """Generate a map rel --> *sentence from stream.
    """
    parser = xml.parsers.expat.ParserCreate()
    parser.buffer_text = True
    parser.buffer_size = 10 * M
    
    handler = Handler()    
    parser.StartElementHandler = handler.start_element
    parser.EndElementHandler = handler.end_element
    parser.CharacterDataHandler = handler.char_data

    parser.ParseFile(stream)
    return handler.results


def main(args):
    from glob import iglob
    
    infname, outfname = args
    with codecs.open(outfname, 'w', encoding='utf-8') as outstream:
        write = outstream.write
        for filename in iglob(infname):
            print 'processing %s' % filename
            with codecs.open(filename) as instream:
                for words, relations in relindex2(instream):
                    for t, v, s in relations:
                        try:
                            write('%s|%s %s|%s\n' % (t, '%s:%d' % v, '%s:%d' % s, ''.join(words))) 
                        except TypeError:
                            pprint((t, v, s))
                            raise


def test(fname):
    # 3 handler functions
    def start_element(name, attrs):
        print 'Start element:', name, attrs
    
    def end_element(name):
        print 'End element:', name
    
    def char_data(data):
        print 'Character data:', repr(data)
    
    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data
  
    with codecs.open(fname) as f:
        p.ParseFile(f)
  
        
if __name__ == '__main__':
#    test(sys.argv[1])
    main(sys.argv[1:])