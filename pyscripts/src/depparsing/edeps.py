# Encoding: UTF-8

"""
.. module:: edeps
    :platform: Unix
    :synopsis: Extract dependencies from a parse file. Three parsers are supported: Freeling, MALT, and RASP.

Extract dependencies from a parse file. Three parsers are supported: Freeling, MALT, and RASP.

.. moduleauthor:: Luca Gilardi <lucag@icsi.berkeley.edu>

"""

from __future__ import print_function

import re, sys, util
import split
import json

from cStringIO import StringIO
from itertools import ifilter
from pprint import pprint, pformat
from collections import namedtuple
from textwrap import dedent
from util import abstract, update, takewhile, normalized, flattened, uwriter, cumulative
from depparsing.util import dprint, dpprint
from functools import partial
from depparsing.findrel import sentence

# Only picking up the relation, word, lemma (basic form), POS tag, and word position (0-based).
deprec = namedtuple('deprec', ('rel', 'word', 'lemma', 'pos', 'wordn', 'head'))

TOP_DEPREC = deprec('#top#', None, None, '-', 0, ())

def Deprec(rel, word, lemma, pos, wordn, head):
    return deprec(rel, word, lemma.lower(), pos, int(wordn), head)

def fdeprec(r):
    """Turn a deprec in a readable (i.e., nonrecursive) tuple.

    :param r: the dependency record t.
    :type r: deprec.

    """
    if r.head:
        return r.rel, r.lemma, r.pos, r.head.lemma, r.head.pos
    else:
        return r.rel, r.lemma, r.pos, '-', '-'

def pformat_deprec(r):
    s = uwriter(StringIO())
    pprint_deprec(r, s)
    formatted = s.getvalue()
    s.close()
    return formatted

def pprint_deprec(r, stream=sys.stdout):
    """Print a deprec on stream.

    :param r: the dependency record to print.
    :type r: deprec.
    :param stream: the stream to print on.
    :type stream: file.

    """
    def helper(dep, d=0):
        print(u'(', file=stream, end='')
        for k, v in dep._asdict().items():
            if k != 'head' or not dep.head:
                print(u'{}={},'.format(k, v), end='', file=stream)
            else:
                print(u'{}='.format(k), file=stream, end='')
                helper(dep.head, d + 1 + len('head='))
            print (u'\n', u' ' * (d + 1), file=stream, end='')
        print(u')', file=stream)
    if type(r) == deprec:
        helper(r)
    else:
        pprint(r, stream=stream)


def test_pprint():
    r = deprec('rel', 'word', 'lemma', 'pos', 1, deprec('rel1', 'word1', 'lemma1', 'pos1', 0, ()))
    pprint_deprec(r)
    r1 = deprec('rel2', 'word2', 'lemma2', 'pos2', 2, r)
    pprint_deprec(r1)


class DepParser(object):
    """Abstract class for parsing the output of a dependency parser."""
    def parse(self, it):
        """Parse the strings in the argument.

        :param it: an iterator over the strings to parse.
        :returns: a list or a generator of tuples containing the parsed data.

        """
        abstract()


class DepBuilder(object):
    """Abstract class for a building a common representation (i.e., relatively independent of
    the parser used) of dependency trees"""
    def __init__(self, **entries):
        update(self, entries)
        
    def build(self, sent_it, parsed_it):
        """Build a forest of dependency trees.

        :param sent_it: an iterator over input sentences (only needed by the RASP parser).
        :param parsed_it: an iterator over the (parsed) output of the dependency parser.
        :returns: a list of deprecs.

        """
        abstract()


class MaltDepParser(DepParser):
    """Parser for a relations relative to a single sentence. A generator
    that returns all the relations up to and including the line with the 'SENT' POS.
    """
    @staticmethod
    def _groups(tokens):
        for t in tokens:
            yield t
            if len(t) == 0:
                break

    def __init__(self, groups=None):
        update(self, groups=groups if groups else self._groups)

    def parse(self, tokens):
        while True:
            block = [e for e in self.groups(tokens) if len(e) > 1]
            if len(block):
                yield block
            else:
                break


class MaltDepBuilder(DepBuilder):
    """Builds deprec elements recursively starting from a parsed block.

    The block is expected to have the following structure (all fields are
    separated by tab characters)::

        <column name="ID" category="INPUT" type="INTEGER"/>
        <column name="FORM" category="INPUT" type="STRING"/>
        <column name="LEMMA" category="INPUT" type="STRING"/>
        <column name="CPOSTAG" category="INPUT" type="STRING"/>
        <column name="POSTAG" category="INPUT" type="STRING"/>
        <column name="FEATS" category="INPUT" type="STRING"/>
        <column name="HEAD" category="HEAD" type="INTEGER"/>
        <column name="DEPREL" category="DEPENDENCY_EDGE_LABEL" type="STRING"/>
        <column name="PHEAD" category="IGNORE" type="INTEGER" default="_"/>
        <column name="PDEPREL" category="IGNORE" type="STRING" default="_"/>

    """
    @staticmethod
    def _index(block):
        """Index by rank order.

        :param: the block to index.
        :returns: a map rank -> block.

        """
        return dict((e[0], e) for e in block)

    def build(self, parsed_it, sentences, keep=lambda x: True):
        """Build a forest of dependency trees for each block of dependencies in parsed_it

        :param sent_it: an iterator over input sentences (only needed by the RASP parser).
        :param parsed_it: an iterator over the (parsed) output of the dependency parser.
        :param keep: a predicate function to filter dependency records: it should answer
            True iff the argument has to be kept.
        :returns: a pair of lists <[sent-id, rank, word, lemma, pos], [sent-id, deprec]>.

        """
        def make_deprec((n, word, lemma, _1, pos, _2, headn, rel, _3, _4)):
#             pprint((word, lemma, pos, sid, headn, rel))
            n, headn = map(int, (n, headn))
            if headn == 0:
                return Deprec(rel, word, lemma, pos, n, ())
            else:
                return Deprec(rel, word, lemma, pos, n, make_deprec(block[headn - 1]))

        for s_id, block in enumerate(parsed_it, start=1):
#             assert len(block) == len(sentence), 'problem at s_id = %s' % s_id
#             idx = self._index(block)
            sentence = [e[1] for e in block]
#             dprint('build', u' '.join(sentence))
            deprecs = filter(keep, [make_deprec(elt) for elt in block])
#             deprecs = [make_deprec(elt) for elt in block]
#             pprint(deprecs)
            yield ([(s_id, n, word, lemma, pos) for n, word, lemma, _, pos, _, _, _, _, _ in block],
                   [(s_id, d) for d in deprecs])


class MaltDepBuilderOld(DepBuilder):
    """Builds deprec elements recursively starting from a parsed block.

    This is for RUWAC only!

    The expected block structure is the following::

        column 0: word
        column 1: feature classification of word in column 1
        column 2: lemma of word in column 1
        column 3: POS of word in column 1
        column 4: rank order in sentence for word in column 1
        column 5: index of word of immediate dependency for word in column 1
        column 6: label for the relationship between word in column 1 and the word
                  upon which it is dependent as indicated in column 6

    """
    @staticmethod
    def _index(block):
        """Index by rank order.
        """
        return dict((e[4], e) for e in block)

    def build(self, parsed_it, sentences, root=(), keep=lambda x: True):
        """Build a forest of dependency trees for each block of dependencies in parsed_it

        :param sent_it: an iterator over input sentences (only needed by the RASP parser).
        :param parsed_it: an iterator over the (parsed) output of the dependency parser.
        :param root: the root element of the tree.
        :param keep: a predicate function to filter dependency records: it should answer
            True iff the argument has to be kept.
        :returns: a list of deprecs.

        """
        def make_deprec((word, _, lemma, pos, rank, headn, rel)):
#             pprint((word, lemma, pos, id, headn, rel))
            return (Deprec(rel, word, lemma, pos, rank, root) if headn == '0'
                    else Deprec(rel, word, lemma, pos, rank, make_deprec(idx[headn])))

        for s_id, sentence, block in ((i, s, b) for i, (s, b) in enumerate(zip(sentences, parsed_it), start=1)):
            assert block, pformat(block)
            idx = self._index(block)
#             pprint(idx)
            deprecs = filter(keep, [make_deprec(elt) for elt in block])
#             deprecs = [make_deprec(elt) for elt in block]
#             pprint(deprecs)
            yield ([(s_id, int(rank) - 1, word, lemma, pos)
                    for _, (word, _, lemma, pos, rank, _, _) in idx.items()],
                   [(s_id, d) for d in deprecs])


