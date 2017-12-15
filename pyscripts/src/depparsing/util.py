"""
Created on Jun 29, 2012
@author: lucag
"""

from __future__ import print_function

import xml.parsers.expat, codecs, sys
from itertools import imap, tee, izip_longest, ifilter
from itertools import takewhile as itakewhile, dropwhile as idropwhile, chain
from itertools import izip
from functools import partial
from pprint import pformat, pprint
import json

K = 2 ** 10
M = K ** 2
uwriter, ureader = codecs.getwriter('utf-8'), codecs.getreader('utf-8')
uopen = partial(codecs.open, encoding='utf-8', buffering=32*M)

class BasicHandler(object):
    def start_element(self, name): pass
    def end_element(self, name): pass
    def char_data(self, data): pass

def count(iterable, elt):
    return sum(imap(lambda x: 1 if x == elt else 0, iterable))

def good(line):
    "A good line ends in a period, is long enough, and starts with an uppercase letter."
    try:
        stripped = line.strip()
        return (len(stripped) > 128
                and stripped[-1] == '.'
                and stripped[0].isupper()
                and count(line, '.') == 1)
    except IndexError:
        return False

def pairwise(it):
    a, b = tee(it)
    next(b, None)
    return izip_longest(a, b)

def split(s, sep=' \n'):
    sentence = []
    word = []
    beg = 0
    for i, char in enumerate(s):
        if char not in sep:
            word.append(char)
        else:
            if word:
                sentence.append((''.join(word), beg, i))
                word = []
            beg = 1 + i
    else:
        if word:
            sentence.append((''.join(word), beg, i + 1))
    return sentence

def find(sentence, beg, end):
    """Searches objects returned by the above split function.
    """
    for i, (w, b, e) in enumerate(sentence):
        if b <= beg and end <= e:
            #return i + 1, w
            return i, w
    return -1, None

def ident(x):
    """Simple identity.
    """
    return x

def filled(stream, filler=None, key=None, start=0):
    """Fills in empty records.
    """
    i = start
    filler = filler if filler else ident
    key = key if key else ident
    it = iter(stream)
    while True:
        elt = next(it)
        if not elt:
            continue
        for _ in range(i, key(elt)):
            #print i, 'returning', filler(i)
            yield filler(i)
            i += 1
        #print i, 'returning', elt
        yield elt
        i = key(elt)


def normalized(stream, key=None, filler=None, start=0, end=0):
    """Make sure the iterable has no 'gaps' in the keys, fills w/ filler otherwise.
    """
    key, filler = key if key else ident, filler if filler else ident
    n = start
    for elt in stream:
        k = key(elt)
        assert k >= n, 'problem: key of {} should be at least {}'.format(pformat(elt), n)
        while k > n:
#             print('Filling in', n, filler(n), file=sys.stderr)
            yield filler(n)
            n += 1
        yield elt
        n += 1
    if end > 0:
        for i in range(n, end):
            yield filler(i)


def Parser(handler):
    """Create and setup a new Parser object.
    """
    parser = xml.parsers.expat.ParserCreate()
    parser.buffer_text = True
    parser.buffer_size = 10 * M

    parser.StartElementHandler = handler.start_element
    parser.EndElementHandler = handler.end_element
    parser.CharacterDataHandler = handler.char_data

    return parser

def find_relations(f):
    relations = set()
    lines = ifilter(lambda l: l.strip() and not l.startswith('%') and not l.startswith('UNIQUE'), f)
    for line in itakewhile(lambda l: l.find('</GRLAB>'), idropwhile(lambda l: l.find('<GRLAB>'), lines)):
        try:
            relations.add(line.split()[1])
        except IndexError:
            pass
    return relations

REL, INDEX = 'rel', 'index'

# This should be renamed to split_with.
def blocks(predicate, iterable):
    """Breaks <iterable> into 'blocks', using <predicate> as separator.
    """
    it = iter(iterable)
    while True:
        b = list(itakewhile(predicate, it))
        if len(b) > 0:
            yield b
        else:
            break

class Dictionary(object):
    def __init__(self, **kw): self.__dict__.update(kw)
    def is_word(self, word, lang): return word in self.__dict__[lang]