class JsonDepBuilder(DepBuilder):
    """Malt/Json format. It builds a list of sequences of words, each like the following:

    .. code-block:: json

        { "dep": { "head": "7", "type": "опред" },
          "end": 67,
          "form": "некультурная",
          "idx": 5,
          "lem": "некультурный",
          "n": "6",
          "pos": "A",
          "start": 55 }

    """
    def build(self, parsed, root=(), keep=lambda x: True):
        """Generates a deprec list for each block of dependencies in <parsed>.

        :param keep: a filtering predicate (the default selects all)
        """
        # There are cycles in RASP-generated dependency "trees" 
        def make_deprec(word, seen):
            form, lemma, pos = map(lambda i: word.get(i, '<?>'), (key.form, key.lem, key.pos))
            # wordn can contain a list of word numbers: let's take the first.
            wordn = word['n'].split()[0]
            # Apparently not all the word elements have a 'dep' key...
            if 'dep' in word:
                dep = word['dep'];
                rel = dep['type']
                # Also, 'head' can be None
                head = int(dep['head']) if 'head' in dep and dep['head'] is not None else 0
            else:
                rel, head = '-', 0

#             dpprint(seen)
#             dprint(rel, form, lemma, pos, wordn, head)
            
            if head in seen:
                return ()
            elif head == 0 or len(words) <= head:
                return Deprec(rel, form, lemma, pos, wordn, root)
            else:
                seen.add(head)
                return Deprec(rel, form, lemma, pos, wordn, make_deprec(words[head - 1], seen))

        key = self.key
        for s_id, sentence in enumerate(parsed, start=1):
            words = sentence['word']
            try:
                def debug_keep(dep):
                    k = keep(dep) if dep else False
                    dprint('dep', dep, 'returning', k)
                    return k
                    
                deprecs = filter(keep, [make_deprec(w, set()) for w in words])
                # wordn can contain a list of word numbers: let's take the first.
                yield ([(s_id, int(w['n'].split()[0]) - 1, w[key.form], w[key.lem], w.get(key.pos, '<?>')) 
                        for w in words],
                       [(s_id, d) for d in deprecs])
            except RuntimeError as x:
                dprint(u'>> problem', x, 'processing sentence idx=%s:' % sentence['idx'],
                       u' '.join(w['form'] for w in words))


class RaspDepParser(DepParser):
    """Parses a RASP output dependency tree.
    """
    def parse(self, dep_it, sent_it):
        HEADER, GR, BODY = 'HGB'
        inparen_re = re.compile(r'\(([^)]+)\)', re.UNICODE)
        ff_re = re.compile(r'([^+_:]+)\+?([\S]+)?:([0-9]+)_(\S+)', re.UNICODE)
        header_re = re.compile(r'(\)) +-?\d +; +\((?:-?\d+\.\d+)?\)', re.UNICODE)
        sent_re = re.compile(r'\|(?:\\\||[^|])+\||[^\s()]+', re.UNICODE)
        sent_splitter = split.splitter('rasp')

        def expand(field):
            match = ff_re.match(field)
            return match.groups() if match else field

        def by2(((_1, i), _2)): return i

        def filler(i):
            w = sentence[i - 1]
            return (w, i), [((w, w, i, u'-'), (w, w, i, u'-'), u'-')]

        # Translate '\\|' -> '|'
        def unescape(w):
            return re.sub(r'\\\|', '|', w)

        def form_or_lemma(i, lemma):
            return sentence[i] if i < len(sentence) else lemma
        
#         uerr = uwriter(sys.stderr)
        dependencies = {}
        status = HEADER
        n = 1
        for line in dep_it:
            line = line.decode('utf-8')
            if header_re.findall(line):
                assert status is HEADER
                if sent_it:
                    sentence = sent_splitter.findall(next(sent_it))
#                     pprint([(i, w) for i, w in enumerate(sentence, start=1)])
                else:
                    # Read sentence from input
                    noheader = header_re.sub(r'\1', line)
                    sentence = [unescape(w[1:-1]) if w[0] == '|' else w for w in sent_re.findall(noheader)]
                n += 1
                status = GR
                continue
            elif status is GR:
                assert line.startswith('gr-list') or len(line) == 0, (status, line)
                dependencies = {}
                status = BODY
                continue
            elif len(line) == 0:
                assert status in (BODY, HEADER), (status, line)
                if status is not HEADER:
#                     pprint(dependencies.items())
#                     yield dict(normalized(sorted(dependencies.items(), key=by2), key=by2, filler=filler, start=1))
                    yield sentence, dependencies
                    dependencies = {}
                    sentence = None
                    status = HEADER
                continue
            assert status is BODY, (status, line)
            inparen = inparen_re.match(line)
            # There can be garbage in the input
            if inparen:
                assert inparen, (status, line)
                fields = [unescape(e[1:-1]) if e[0] == '|' else e for e in inparen.group(1).split()]
                deps = map(expand, fields)
                _rel = deps[0]
                _sub = deps[1] if len(deps) > 1 and type(deps[1]) is not tuple else None
                rel = '%s.%s' % (_rel, _sub) if _sub else _rel
                try:
                    head, dep = map(lambda (l, _, i, p): (l.lower(), form_or_lemma(int(i) - 1, l.lower()), int(i), p),
                                    filter(lambda e: type(e) is tuple, deps[1:])[-2:])
                    b_i = dep[0], dep[2]
                    # This is the triple's format
                    dependencies.setdefault(b_i, []).append((dep, head, rel))
                except ValueError:
                    pass
#                     print(u'Ignoring {}'.format(deps), file=uerr)
                except IndexError:
                    dprint(u'Problem retrieving dependency info for sent "%s"' % line, file=uwriter(sys.stderr))


class RaspDepBuilder(DepBuilder):
    def build(self, parsed_it, sent_it, keep=lambda dep: dep):
        def make_deprec(dep, seen):
            """dep is a list of <dep, head, rel> triples.
            """
            if dep not in seen:
                seen.add(dep)
                l, w, r, p = dep
                for _, head, rel in dependencies.get((l, r), [(dep, dep, '#top#')]):
                    hr, _, hr, _ = head
                    if hr == r:
                        yield Deprec(rel, w, l, p, r, ())
                    else:
                        for h in make_deprec(head, seen):
                            yield Deprec(rel, w, l, p, r, h)

        def filler(r):
            i = r - 1
            w = sentence[i] if i < len(sentence) else ''
            if i >= len(sentence):
                dprint('Cannot find filler for pos', i, 'in sentence (%s)' % s_id, sentence)
            return (w, w, r, u'-')

        def key((_0, _1, r, _3)):
            return r

        for s_id, (sentence, dependencies) in enumerate(parsed_it, start=1):
#             pprint(dependencies)
            try:
#                 pprint(dependencies)
                deps = set(flattened([(d, h) for d, h, _ in flattened(dependencies.values())]))
                flattened_deps = normalized(sorted(deps, key=key), key=key, filler=filler, start=1, end=1 + len(sentence))
#                 pprint(flattened_deps)
                dd = set(flattened([list(make_deprec(d, set())) for d in flattened_deps]))
#                 pprint(dd)
                deprecs = filter(keep, dd)
            except:
                dprint('Problem with sentence', s_id)
                dpprint(dependencies)
#                 raise

            words = normalized(sorted(set(reduce(lambda x, y: x + list(y[0:2]),
                                                 flattened(dependencies.values()), [])), key=key),
                               key=key, filler=filler, start=1, end=1 + len(sentence))
            yield ([(s_id, r - 1, f, l, p) for l, f, r, p in words],
                   [(s_id, d) for d in deprecs],
                   dependencies)


TEST_SS = dedent(u"""\
    Это    P--nsnn    это    P    1    2    предик
    типа    Ncmsgn    тип    N    2    0    ROOT
    девушка    Ncfsny    девушка    N    3    2    квазиагент
    в    Sp-a    в    S    4    3    атриб
    один    P--msaa    один    P    5    6    количест
    день    Ncmsan    день    N    6    4    предл
    отмечает    Vmip3s-a-e    отмечать    V    7    2    вводн
    ,    ,    ,    ,    8    7    PUNC
    что    C    что    C    9    7    предик
    одного    P--nsga    один    P    10    13    1-компл
    на    Sp-l    на    S    11    13    обст
    себе    P----ln    себя    P    12    11    предл
    женила    Vmis-sfa-p    женить    V    13    9    подч-союзн
    и    C    и    C    14    15    огранич
    квартиру    Ncfsan    квартира    N    15    13    предик
    ,    ,    ,    ,    16    15    PUNC
    алименты    Ncmpan    алименты    N    17    18    предик
    надыбала    Vmis-sfa-p    надыбать    V    18    2    сент-соч
    и    C    и    C    19    18    сочин
    нашла    Vmis-sfa-p    найти    V    20    19    соч-союзн
    второго    Momsa    второй    M    21    23    предик
    -    -    -    -    22    21    PUNC
    изуродовал    Vmis-sma-p    изуродовать    V    23    20    подч-союзн
    ее    P-3fsan    она    P    24    23    1-компл
    ,    ,    ,    ,    25    24    PUNC
    порвал    Vmis-sma-p    порвать    V    26    18    сочин
    все    P---paa    весь    P    27    28    опред
    дырки    Ncfpan    дырка    N    28    26    1-компл
    ,    ,    ,    ,    29    28    PUNC
    заразил    Vmis-sma-p    заразить    V    30    26    сочин
    всеми    P---pia    весь    P    31    32    опред
    венболезнями    Ncfpin    венболезнь    N    32    30    2-компл
    ,    ,    ,    ,    33    32    PUNC
    заставил    Vmis-sma-p    заставить    V    34    30    сочин
    подарить    Vmn----a-p    подарить    V    35    34    2-компл
    квартиру    Ncfsan    квартира    N    36    35    1-компл
    и    C    и    C    37    35    сочин
    снабжать    Vmn----a-e    снабжать    V    38    37    соч-союзн
    его    P-3msan    он    P    39    38    1-компл
    водкой    Ncfsin    водка    N    40    38    2-компл
    .    SENT    .    S    41    40    PUNC
    Оба    Mcm-n    оба    M    1    2    предик
    почитаются    Vmip3p-m-e    почитаться    V    2    0    ROOT
    в    Sp-a    в    S    3    2    обст
    день    Ncmsan    день    N    4    3    предл
    любви    Ncfsgn    любовь    N    5    4    квазиагент
    .    SENT    .    S    6    5    PUNC
    А    C    а    C    1    0    ROOT
    хорошо    R    хорошо    R    2    4    обст
    бы    Q    бы    Q    3    2    огранич
    объединить    Vmn----a-p    объединить    V    4    1    соч-союзн
    события    Ncnpan    событие    N    5    4    1-компл
    18-88    Mc---p    18-88    M    6    5    нум-аппоз
    ,    ,    ,    ,    7    6    PUNC
    Компьенский    Afpmsnf    компьенский    A    8    9    опред
    лес    Ncmsnn    лес    N    9    5    сочин
    -    -    -    -    10    9    PUNC
    Хайратонский    Afpmsnf    хайратонский    A    11    12    опред
    мост    Ncmsnn    мост    N    12    9    сочин
    .    SENT    .    S    13    12    PUNC
    Символы    Ncmpnn    символ    N    1    0    ROOT
    капитуляции    Ncfsgn    капитуляция    N    2    1    1-компл
    кайзера    Ncmsgy    кайзер    N    3    2    квазиагент
    и    C    и    C    4    2    сочин
    совка    Ncfsnn    совка    N    5    4    соч-союзн
    .    SENT    .    S    6    5    PUNC""").split('\n')

TEST_SS2 = dedent(u"""\
    1    Нужно    нужно    R    R    R    0    ROOT    _    _
    2    создавать    создавать    V    V    Vmn----a    1    предик    _    _
    3    что-то    что-то    P    P    P--nsan    2    1-компл    _    _
    4    новое    новый    A    A    Afpnsa    3    опред    _    _
    5    ,    ,    ,    ,    ,    4    PUNC    _    _
    6    но    но    C    C    C    1    сент-соч    _    _
    7    нельзя    нельзя    R    R    R    6    соч-союзн    _    _
    8    общество    общество    N    N    Ncnsan    9    1-компл    _    _
    9    вылечить    вылечить    V    V    Vmn----a    7    предик    _    _
    10    по    по    S    S    Sp-p    9    обст    _    _
    11    частностям    частность    N    N    Ncfpdn    10    предл    _    _
    12    ,    ,    ,    ,    ,    11    PUNC    _    _
    13    общество    общество    N    N    Ncnsnn    9    предик    _    _
    14    нужно    нужный    A    A    Afpns-s    0    ROOT    _    _
    15    лечить    лечить    V    V    Vmn----a    0    ROOT    _    _
    16    в    в    S    S    Sp-l    15    обст    _    _
    17    целом    целое    N    N    Ncnsln    16    предл    _    _
    18    ,    ,    ,    ,    ,    17    PUNC    _    _
    19    потому    потому    P    P    P-----r    0    ROOT    _    _
    20    что    что    C    C    C    42    соотнос    _    _
    21    общество    общество    N    N    Ncnsnn    23    пролепт    _    _
    22    –    –    -    -    -    21    аппоз    _    _
    23    это    это    P    P    P--nsnn    24    предик    _    _
    24    система    система    N    N    Ncfsnn    0    ROOT    _    _
    25    ,    ,    ,    ,    ,    24    PUNC    _    _
    26    и    и    C    C    C    24    сочин    _    _
    27    если    если    C    C    C    33    обст    _    _
    28    идет    идти    V    V    Vmip3s-a    27    подч-союзн    _    _
    29    развал    развал    N    N    Ncmsnn    28    предик    _    _
    30    в    в    S    S    Sp-l    29    атриб    _    _
    31    экономике    экономика    N    N    Ncfsln    30    предл    _    _
    32    ,    ,    ,    ,    ,    31    PUNC    _    _
    33    идут    идти    V    V    Vmip3p-a    26    соч-союзн    _    _
    34    реформы    реформа    N    N    Ncfpnn    33    предик    _    _
    35    ,    ,    ,    ,    ,    34    PUNC    _    _
    36    которые    который    P    P    P---pna    37    предик    _    _
    37    отбрасывают    отбрасывают    V    V    Vmip3p-a    34    опред    _    _
    38    людей    человек    N    N    Ncmpay    37    1-компл    _    _
    39    в    в    S    S    Sp-a    37    обст    _    _
    40    бедность    бедность    N    N    Ncfsan    39    предл    _    _
    41    ,    ,    ,    ,    ,    40    PUNC    _    _
    42    то    то    C    C    C    24    сочин    _    _
    43    частностями    частность    N    N    Ncfpin    42    соч-союзн    _    _
    44    не    не    Q    Q    Q    45    огранич    _    _
    45    обойдешься    обойтись    V    V    Vmif2s-a    0    ROOT    _    _
    46    ,    ,    ,    ,    ,    45    PUNC    _    _
    47    невозможно    невозможно    R    R    R    45    вводн    _    _
    48    вытащить    вытащить    V    V    Vmn----a    45    сочин    _    _
    49    себя    себя    P    P    P----an    48    1-компл    _    _
    50    из    из    S    S    Sp-g    48    обст    _    _
    51    трясины    трясина    N    N    Ncfsgn    50    предл    _    _
    52    за    за    S    S    Sp-a    48    обст    _    _
    53    волосы    волос    N    N    Ncmpan    52    предл    _    _
    54    ,    ,    ,    ,    ,    53    PUNC    _    _
    55    нужно    нужно    R    R    R    48    разъяснит    _    _
    56    сначала    сначала    R    R    R    57    обст    _    _
    57    осушить    осушить    V    V    Vmn----a    55    предик    _    _
    58    трясину    трясина    N    N    Ncfsan    57    1-компл    _    _
    59    .    .    S    S    SENT    58    PUNC    _    _""").split('\n')

TEST_SS3 = dedent(u"""\
    1    «Мы    «мы    N    N    Ncfsgn    0    ROOT    _    _
    2    видим    видеть    V    V    Vmip1p-a    1    опред    _    _
    3    социальную    социальный    A    A    Afpfsa    4    опред    _    _
    4    опасность    опасность    N    N    Ncfsan    2    1-компл    _    _
    5    указанных    указанный    A    A    Afp-pg    6    опред    _    _
    6    продуктов    продукт    N    N    Ncmpgn    4    квазиагент    _    _
    7    в    в    S    S    Sp-l    2    обст    _    _
    8    том    то    P    P    P--nsln    7    предл    _    _
    9    ,    ,    ,    ,    ,    8    PUNC    _    _
    10    что    что    C    C    C    8    эксплет    _    _
    11    банки    банк    N    N    Ncmpnn    15    предик    _    _
    12    в    в    S    S    Sp-a    15    обст    _    _
    13    последнее    последний    A    A    Afpnsa    14    опред    _    _
    14    время    время    N    N    Ncnsan    12    предл    _    _
    15    проводят    проводить    V    V    Vmip3p-a    10    подч-союзн    _    _
    16    агрессивный    агрессивный    A    A    Afpmsa    17    опред    _    _
    17    маркетинг    маркетинг    N    N    Ncmsan    15    1-компл    _    _
    18    ,    ,    ,    ,    ,    17    PUNC    _    _
    19    закредитовывают    закредитовывают    V    V    Vmip3p-a    15    сочин    _    _
    20    семьи    семья    N    N    Ncfsgn    19    1-компл    _    _
    21    и    и    C    C    C    19    сочин    _    _
    22    ввергают    ввергают    V    V    Vmip3p-a    21    соч-союзн    _    _
    23    их    они    P    P    P-3-pan    22    1-компл    _    _
    24    в    в    S    S    Sp-a    22    2-компл    _    _
    25    бедность    бедность    N    N    Ncfsan    24    предл    _    _
    26    ,    ,    ,    ,    ,    25    PUNC    _    _
    27    —    —    -    -    -    29    вспом    _    _
    28    возмущается    возмущаться    V    V    Vmip3s-a    29    опред    _    _
    29    Янин    янин    N    N    Npmsny    1    аппоз    _    _
    30    .    .    S    S    SENT    29    PUNC    _    _

    1    Афанасий    афанасий    N    N    Npmsny    0    ROOT    _    _
    2    и    и    C    C    C    1    сочин    _    _
    3    Прасковья    прасковья    N    N    Npfsny    2    соч-союзн    _    _
    4    Кривошапкины    кривошапкин    N    N    Npmpny    3    аппоз    _    _
    5    имели    иметь    V    V    Vmis-p-a    0    ROOT    _    _
    6    12    12    M    M    Mc    7    количест    _    _
    7    детей    ребенок    N    N    Ncmpgy    5    1-компл    _    _
    8    и    и    C    C    C    5    сочин    _    _
    9    после    после    S    S    Sp-g    0    ROOT    _    _
    10    раскулачивания    раскулачивание    N    N    Ncnsgn    9    предл    _    _
    11    их    их    P    P    P-----a    12    1-компл    _    _
    12    отца    отец    N    N    Ncmsgy    10    1-компл    _    _
    13    Ивана    иван    N    N    Npmsgy    10    квазиагент    _    _
    14    Осиповича    осипович    N    N    Ncmsgy    13    аппоз    _    _
    15    в    в    S    S    Sp-l    10    атриб    _    _
    16    1922–1923    1922–1923    M    M    Mc    17    опред    _    _
    17    годах    год    N    N    Ncmpln    15    предл    _    _
    18    впали    впасть    V    V    Vmis-p-a    10    опред    _    _
    19    в    в    S    S    Sp-a    18    1-компл    _    _
    20    бедность    бедность    N    N    Ncfsan    19    предл    _    _
    21    .    .    S    S    SENT    20    PUNC    _    _

    """).split('\n')