class SpanishSet(object):
    def __init__(self): self.words = SpanishSet._make_spanish_dict()
    def __contains__(self, item): return item in self.words
    is_word = __contains__

    @staticmethod
    def _make_spanish_dict():
        import os, string
        corr = os.path.join(os.environ['FREELINGSHARE'], 'es', 'corrector', 'corrector.src')
        return set(chain.from_iterable([l[1].split(',') for l in imap(string.split, uopen(corr))]))

class EnglishSet(object):
    from nltk.corpus import wordnet as _wn #@UnusedImport
    def __contains__(self, item): return EnglishSet._wn.synsets(item)
    is_word = __contains__

import os
def freelingsh(*path):
    return os.path.join(*[os.environ['FREELINGSHARE']] + list(path))

def pairs(iterable):
    it = iter(iterable)
    while True:
        try:
            yield (next(it), next(it))
        except StopIteration:
            break


# from itertools import islice
from string import punctuation
class Lemmatizer(object):
    """A Freeling dictionary.
    """
    def __init__(self, ins):
        def db():
            "returns a list of (word, (lemma, tag)+) elements."
            return [(l[0], [p for p in pairs(l[1:])]) for l in (l.rstrip().split() for l in ins)]
        update(self, lemma=dict((w, pp) for w, pp in db()))
#         pprint([l for l in islice(self.lemma.iteritems(), 20)], stream=sys.stderr)

    def get(self, word, pos=None):
        if word in punctuation or pos in punctuation or word.isdigit() or len(word) == 1:
            return [(word, pos if pos else word)]
        else:
            pairs = self.lemma.get(word, ())
            matching = pairs if pos is None else [(l, t) for l, t in pairs if t.startswith(pos)]
            return matching if matching else [(u'<unknown>', pos)]


from nltk.corpus import wordnet
def derivations(lemma):
    """Returns all the lemmas that are derivationally related with <lemma>.
    """
    return set(reduce(lambda l, m: l + m,
                      [l.derivationally_related_forms() for l in wordnet.lemmas(lemma)], []))  # @UndefinedVariable


def Environment(envm={}, **envkw):
    """An environment expander.
    """
    def merged(*maps):
        """Merge *maps in order."""
        def update(m1, m2):
            m1.update(m2)
            return m1
        return reduce(update, maps, {})

    def expand_one(x, e):
        def mformat(x): # Maybe-format
            return x.format(**e) if type(x) in (str, unicode) else x
        return map(lambda v: mformat(v), x) if type(x) in (list, tuple) else mformat(x)

    def expand(x, **kw):
        env = merged(envm, envkw, kw)
        e = dict((k, expand_one(v, env)) for k, v in env.items())
        return expand_one(x, e)

    return expand


# Noun, verb, adjective, adverb tags
tags = N, V, A, S = 'nvas'

def tag(word, pos):
    return (word, pos)

def untag((word, pos)):
    return '%s.%s' % (word, pos)

tagN = partial(tag, pos=N)
tagV = partial(tag, pos=V)

# Change this to have the d* functions below actually work
_debug = False
# _debug = True

def noop(*args, **entries):
    pass

def _dforeach(function, collection):
    for e in collection:
        function(e)

dprint = partial(print, file=uwriter(sys.stderr)) if _debug else noop
dpprint = partial(pprint, stream=uwriter(sys.stderr)) if _debug else noop
dforeach = _dforeach if _debug else noop

def read_seed(iterable, tag=True):
    """Returns a list of <rel-type, tagged-noun, tagged-verb> triples,
    where rel-type is either subj-verb or obj-verb.
    """
    def _tag((a, b, c)):
        return ('subj-verb', tagN(a), tagV(b)) if c == '-' else ('obj-verb', tagN(c), tagV(b))
    def _raw((a, b, c)):
        return ('subj-verb', a, b) if c == '-' else ('obj-verb', c, b)
    return map(_tag if tag else _raw, iterable)


class FileIterator(object):
    def __init__(self, f):
        update(self, file=f, buffer=u'', size=1024*1024, linesep=u'\n')
    def __iter__(self):
        return self
    def next(self):
        buf = self.buffer
        ni = 1 + buf.find(self.linesep)
        while ni == 0:
            r = self.file.read(self.size)
            if len(r) == 0:
                ni = len(buf)
                break
            else:
                buf += r
                ni = 1 + buf.find(self.linesep)
        if ni == 0:
            raise StopIteration()
        b = buf[:ni]
        buf = buf[ni:]
        return b