def test_JsonDepBuilder():
    docs = json.load(open('/tscratch/tmp/jhong/extractruwac/int_ruwac_000001.json/pp.json'))
    deplists = list(JsonDepBuilder().build(docs['sentences'], None))
    for _, deps in deplists:
        for _, d in deps:
            pprint_deprec(d, stream=uwriter(sys.stderr))

def test_MaltDepParser():
    def groups(tokens):
#             return takewhile(lambda l: l[1] != 'SENT', tokens)
        return takewhile(lambda l: len(l) > 0, tokens)

    dp = MaltDepParser(groups=groups)

    r = dp.parse(l.split() for l in TEST_SS)
    pprint(list(r))

    r = dp.parse(l.split() for l in TEST_SS2)
    pprint(list(r))

    r = dp.parse(l.split() for l in TEST_SS3)
    pprint(list(r))

def test_MaltDepBuilder1():
    dp = MaltDepParser()
    parsed = list(dp.parse(l.split() for l in TEST_SS2))
    pprint(parsed)
    builder = MaltDepBuilder()
    deplists = builder.build(parsed)
    uout = uwriter(sys.stdout)
    for _, deps in deplists:
        for _, d in deps:
#             print(p)
            for e in fdeprec(d):
                print(e, end=' ', file=uout)
            else:
                print(file=uout)
        else:
            print(file=uout)

def test_MaltDepBuilder2():
    dp = MaltDepParser()
    parsed = list(dp.parse(l.split() for l in TEST_SS2))
#     pprint(parsed)
    builder = MaltDepBuilder()
    deplists = builder.build(parsed)
    uout = uwriter(sys.stdout)
    for _, deps in deplists:
        for _, d in deps:
            pprint_deprec(d, stream=uout)


TEST_SS4 = (dedent("""\
                I declare resumed the session of the European Parliament adjourned on Friday 17 December 1999, \
                and I would like once again to wish you a happy new year in the hope that you enjoyed a pleasant festive period.
                """),
            dedent("""\
                (I |declare| |resumed| |the| |session| |of| |the| |European| |Parliament| |adjourned| |on| |Friday| |17| |December| |1999| |,| |and| I |would| |like| |once| |again| |to| |wish| |you| |a| |happy| |new| |year| |in| |the| |hope| |that| |you| |enjoyed| |a| |pleasant| |festive| |period| |.|) 1 ; (-50.303)
                gr-list: 1
                (|ncsubj| |declare:2_VV0| |I:1_PPIS1| _)
                (|passive| |resume+ed:3_VVN|)
                (|xcomp| _ |declare:2_VV0| |resume+ed:3_VVN|)
                (|obj| |resume+ed:3_VVN| |session:5_NN1|)
                (|det| |session:5_NN1| |the:4_AT|)
                (|iobj| |session:5_NN1| |of:6_IO|)
                (|dobj| |of:6_IO| |Parliament:9_NNJ1|)
                (|det| |Parliament:9_NNJ1| |the:7_AT|)
                (|ncmod| _ |Parliament:9_NNJ1| |European:8_JJ|)
                (|passive| |adjourn+ed:10_VVN|)
                (|ncsubj| |adjourn+ed:10_VVN| |Parliament:9_NNJ1| |obj|)
                (|xmod| _ |Parliament:9_NNJ1| |adjourn+ed:10_VVN|)
                (|ccomp| _ |adjourn+ed:10_VVN| |on:11_II|)
                (|ccomp| _ |on:11_II| |like:20_VV0|)
                (|ncsubj| |like:20_VV0| |and:17_CC| _)
                (|aux| |like:20_VV0| |would:19_VM|)
                (|xcomp| |to| |like:20_VV0| |wish:24_VV0|)
                (|ncmod| _ |wish:24_VV0| |again:22_RR|)
                (|obj2| |wish:24_VV0| |year:29_NN1|)
                (|dobj| |wish:24_VV0| |you:25_PPY|)
                (|det| |year:29_NN1| |a:26_AT1|)
                (|ncmod| _ |year:29_NN1| |in:30_II|)
                (|dobj| |in:30_II| |hope:32_NN1|)
                (|det| |hope:32_NN1| |the:31_AT|)
                (|ccomp| |that:33_CST| |hope:32_NN1| |enjoy+ed:35_VVD|)
                (|ncsubj| |enjoy+ed:35_VVD| |you:34_PPY| _)
                (|dobj| |enjoy+ed:35_VVD| |period:39_NN1|)
                (|det| |period:39_NN1| |a:36_AT1|)
                (|ncmod| _ |period:39_NN1| |pleasant:37_JJ|)
                (|ncmod| _ |period:39_NN1| |festive:38_JJ|)
                (|ncmod| _ |year:29_NN1| |happy:27_JJ|)
                (|ncmod| _ |year:29_NN1| |new:28_JJ|)
                (|ncmod| _ |again:22_RR| |once:21_RR|)
                (|conj| |and:17_CC| |December:14_NPM1|)
                (|conj| |and:17_CC| |I:18_ZZ1|)
                (|ncmod| _ |December:14_NPM1| |Friday:12_NPD1|)
                (|ncmod| |num| |December:14_NPM1| |1999:15_MC|)
                (|ncmod| |num| |December:14_NPM1| |17:13_MC|)"""))

TEST_SS5 = (dedent("""\
                The Commission is the executive and Parliament ought to have no desire whatsoever to take on this role, \
                for the sake of its own independence; but Parliament is a supervisory body, \
                and what better forum could there be in which to expound the reasoning behind \
                one' s decisions than a democratically-elected Parliament, indeed an ongoing \
                parliamentary discussion?
                """),
            dedent("""\
                (|The| |Commission| |is| |the| |executive| |and| |Parliament| |ought| |to| |have| |no| |desire| |whatsoever| |to| |take| |on| |this| |role| |,| |for| |the| |sake| |of| |its| |own| |independence| |;| |but| |Parliament| |is| |a| |supervisory| |body| |,| |and| |what| |better| |forum| |could| |there| |be| |in| |which| |to| |expound| |the| |reasoning| |behind| |one| |s| |decisions| |than| |a| |democratically-elected| |Parliament| |,| |indeed| |an| |ongoing| |parliamentary| |discussion| ?) 0 ; ()
                gr-list: 1
                (|obj| |take:15_VV0| |whatsoever:13_DDQV|)
                (|xmod| |to| |whatsoever:13_DDQV| |take:15_VV0|)
                (|ccomp| _ |take:15_VV0| |and:35_CC|)
                (|conj| |and:35_CC| |role:18_NN1|)
                (|conj| |and:35_CC| |be:41_VB0|)
                (|obj| |be:41_VB0| |forum:38_NN1|)
                (|aux| |be:41_VB0| |could:39_VM|)
                (|ncsubj| |be:41_VB0| |there:40_EX| _)
                (|pcomp| |be:41_VB0| |in:42_II|)
                (|dobj| |in:42_II| |which:43_DDQ|)
                (|obj| |expound:45_VV0| |which:43_DDQ|)
                (|xmod| |to| |which:43_DDQ| |expound:45_VV0|)
                (|obj2| |expound:45_VV0| |discussion:62_NN1|)
                (|dobj| |expound:45_VV0| |reasoning:47_NN1|)
                (|det| |discussion:62_NN1| |an:59_AT1|)
                (|ncmod| _ |discussion:62_NN1| |ongoing:60_JJ|)
                (|ncmod| _ |discussion:62_NN1| |parliamentary:61_JJ|)
                (|ncmod| _ |reasoning:47_NN1| |indeed:58_RR|)
                (|det| |reasoning:47_NN1| |the:46_AT|)
                (|ncmod| _ |reasoning:47_NN1| |behind:48_II|)
                (|dobj| |behind:48_II| |decision+s:52_NN2|)
                (|ncmod| _ |decision+s:52_NN2| |than:53_CSN|)
                (|dobj| |than:53_CSN| |Parliament:56_NNJ1|)
                (|det| |Parliament:56_NNJ1| |a:54_AT1|)
                (|passive| |democratically-elect+ed:55_VVN|)
                (|ncsubj| |democratically-elect+ed:55_VVN| |Parliament:56_NNJ1| |obj|)
                (|ncmod| _ |Parliament:56_NNJ1| |democratically-elect+ed:55_VVN|)
                (|ncmod| |num| |decision+s:52_NN2| |one:49_MC1|)
                (|ncmod| _ |decision+s:52_NN2| |s:51_ZZ1|)
                (|det| |forum:38_NN1| |what:36_DDQ|)
                (|ncmod| _ |forum:38_NN1| |better:37_JJR|)
                (|ta| |comma| |be+s:30_VBZ| |role:18_NN1|)
                (|ncmod| _ |be+s:30_VBZ| |for:20_IF|)
                (|xcomp| _ |be+s:30_VBZ| |body:33_NN1|)
                (|ncsubj| |be+s:30_VBZ| |supervisory:32_JJ| _)
                (|det| |supervisory:32_JJ| |a:31_AT1|)
                (|dobj| |for:20_IF| |sake:22_NN1|)
                (|det| |sake:22_NN1| |the:21_AT|)
                (|iobj| |sake:22_NN1| |of:23_IO|)
                (|dobj| |of:23_IO| |but:28_CCB|)
                (|conj| |but:28_CCB| |independence:26_NN1|)
                (|conj| |but:28_CCB| |Parliament:29_NNJ1|)
                (|det| |independence:26_NN1| |its:24_APP$|)
                (|ncmod| _ |independence:26_NN1| |own:25_DA|)
                (|det| |role:18_NN1| |this:17_DD1|)
                (|ncmod| |prt| |take:15_VV0| |on:16_RP|)
                (|ncsubj| |be+s:3_VBZ| |Commission:2_NNJ1| _)
                (|ccomp| _ |be+s:3_VBZ| |have:10_VH0|)
                (|ncsubj| |have:10_VH0| |and:6_CC| _)
                (|ncmod| |prt| |ought:8_VMK| |to|)
                (|aux| |have:10_VH0| |ought:8_VMK|)
                (|dobj| |have:10_VH0| |desire:12_NN1|)
                (|det| |desire:12_NN1| |no:11_AT|)
                (|det| |and:6_CC| |the:4_AT|)
                (|conj| |and:6_CC| |executive:5_NN1|)
                (|conj| |and:6_CC| |Parliament:7_NNJ1|)
                (|det| |Commission:2_NNJ1| |The:1_AT|)
                """))

def test_RaspDepParser():
    dp = RaspDepParser()
    sent, dep = TEST_SS4
    parsed = list(dp.parse(dep.split('\n')))
    print (sent)
    pprint(parsed)


def test_RaspDepBuilder():
    dp = RaspDepParser()
    sent, dep = TEST_SS5
    parsed = list(dp.parse(dep.split('\n'), iter((sent,))))
    builder = RaspDepBuilder()
    deplists = builder.build(parsed, (sent,))
    uout = uwriter(sys.stdout)
    for _, deps in deplists:
        for _, d in deps:
            pprint_deprec(d, stream=uout)



def dependencies(stream, parser, sentence_stream=None, keep=None):
    """Parse a Freeling-generated dependency file, and return a map of
    rel -> [record], where record is a (rel, dep, pos, wordn, head) tuple.
    """
    import string

    from itertools import groupby, izip, imap

    fields_re = re.compile(r'^(\d+):( *)[\w-]+/([\w-]+)/\(([^ ]+) ([^ ]+) ([^ ]+) (\d+) (\d+) ?[^ ]\)', re.UNICODE)
    level_re = re.compile(r'^\d+: *\]', re.UNICODE)

    def freeling_extract():
        def make_deprec(depth=-1, head=()):
            for line in (l.rstrip().decode('utf-8') for l in stream):
                fields = fields_re.match(line)
                level = level_re.match(line)
                if fields:
                    sent_id, spaces, rel, word, lemma, pos, beg, end = fields.groups()
                    d = len(spaces) / 2
                    sent_id, beg, end = map(int, (sent_id, beg, end))
                    sentence = tokenized_sentences[sent_id - 1]
                    read_so_far = cumulatives[sent_id - 1]
#                     word_id, _ = util.find(sentence, int(beg) - read_so_far, int(end) - read_so_far)
#                     yield sent_id, deprec(rel, word, lemma, pos, str(word_id), head)
                    yield sent_id, deprec(rel, word, lemma, pos, beg - read_so_far, head)
                    if d > depth:
                        if line[-1] == u'[':  # this is because some ]'s are not there...
#                             for p in make_deprec(p, deprec(rel, word, lemma, pos, str(word_id), head)):
                            for p in make_deprec(d, deprec(rel, word, lemma, pos, beg - read_so_far, head)):
                                yield p
                    elif d < depth:
                        return
                elif level:
                    return
                else:
                    if line != u'' and line[-1] == u'[':
                        print('ignoring line %s' % repr(line), file=sys.stderr)

        # TODO: check tokenization
        def tokenized(sentence):
            return util.split(sentence[:-1])

        def normalized(groups):
            """Make sure the (sent_id, deprecs) iterable has no 'gaps' in the sent_ids.
            """
            n = 1
            for sent_id, deprecs in groups:
                assert sent_id >= n, pformat((sent_id, deprecs))
                if sent_id == n:
                    yield sent_id, deprecs
                else:
                    while sent_id > n:
#                        print >> sys.stderr, 'Filling in', n, sent_id
                        yield n, ()
                        n += 1
                    yield sent_id, deprecs
                n += 1


        ss1, ss2 = tee(sentence_stream)
        tokenized_sentences = map(tokenized, ss1)
        cumulatives = cumulative(ss2)
#         words = OrderedDict()
        by_line_num = normalized(groupby(make_deprec(), lambda (sent_id, r): sent_id))
        for i, (sentence, (sent_id, deprecs)) in enumerate(izip(tokenized_sentences, by_line_num)):
            dr1, dr2 = tee(deprecs)
            assert i + 1 == sent_id, pformat((i + 1, sent_id, sentence, [d for d in deprecs]))
            yield ([(s_id, r.wordn, r.word, r.lemma, r.pos) for s_id, r in dr1],
                   ifilter(lambda r: keep is None or keep(r), dr2))

#    import util
    from itertools import ifilterfalse, tee
    ignore = re.compile(r'Loading|Parsing file|Parsed')

#     def stanford_extract():
#         from parse import PennTree
#         for line in ifilterfalse(ignore.match, stream):
#             if line.startswith('Parsing ['):
#                 sentence = line[2 + line.index(':'):].split()
#             pos_lemma_pairs = PennTree.Parser.parseFile(stream)  # @UndefinedVariable @UnusedVariable
#         pprint(sentence)
#         pprint()

    inparen_re = re.compile(r'\(([^)]+)\)', re.UNICODE)
    ff_re = re.compile(r'([^+_:]+)\+?([\S]+)?:([0-9]+)_(\S+)', re.UNICODE)
    # Example: (|every| |year| |,| |they| |mate| |and| |cubs| |are| |born| |.|) 1 ; (-20.152)
    sent_re = re.compile(r'\|[^|]+\||[^\s()]+')
    header = re.compile(r'\) +-?\d +; +\((-?\d+\.\d+)?\)', re.UNICODE)

    HEADER, GR, BODY, SKIP = 'h', 'g', 'b', 's'
    TOP_HEAD = (u'_', None, u'0', u'-')
    TOP_REL = u'#top#'

    def rasp_extract():
        """Extract dependencies from RASP output.
        Example output: (|xcomp| _ |be+ed:2_VBDZ| |pain:6_NN1|)
        """
        def expand(field):
            match = ff_re.match(field)
            return match.groups() if match else field

        def make_deprec(rel, head, dep, mark=dict()):
            try:
                w = sentence[int(dep[2]) - 1]
            except IndexError:
#                print >> sys.stderr, 'Problem with sentence {0}'.format(sentence)
                w = '?'
            t = (rel, head, dep)
            found, seen = mark.get(t, (None, None))
            if not found:
                h = dependencies.get((head[0], head[2]))
                mark[t] = (found, h)
                found = Deprec(rel, w, dep[0], dep[3], dep[2], () if h == seen else make_deprec(*h, mark=mark))
                mark[t] = (found, h)
            return found