from contextlib import contextmanager

@contextmanager
def closing(*things):
    """A context manager for safely dealing with many open files.

    >>> class T(object):
    ...     def close(self):
    ...         print self.__class__.__name__, 'closed'
    ...
    >>> with closing(*[T() for _ in range(3)]):
    ...     pass
    ...
    T closed
    T closed
    T closed
    """
    collections = {list, tuple, set}
    dictionaries = {dict, }
    try:
        yield things
    finally:
        for t in things:
            if type(t) in collections:
                for e in t: e.close()
            elif type(t) in dictionaries:
                for e in t.values(): e.close()
            else:
                t.close()

class Unbuffered:
    """An unbuffered stream.
    """
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def grouped(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.
    """
    # grouped(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def grouped2(n, iterable):
    """Collect data into fixed-length chunks or blocks.
    """
    args = [iter(iterable)] * n
    return izip(*args)


def flattened(listoflists):
    """Flatten one level of nesting.
    """
    return chain.from_iterable(listoflists)


def takewhile(predicate, it):
    """Our version takes up to, and including, the element that negates predicate.
    """
    for x in it:
        yield x
        if not predicate(x):
            break


# A slightly tweaked version of the same function in the AIMA
# codebase (https://code.google.com/p/aima-python/)
def update(x, *maps, **entries):
    """Update a dict; or an object with slots; according to entries.

    >>> update({'a': 1}, a=10, b=20)
    {'a': 10, 'b': 20}
    >>> update(Struct(a=1), a=10, b=20)
    Struct(a=10, b=20)
    """
    for m in maps:
        if isinstance(m, dict):
            entries.update(m)
        else:
            entries.update(m.__dict__)

    if isinstance(x, dict):
        x.update(entries)
    else:
        x.__dict__.update(entries)
    return x


def abstract():
    raise NotImplementedError()


# A JSON dump/pretty print
json_dump = partial(json.dump, sort_keys=True, indent=2, ensure_ascii=False, separators=(',', ': '))


def json_pprint(ins, outs):
    with ins:
        try:
            obj = json.load(ins)
        except ValueError, e:
            raise SystemExit(e)
    with outs:
        json_dump(obj, outs)
        outs.write('\n')


def dict_dfs(x):
    """Perform DFS on the values of a dictionary.
    """
    if isinstance(x, dict):
        for k, v in x.iteritems():
            yield k
            for y in dict_dfs(v):
                yield y
    elif isinstance(x, list):
        for y in x:
            for z in dict_dfs(y):
                yield z
    else:
        yield x


def cumulative(seq):
    """Returns a sequence of the cumulative lengths in <seq>.
    """
    acc = 0
    lengths = []
    for e in seq:
        lengths.append(acc)
        acc += 1 + len(e)
    return lengths


from time import strftime
DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'

def lines(it, split_with=None):
    return (l.rstrip() for l in it) if not split_with else (l.rstrip().split(split_with) for l in it)

def log(message):
    print('%s - %s' % (strftime(DATEFORMAT), message))


# This is from AIMA (P. Norvig's code). Always useful.
class Struct(object):
    """Create an instance with argument=value slots.
    For lightweight objects whose class doesn't matter.
    """
    def __init__(self, *maps, **entries):
        for m in maps:
            entries.update(m)
        self.__dict__.update(entries)

    def __cmp__(self, other):
        if isinstance(other, Struct):
            return cmp(self.__dict__, other.__dict__)
        else:
            return cmp(self.__dict__, other)

    def __repr__(self):
        args = ["%s=%s" % (k, repr(v)) for (k, v) in list(vars(self).items())]
        return "Struct(%s)" % ", ".join(args)

    def __len__(self):
        return self.__dict__.__len__()

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __json__(self):
        return self.__dict__


if __name__ == '__main__':
    if len(sys.argv) > 1:
        import doctest
        doctest.testmod()
    else:
        json_pprint(ureader(sys.stdin), uwriter(sys.stdout))