#         def make_deprec2(rel, head, dep, mark=dict()):
#             try:
#                 w = sentence[int(dep[2]) - 1]
#             except IndexError:
# #                print >> sys.stderr, 'Problem with sentence {0}'.format(sentence)
#                 w = '?'
#             t = (rel, head, dep)
#             found, seen = mark.get(t, (None, None))
#             if not found:
#                 print 'looking up', head[0], head[2]
#                 h = dependencies.get((head[0], head[2]))
#                 print 'found', h
#                 mark[t] = (found, h)
#                 found = deprec(rel, w, dep[0], dep[3], dep[2], () if h == seen else make_deprec2(*h, mark=mark))
#                 mark[t] = (found, h)
#             return found

        def deprecords():
            """Second pass through records, adding heads recursively.
            """
            for rel, head, dep in dependencies.values():
                r = make_deprec(rel, head, dep)
                # Let's make sure top-marked relations have a null head
#                 print fdeprec(r)
                assert not(r.rel == TOP_REL and r.head)
                yield r

        def corrections(sentence):
            hole_count = 0
            offsetof = {}
            for i, w in enumerate(sentence):
                offsetof[i + 1] = max(0, i - hole_count)
                hole_count += len(split_re.findall(w)) - 1
            for j in range(hole_count + 1):
                offsetof[i + j + 1] = max(0, i + j - hole_count)
            return offsetof

        def __adjusted_dependencies():
            "Quick fix for dependencies when there is a false token at pos. 1"
            def _m(dep):
                dd = list(dep)
                dd[2] = unicode(int(dd[2]) - 1)
                return tuple(dd)
            def mod((w, d1, d2)):
                return (w, _m(d1), _m(d2))
#            print >> ustderr, 'Adjusting:', sent_id
#            pprint(dependencies, ustderr)
            adjusted = dict(((w, unicode(int(i) - 1)), mod(v)) for (w, i), v in dependencies.items())
#            print >> ustderr, 'adjusted:'
#            pprint(adjusted, ustderr)
            return adjusted

        import codecs
        from split import splitter

        ustderr = codecs.getwriter('utf-8')(sys.stderr)

        state = HEADER
        dependencies = {}
        min_i = sys.maxsize
        sentence = None
        sent_id = 0
        # TODO: check this!!
        split_re = splitter('rasp')
        for _, line in enumerate(l.strip().decode('utf-8') for l in stream):
            if header.findall(line):  # synch on the header
                assert state is HEADER
                _sentence_raw = next(sentence_stream).strip()
                sent_id += 1
                while not _sentence_raw:
                    # There are some gaps every now and then...
                    _sentence_raw = next(sentence_stream).strip()
#                    print >> ustderr, 'Re-read:', _sentence_raw,
                    sent_id += 1
                sentence = string.split(_sentence_raw)
                s1 = [w[1:-1] if w[0] == '|' else w for w in sent_re.findall(line)]
                assert sentence, sent_id
                state = GR
                continue
            elif state is GR:
                assert line.startswith('gr-list') or len(line) == 0, (state, line)
                dependencies = {}
                min_i = sys.maxsize
                state = BODY
                continue
            elif len(line) == 0:
                assert state in (BODY, SKIP, HEADER), (state, line)
                if state is not HEADER:
                    s = sentence[:]
                    offsetof = corrections(s)
#                    if min_i > 1:
# #                        print >> ustderr, 'min_i', min_i
#                        dependencies = __adjusted_dependencies()
#                        min_i = 1
                    for b, i in imap(lambda (b, i): (b, int(i)), dependencies.keys()):
                        try:
                            s[offsetof[i]] = b
                        except KeyError:
                            print(sent_id, file=ustderr)
                            pprint(sentence, ustderr)
                            pprint(offsetof, ustderr)
                            pprint(dependencies, ustderr)
                            raise
                        except IndexError:
                            print(sent_id, ustderr)
                            pprint(sentence, ustderr)
                            pprint(offsetof, ustderr)
                            pprint(dependencies, ustderr)
                            raise
                    deprecs = list(deprecords())
#                     pprint(offsetof)
#                     ss = [(sent_id, offsetof[int(p.wordn)], sentence[offsetof[int(p.wordn)]], p.lemma.lower(), p.pos) for p in deprecs]
                    ss = [(sent_id, int(d.wordn), s1[int(d.wordn) - 1].lower(), d.lemma.lower(), d.pos) for d in deprecs]
#                     pprint(ss)
                    yield (ss, [(sent_id, dep) for dep in deprecs if keep is None or keep(dep)])
                            # TODO: check this
                            # ((sent_id, dep) for dep in deprecs if keep is None or keep(dep)) if status is not SKIP else ())
                    dependencies = {}
                    min_i = sys.maxsize
                    sentence = None
                    state = HEADER
                continue
            assert state in (BODY, SKIP), (state, line)
#            if status in (BODY, SKIP):
            inparen = inparen_re.match(line)
            # Unlikely, but there can be garbage in the input
            if inparen:
                assert inparen, (state, line)
                fields = [e[1:-1] if e[0] == '|' else e for e in inparen.group(1).split()]
#                 pprint(fields)
                deps = map(expand, fields)
#                 pprint(deps)
                rel = deps[0]
                try:
                    head, dep = map(lambda t: (t[0], t[1], int(t[2]), t[3]),
                                    filter(lambda e: type(e) is tuple, deps[1:])[-2:])
                    _, i = b_i = dep[0], dep[2]
                    if i < min_i:
                        min_i = i
                    t = (rel, head, dep)
                    if not b_i in dependencies or dependencies[b_i][0] == TOP_REL:
                        dependencies[b_i] = t
                        hb, hi = head[0], head[2]
                        if hi < min_i:
                            min_i = hi
                        if (hb, hi) not in dependencies:
                            dependencies[(hb, hi)] = (TOP_REL, TOP_HEAD, head)
                    else:
                        state = SKIP
#                         print(u'Skipping {0}'.format(line), file=ustderr)
                except ValueError:
                    pass
#                     print(u'Ignoring {0}'.format(deps), file=ustderr)

    def malt_extract(ruwac=False):
        """Extract relations from Malt's output.
        """
        def groups(tokens):
            # return takewhile(lambda l: l[1] != 'SENT', tokens)
            return takewhile(lambda t: len(t) > 1, tokens)

        parsed = list(MaltDepParser(groups=groups).parse(l.decode('utf-8').rstrip().split('\t') for l in stream))
#         parsed = list(MaltDepParser(groups=groups).parse(l.rstrip().split('\t') for l in stream))
#         pprint(parsed, stream=uwriter(sys.stderr))

#         splitter = split.splitter(parser)
#         ss = [l.rstrip().decode('utf8') for l in sentence_stream]
#         ss = [l.rstrip() for l in sentence_stream]
#         pprint(ss)
#         sentences = list(splitter.findall(s) for s in ss)
#         pprint(sentences)
#         assert len(sentences) == len(parsed), format((sentences, parsed))
#         pprint(parsed)
        builder = MaltDepBuilder()
#         builder = MaltDepBuilderOld()
        return builder.build(parsed, None, keep=keep)


    extract = {'freeling': freeling_extract,
               'rasp': rasp_extract,
               'malt': malt_extract,
               'malt-ru': malt_extract,
               'malt-fa': malt_extract,
#                'stanford': stanford_extract,
               }

    return extract[parser]()


def _main(parser, (process, keep, relations, chunk_size), input_files, output_base):
    """config is a freeling rule file (.dat).
    """
    import codecs
    from glob import iglob
    from os.path import join, splitext
    from util import uopen

    # TODO: not used
    def heads(dep):
        while dep.head:
            yield dep.head
            dep = dep.head

    def index(pred, iterable):
        for i, element in enumerate(iterable):
            if pred(element):
                return i
        raise ValueError('predicate failed: %s' % iterable)

    def to_files(base, sent_in, dep_in, target_out, rels_out):
        """Process a sigle sentence/dependency pair.
        """
        for i, (sent, deps) in enumerate(dependencies(dep_in, parser, sent_in, keep)):
            sentence = [(base + s_id, w_id, w, l, p) for s_id, w_id, w, l, p in sent]
            print(linejoin(tabjoin(unicode(f) for f in w) for w in sentence), file=target_out)
            for sent_id, dep in deps:
                print(tabjoin((str(base + sent_id),) + process(dep)), file=rels_out)
        else:
            print('done {} records ({}, {}).'.format(1 + i, sent[0][0] if sent else '?', int(chunk_size)))
            sys.stdout.flush()


    def _make_relations_single():
        fname = input_files
        print('[{0}] processing {1} for relations ... '.format(parser, fname), end='')
        sys.stdout.flush()
        base_id, base_dir, base_name, source_fname, target_fname = filenames(fname)
        dpfile = uopen(join(base_dir, '%s.dp' % base_name), mode='wb')
        with open(fname) as dep_stream, uopen(source_fname) as sent_stream, uopen(target_fname, 'wb') as target, dpfile:
            to_files(base_id, sent_stream, dep_stream, target, dpfile)

    tabjoin = u'\t'.join
    linejoin = u'\n'.join

    def _make_relations_multiple():
        # Dependency pair files
        with uopen(join(output_base, 'all.dp') , mode='wb') as dpfile:
            for fname in iglob(input_files):
                print('[{0}] processing {1} for relations ...'.format(parser, fname), end='')
                sys.stdout.flush()
                base_id, _, _, source_fname, target_fname = filenames(fname)
                with uopen(fname) as dep_stream, uopen(source_fname) as sent_stream, uopen(target_fname, 'wb') as target:
                    to_files(base_id, sent_stream, dep_stream, target, dpfile)

    def filenames(fname):
        bpath = splitext(fname)[0]
        bdir, bname = split(bpath)
        try:
            base_id = int(bname, 16) * chunk_size
        except ValueError:
            base_id = 0
        return base_id, bdir, bname, u'{}.ss'.format(bpath), u'{}.ss.l'.format(bpath)

    def make_relations():
        return _make_relations_single() if '*' not in input_files else _make_relations_multiple()

    make_relations()


def process_freeling_relation(dep):
    """Answer the two pairs <dependent, head> in base form and lemma form.
    """
    if dep.rel in ('subj', 'dobj'):
        return dep.wordn, dep.head.wordn, dep.rel, dep.lemma, dep.head.lemma
    else:
        v = dep.head.head
        return dep.wordn, v.wordn, dep.rel, dep.lemma, u'{}_{}'.format(v.lemma, dep.head.lemma)

def process_freeling_raw_relation(dep):
    """Answer the two pairs <dependent, head> in base form and lemma form.
    """
    if dep.rel in ('subj', 'dobj'):
        return (dep.wordn, dep.head.wordn, dep.rel,
                dep.word, dep.lemma, dep.head.word, dep.head.lemma)
    else:
        v = dep.head.head
        return (dep.wordn, v.wordn, dep.rel, dep.lemma,
                u'{}_{}'.format(v.word, dep.head.word),
                u'{}_{}'.format(v.lemma, dep.head.lemma))

def process_freeling_plus_relation(dep):
    """Answer the two pairs <dependent, head> in base form and lemma form.
    """
    def tag(dep):
        if dep.pos[0] == 'N': return 'n'
        elif dep.pos[0] == 'V': return 'v'
        elif dep.pos[0] == 'R': return 's'
        elif dep.pos[0] == 'A': return 'a'
        else: return '?FREELING[%s]' % dep.pos

    if dep.rel in ('subj', 'dobj'):
        return (dep.wordn, dep.head.wordn,
                dep.rel,
                (dep.word, tag(dep)), (dep.lemma, tag(dep)),
                (dep.head.word, tag(dep.head)), (dep.head.lemma, tag(dep.head)))
    else:
        v = dep.head.head
        return (dep.wordn, v.wordn,
                dep.rel,
                (dep.word, tag(dep)), (dep.lemma, tag(dep)),
                (v.word, tag(v)), (v.lemma, tag(v)))

bad = re.compile(r'[._#$-]', re.UNICODE)

#def freeling_keep((_, dep)):
def freeling_keep(dep_or_tuple):
    dep = dep_or_tuple[1] if type(dep_or_tuple) == tuple else dep_or_tuple
    if dep.rel in ('subj', 'dobj') and dep.pos[0] == 'N':
        return dep.head.pos[0] == 'V' and not bad.findall(dep.word) and not bad.findall(dep.head.word)
    if dep.rel == 'obj-prep' and dep.pos[0] == 'N' and dep.head.rel == 'cc':
        #assert dep.head.head.pos[0] == 'V'
        return dep.head.head.pos[0] == 'V'
    return False

def process_rasp_relation(dep):
    if dep.rel in ('subj', 'ncsubj', 'obj2'):
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel, dep.lemma, dep.head.lemma)
    elif dep.head.pos[0] == 'I':
        v = dep.head.head
        return (unicode(dep.wordn - 1), unicode(v.wordn - 1),
                dep.rel, dep.lemma, u'{}_{}'.format(v.lemma, dep.head.lemma))
    else:
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel, dep.lemma, dep.head.lemma)

def process_rasp_raw_relation(dep):
    if dep.rel in ('subj', 'ncsubj', 'obj2'):
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel, dep.word, dep.lemma, dep.head.word, dep.head.lemma)
    elif dep.head.pos[0] == 'I':
        v = dep.head.head
        return (unicode(dep.wordn - 1), unicode(v.wordn - 1),
                dep.rel, dep.word, dep.lemma,
                u'{}_{}'.format(v.lemma, dep.head.lemma), u'{}_{}'.format(v.word, dep.head.word))
    else:
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel, dep.word, dep.lemma, dep.head.word, dep.head.lemma)

def process_rasp_plus_relation(dep):
    def tag(dep):
        if dep.pos[0:2] == 'NN': return 'n'
        elif dep.pos[0] == 'V': return 'v'
        elif dep.pos[0] == 'R': return 's'
        elif dep.pos[0] == 'J': return 'a'
        elif dep.pos[0] == 'I': return 'p'
        else: return 'RASP[%s]' % dep.pos

    if dep.head == ():
        return False
    
    if dep.rel in ('subj', 'ncsubj', 'obj2'):
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1), 
                dep.rel,
                (dep.word, tag(dep)), (dep.lemma, tag(dep)),
                (dep.head.word, tag(dep.head)), (dep.head.lemma, tag(dep.head)))
    elif dep.head.pos[0] == 'I':
        v = dep.head.head
        return (unicode(dep.wordn - 1), unicode(v.wordn - 1),
                dep.rel,
                (dep.word, tag(dep)), (dep.lemma, tag(dep)),
                (v.word, tag(v)), (v.lemma, tag(v)))
    else:
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel,
                (dep.word, tag(dep)), (dep.lemma, tag(dep)),
                (dep.head.word, tag(dep.head)), (dep.head.lemma, tag(dep.head)))

def process_malt_plus_relation(dep):
    def tag(pos):
        if pos == 'N': return 'n'
        elif pos == 'V': return 'v'
        elif pos == 'R': return 's'
        elif pos == 'A': return 'a'
        else: return 'MALT[%s]' % pos

    if dep.rel in ('предик', '1-компл'):
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel,
                (dep.lemma, tag(dep.pos)),
                (dep.head.lemma, tag(dep.head.pos)))
    elif dep.head.pos == 'S':
        v = dep.head.head
        return (unicode(dep.wordn - 1), unicode(v.wordn - 1),
                dep.rel,
                (dep.lemma, tag(dep.pos)), (v.lemma, tag(v.pos)))
    else:  # dep and dep.head:
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel,
                (dep.lemma, tag(dep.pos)), (dep.head.lemma, tag(dep.head.pos)))

def process_malt_relation(dep):
#     pprint_deprec(dep, stream=uwriter(sys.stderr))
    subj, dobj = u'предик', u'1-компл'
    if dep.rel in (subj, dobj) and dep.head:
        return unicode(dep.wordn - 1), unicode(dep.head.wordn - 1), dep.rel, dep.lemma, dep.head.lemma
    elif dep.head and dep.head.pos == 'S':
#     elif dep.head.pos == 'S':
        v = dep.head.head
        return unicode(dep.wordn - 1), unicode(v.wordn - 1), dep.rel, dep.lemma, v.lemma
    elif dep and dep.head:
        return unicode(dep.wordn - 1), unicode(dep.head.wordn - 1), dep.rel, dep.lemma, dep.head.lemma
    else:
        pprint_deprec(dep, uwriter(sys.stderr))
        return '???'

# TODO: POS tags are for the Russian MALT only
def process_malt_raw_relation(dep):
    def pos(dep):
        if dep.pos == 'N':
            return 'n'
        elif dep.pos == 'V':
            return 'v'
        elif dep.pos == 'R':
            return 's'
        elif dep.pos == 'A':
            return 'a'
        elif dep.pos == 'S':
            return '_' # SENT, ie the end of sentence
        elif dep.pos == 'P': # proposition?
            return 'p'
        elif dep.pos == 'C': # conjunction?
            return 'c'
        else:
            raise TypeError(u'%s: unknown POS' % pformat_deprec(dep))

#     pprint_deprec(dep, stream=uwriter(sys.stderr))
    subj, dobj = u'предик', u'1-компл'
    if dep.rel in (subj, dobj) and dep.head:
        return (unicode(dep.wordn - 1), unicode(dep.head.wordn - 1),
                dep.rel,
                (dep.word, pos(dep)), (dep.lemma, pos(dep)),
                (dep.head.word, pos(dep.head)), (dep.head.lemma, pos(dep.head)))
    elif dep.head and dep.head.pos == 'S':
#     elif dep.head.pos == 'S':
        v = dep.head.head
        return (unicode(dep.wordn - 1),
                unicode(v.wordn - 1),
                dep.rel,
                (dep.word, pos(dep)), (dep.lemma, pos(dep)),
                (v.word, pos(v)), (v.lemma, pos(v)))
    elif dep and dep.head:
        return (unicode(dep.wordn - 1),
                unicode(dep.head.wordn - 1),
                dep.rel,
                (dep.word, pos(dep)), (dep.lemma, pos(dep)),
                (dep.head.word, pos(dep.head)), (dep.head.lemma, pos(dep.head)))
    else:
        pprint_deprec(dep, uwriter(sys.stderr))
        return '???'

def malt_keep(dep):
    """Should <dep> be kept?
    """
#     pprint_deprec(dep, stream=uwriter(sys.stderr))
#     pprint_deprec(dep)
#     pprint(dep)

    if dep.rel == 'PUNC':
        return False

#     subj, dobj = u'предик', u'1-компл'
#     if dep.rel in (subj, dobj):
#         return dep.pos == 'N' and dep.head.pos == 'V'
#     if dep.rel == dobj and dep.pos == 'N':
    if dep.pos == 'N' and dep.head:
        if dep.head.pos in ('N', 'V'):
            return True
        if dep.head.pos == 'S':
            return dep.head.head and dep.head.head.pos == 'V'
    return False

def rasp_keep(dep):
    if dep.rel in ('subj', 'ncsubj', 'obj2'):
        return (dep.pos[0:2] == 'NN' and dep.head.pos[0] == 'V'
                and not bad.findall(dep.word)
                and not bad.findall(dep.head.word))
    if (dep.rel == 'dobj' and dep.pos[0:2] == 'NN'
        and not bad.findall(dep.word)
        and not bad.findall(dep.head.word)):
        if dep.head.pos[0] == 'V':
            return True
        if dep.head.pos[0] == 'I':
            return dep.head.head and dep.head.head.pos[0] == 'V'
    return False

def rasp_keep2(dep):
    if dep.rel in ('subj', 'ncsubj', 'obj2'):
        return dep.pos[0:2] == 'NN' and dep.head.pos[0] == 'V'
    if dep.rel == 'dobj' and dep.pos[0:2] == 'NN':
        if dep.head.pos[0] == 'V':
            return True
        if dep.head.pos[0] == 'I':
            return dep.head.head and dep.head.head.pos[0] == 'V'
    return False

def rasp_plus_keep(dep):
    if dep.head == () or dep.pos == None or dep.head.pos == None:
        return False
    if dep.rel in ('subj', 'ncsubj', 'obj2', 'ncmod'):
        if dep.pos[0:2] == 'NN':
            return dep.head.pos[0] == 'V' or dep.head.pos[0:2] == 'NN'
        if dep.pos[0] == 'J':
            return dep.head.pos[0:2] == 'NN'
        if dep.pos[0] == 'V':
            return dep.head.pos[0:2] == 'NN'
    if dep.rel == 'dobj' and dep.pos[0:2] == 'NN':
        if dep.head.pos[0] == 'V':
            return True
        if dep.head.pos[0] == 'I':
            return dep.head.head and dep.head.head.pos[0] == 'V'
    return False


config = {'freeling': (process_freeling_relation,
                        freeling_keep,
                        ('subj', 'dobj', 'obj-prep'),
                        1024),
           'freeling+': (process_freeling_plus_relation,
                         freeling_keep,
                         ('subj', 'dobj', 'obj-prep'),
                         1024),
           'rasp': (process_rasp_relation,
                    rasp_keep2,
                    ('subj', 'ncsubj', 'dobj', 'obj2'),
                    4096),
           'rasp+': (process_rasp_plus_relation,
#                     None,
                     rasp_plus_keep,
                     ('subj', 'ncsubj', 'dobj', 'obj2', 'iobj'),
                     4096),
           'malt': (process_malt_relation,
                    malt_keep,
                    ('предик', '1-компл'),
                    4096),
           'malt-ru': (process_malt_relation,
                       malt_keep,
                       ('предик', '1-компл'),
                       4096),
           'malt+': (process_malt_plus_relation,
                     malt_keep,
                     ('предик', '1-компл'),
                     4096),
          }


def test_0():
    ss = ('Entire cities have been hurled into poverty by the housing crisis .',)
    ll = dedent("""\
        (|Entire:1_JB| |city+s:2_NNL2| |have:3_VH0| |be+en:4_VBN| |hurl+ed:5_VVN| |into:6_II| |poverty:7_NN1| |by:8_II| |the:9_AT| |housing:10_NN1| |crisis:11_NN1| |.:12_.|) 1 ; (-20.077)
        gr-list: 1
        (|ncsubj| |hurl+ed:5_VVN| |city+s:2_NNL2| _)
        (|aux| |hurl+ed:5_VVN| |have:3_VH0|)
        (|aux| |hurl+ed:5_VVN| |be+en:4_VBN|)
        (|passive| |hurl+ed:5_VVN|)
        (|iobj| |hurl+ed:5_VVN| |into:6_II|)
        (|dobj| |into:6_II| |poverty:7_NN1|)
        (|ncmod| _ |poverty:7_NN1| |by:8_II|)
        (|dobj| |by:8_II| |crisis:11_NN1|)
        (|det| |crisis:11_NN1| |the:9_AT|)
        (|ncmod| _ |crisis:11_NN1| |housing:10_NN1|)
        (|ncmod| _ |city+s:2_NNL2| |Entire:1_JB|)
        """)
    pprint([(d, list(r)) for d, r in dependencies(StringIO(ll + '\n'), 'rasp', iter(ss), None)])
    pprint([(d, list(r)) for d, r in dependencies(StringIO(ll + '\n'), 'rasp', iter(ss), rasp_plus_keep)])
    pprint([(d, [process_rasp_plus_relation(r) for _, r in rr])
            for d, rr in dependencies(StringIO(ll + '\n'), 'rasp', iter(ss), rasp_plus_keep)])

def test_1():
    ss = ('The housing crisis has hurled entire cities into poverty .',)
    ll = dedent("""\
        (|The:1_AT| |housing:2_NN1| |crisis:3_NN1| |have+s:4_VHZ| |hurl+ed:5_VVN| |entire:6_JB| |city+s:7_NNL2| |into:8_II| |poverty:9_NN1| |.:10_.|) 1 ; (-18.219)
        gr-list: 1
        (|ncsubj| |hurl+ed:5_VVN| |crisis:3_NN1| _)
        (|aux| |hurl+ed:5_VVN| |have+s:4_VHZ|)
        (|iobj| |hurl+ed:5_VVN| |into:8_II|)
        (|dobj| |hurl+ed:5_VVN| |city+s:7_NNL2|)
        (|dobj| |into:8_II| |poverty:9_NN1|)
        (|ncmod| _ |city+s:7_NNL2| |entire:6_JB|)
        (|det| |crisis:3_NN1| |The:1_AT|)
        (|ncmod| _ |crisis:3_NN1| |housing:2_NN1|)
        """)
    pprint([(d, list(r)) for d, r in dependencies(StringIO(ll + '\n'), 'rasp', iter(ss), None)])
    pprint([(d, list(r)) for d, r in dependencies(StringIO(ll + '\n'), 'rasp', iter(ss), rasp_plus_keep)])
    pprint([(d, [process_rasp_plus_relation(r) for _, r in rr])
            for d, rr in dependencies(StringIO(ll + '\n'), 'rasp', iter(ss), rasp_plus_keep)])

def test_2():
    from util import ureader
    ss = ('Бедность как одеялом накрывает континент .',)
    ll = dedent("""\
        1       Бедность        бедность        N       N       Ncfsnn  0       ROOT    _       _
        2       как     как     C       C       C       1       сравнит _       _
        3       одеялом одеяло  N       N       Ncnsin  2       сравн-союзн     _       _
        4       накрывает       накрывать       V       V       Vmip3s-a        5       опред   _       _
        5       континент       континент       N       N       Ncmsnn  3       атриб   _       _
        6       .       .       S       S       SENT    5       PUNC    _       _
        """)
#     pprint([(p, list(r)) for p, r in dependencies(StringIO(ll + '\n'), 'malt', iter(ss), None)])
    pprint([(d, list(r)) for d, r in dependencies(ureader(StringIO(ll + '\n')), 'malt', iter(ss), malt_keep)])
    pprint([(d, [process_malt_relation(r) for _, r in rr])
            for d, rr in dependencies(ureader(StringIO(ll + '\n')), 'malt', iter(ss), malt_keep)])


def main(parser, input_files, output_base):
    _main(parser, config[parser], input_files, output_base)


if __name__ == '__main__':
#     test_2()
    #    parser, input_files, output_base, corpus_id, lang_id, chunk_size = sys.argv[1:]
    parser, input_files, output_base = sys.argv[1:]
    main(parser, input_files, output_base)
