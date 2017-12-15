# -*- coding: UTF-8 -*-

"""
.. module:: dep2json
    :platform: Unix
    :synopsis: Translation from a dependency parse to the internal JSON format.

Translation from a dependency parse to the internal JSON format. Three formats
are supported: RASP (English), Freeling (Spanish), and Malt (Russian and Farsi).
Created on Oct 18, 2013.

.. moduleauthor:: Luca Gilardi <lucag@icsi.berkeley.edu>

"""

from __future__ import print_function

from argparse import ArgumentParser
from collections import namedtuple
from functools import partial
from functools import reduce
from itertools import starmap
from json import load, dump
from pprint import pprint, pformat
from string import split
from subprocess import check_output
from tempfile import NamedTemporaryFile
from textwrap import dedent
import sys, logging

from depparsing.edeps import RaspDepParser, RaspDepBuilder
from depparsing.parser.freeling.util import to_nodelist
from depparsing.parser.malt.util import ConllxRecord
from depparsing.parser.util import parserdesc, sanitized
from depparsing.util import dpprint, blocks, lines
from edeps import dependencies
from util import uopen, uwriter, ureader, cumulative
from util import update, dprint
METANET_IXSCHEMA = u'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json'
JDATA = {'encoding': 'UTF-8',
         'lang': None,
         'jsonschema': METANET_IXSCHEMA,
         'documents': [],
         'sentences': []}

uout, uerr = map(uwriter, (sys.stdout, sys.stderr))


class Translator(object):

    """Base class for Translator objects, used to translate a dependency parse into
    the internal JSON format.
    """

    def __init__(self, **kw):
        update(self, kw)


class FreelingTranslator(Translator):

    """A Translator for Freeling dependency trees
    """

    def translate(self, deps, sents, process, keep):
        """Translate a dependency parse into JSON.

        :param deps:    a list of dependency trees.
        :param sents:   the sentences that generated the dependency trees.
        :param process: a function to process a single dependency tree.
        :param keep:    a predicate function: invoked on a deprec element to determine
                        whether to keep that record or not.
        :returns:       the complete JSON representation on the deprec list.

        """
#         deps = [d.decode('utf-8') for d in deps]
        sentences = []
        documents = []
        for i, (sent, deps) in enumerate(dependencies(iter(deps), self.parser, iter(sents))):
            sentence = sorted(((self.base + s_id, w_beg, w, l, p) for s_id, w_beg, w, l, p in sent), key=lambda e: e[1])
            word_id = dict((w_beg, i) for i, (_, w_beg, _, _, _) in enumerate(sentence))
            deps = list(deps)
            wdeps = [{'type': d.rel,
                      'dep': word_id[d.wordn],
                      'head': (word_id[d.head.wordn] + 1) if len(d.head) else 0}
                     for _, d in deps]
            words = [{'idx': word_id[d.wordn],
                      'form': d.word,
                      'n': word_id[d.wordn] + 1,
                      'lem': d.lemma,
                      'pos': d.pos,
                      'start': d.wordn,
                      'end': d.wordn + len(d.word),
                      'dep': {'type': d.rel,
                              'head': (word_id[d.head.wordn] + 1) if len(d.head) else 0}}
                     for _, d in deps]
            sentences.append({'idx': self.base + i,
                              'ctext': u' '.join(w for _, _, w, _, _ in sentence),
                              'word': words,
                              'dparse': wdeps,
                              '%s' % self.parser: {'word': words,
                                                   'relations': [process(d) for _, d in deps if keep(d)]}})

        return dict(JDATA, lang=self.lang, sentences=sentences, documents=documents)


class MaltTranslator(Translator):

    """A Translator for Malt dependency trees.
    """

    def translate(self, deps, sents, process, keep):
        """Translate a dependency parse into JSON.

        :param deps: a list of deprec dependency trees.
        :param sents: the sentences that generated the dependency trees.
        :param process: a function to process a single dependency tree.
        :param keep: a predicate function: invoked on a deprec element to determine
            whether to keep that record or not.
        :returns: the complete JSON representation on the deprec list.

        """
        # Make sure all the dependences are in Unicode
#         deps = [d.decode('utf8') for d in deps]

        sentences = []
        documents = []

        def start(idx):
            i = idx - 1
            try:
                return ss.index(ctext[i])
            except ValueError:
                dprint(u"can't find {}-th '{}' in '{}'".format(i, ctext[i], ss))
                return -1

        def end(idx):
            i = idx - 1
            try:
                return ss.index(ctext[i]) + len(ctext[i])
            except ValueError:
                dprint(u"can't find {}-th '{}' in '{}'".format(i, ctext[i], ss))
                return -1

        for i, ((sent, deps), ss) in enumerate(zip(dependencies(iter(deps), self.parser, iter(sents)), sents)):
            # TODO: remove? this isn't really needed
            sentence = sorted(((self.base + s_id, int(rank), form, lemma, pos)
                               for s_id, rank, form, lemma, pos in sent),
                              key=lambda e: e[1])
#             word_id = dict((rank, i) for i, (_, rank, _, _, _) in enumerate(sentence))
            ctext = [form for _, _, form, _, _ in sentence]
#             dprint('tran', u' '.join(ctext))
#             deps = list(deps)
#             dpprint(deps)

            wdeps = [{'type': d.rel,
                      'dep': d.wordn,
                      'head': d.head.wordn if len(d.head) else 0} for _, d in deps]
            words = [{'idx': d.wordn - 1,
                      'form': d.word, 'n': d.wordn, 'lem': d.lemma, 'pos': d.pos,
                      'start': start(d.wordn), 'end': end(d.wordn),
                      'dep': {'type': d.rel,
                              'head': d.head.wordn if len(d.head) else 0}}
                     for _, d in deps]
            words2 = [{'idx': d.wordn - 1,
                       'form': d.word, 'n': d.wordn, 'lem': d.lemma, 'pos': d.pos,
                       'start': start(d.wordn), 'end': end(d.wordn),
                       'dep': {'type': d.rel,
                               'head': d.head.wordn if len(d.head) else 0}}
                      for _, d in deps]
            sentences.append({'idx': self.base + i,
                              'dparse': wdeps,
                              'word': words,
                              'ctext': u' '.join(ctext),
                              '%s' % self.parser: {'word': words2,
                                                   'relations': [process(d) for _, d in deps if keep(d)]}})
            
        return dict(JDATA, lang=self.lang, sentences=sentences, documents=documents)


class RaspTranslator(Translator):

    """A Translator for RASP dependency trees.
    """

    def translate(self, deps, sents, process, keep):
        """Translate a dependency parse into JSON.

        :param deps: a list of deprec dependency trees.
        :param sents: the sentences that generated the dependency trees.
        :param process: a function to process a single dependency tree.
        :param keep: a predicate function: invoked on a deprec element to determine
            whether to keep that record or not.
        :returns: the complete JSON representation on the deprec list.

        """
        dp = RaspDepParser()
#         dpprint(sents)
#         dpprint(deps)
        parsed = list(dp.parse(deps, iter(sents)))
#         parsed = list(dp.parse(deps))
        builder = RaspDepBuilder()
        deplists = list(builder.build(parsed, sents))
#         dpprint(deplists)

        sentences = []
        documents = []
        
        def start(idx):
            i = idx - 1
            try:
                return ss.index(ctext[i])
            except ValueError:
                dprint(u"can't find {}-th '{}' in '{}'".format(i, ctext[i], ss))
                return -1

        def end(idx):
            i = idx - 1
            try:
                return ss.index(ctext[i]) + len(ctext[i])
            except ValueError:
                dprint(u"can't find {}-th '{}' in '{}'".format(i, ctext[i], ss))
                return -1


        for i, ((sent, deps, _), ss) in enumerate(zip(deplists, sents)):
            sentence = sorted(((self.base + s_id, wordn, w, l, p) for s_id, wordn, w, l, p in sent), key=lambda e: e[1])
            ctext = [w for _, _, w, _, _ in sentence]
            starts = cumulative(ctext)
#             dprint(ctext)
#             pprint(sentence)
#             pprint(word_id)
#             pprint(alldeps)
            deps = list(d for _, d in deps)  # XXX
            wdeps = [{'type': d.rel,
                      'dep': d.wordn - 1,
                      'head': d.head.wordn if len(d.head) else 0} for d in deps]
            words = [{'idx': d.wordn - 1,
                      'form': d.word,
                      'n': d.wordn,
                      'lem': d.lemma,
                      'pos': d.pos,
                      'rpos': d.pos, 
                      'start': start(d.wordn - 1),
                      'end': end(d.wordn - 1),
                      'dep': {'type': d.rel,
                              'head': d.head.wordn if len(d.head) else 0}} for d in deps]
            words2 = [{'idx': d.wordn - 1,
                       'form': d.word,
                       'n': d.wordn,
                       'lem': d.lemma,
                       'pos': d.pos,
                       'start': start(d.wordn - 1),
                       'end': end(d.wordn - 1),
                       'dep': {'type': d.rel,
                               'head': (d.head.wordn - 1) if len(d.head) else 0}} for d in deps]
            sentences.append({'idx': self.base + i,
                              'ctext': u' '.join(ctext),
                              'dparse': wdeps,
                              'word': words,
                              '%s' % self.parser: {'word': words2,
                                                   #'deptree': deps,
                                                   #'deps': alldeps,
                                                   'relations': [process(d) for d in deps if keep(d)],
                                                   'starts': starts}})
        return dict(JDATA, lang=self.lang, sentences=sentences, documents=documents)


class Parser(object):

    """A parser object, used to invoke specific parser porcesses.
     Returns a pair <sentence, list<relation>>.
    """

    def __init__(self, **kw):
        """:param **kw: it assumes the following keys: command, Translator.
        """
        update(self, kw, debug=kw['debug'] if 'debug' in kw else False)

    def parse(self, sentences, translate):
        """Parse a list of sentences.

        :param sentences: a sequence of strings.
        :returns: A list of dependency trees (a forest)
        """
        def tmpfile(prefix):
            return NamedTemporaryFile(dir='.', delete=False, prefix=prefix) if self.debug else NamedTemporaryFile(prefix=prefix)

        with uwriter(tmpfile('in-')) as infile, uwriter(tmpfile('err-')) as errfile:
            infile.writelines(u'\n'.join(sanitized(s) for s in sentences))
            infile.seek(0)
            dependencies = check_output(self.command, stdin=infile, stderr=errfile).split('\n')
            process, keep = self.config
#             dpprint(dependencies)
            if translate:
                return translate(dependencies, sentences, base=0, parser=self.name, process=process, keep=keep)
            else:
                return dependencies


def parser_for(lang):
    """Create a Parser object for a specific language.

    :param lang: one of 'en', 'es', 'ru', 'fa'.
    :returns: a Parser object.
    """
    pdesc = parserdesc(lang)
    return Parser(name=pdesc.name, config=pdesc.config, command=pdesc.command, debug=True, encoding='utf-8')


def translate(deps, sents, base, parser, process, keep):
    """Translate a dependency tree list into the internal JSON format.

    :param deps: a list of dependency trees.
    :param sents: the input sentences.
    :param base: an integer (used for parallel parsing).
    :param parser: a Parser object.
    :param process: a function to process a single dependency tree.
    :param keep: a predicate function, invoked on a deprec element to determine
        whether to keep that record or not.
    """
    txtor = {'freeling': FreelingTranslator(lang='es', parser=parser, base=base),
             'rasp': RaspTranslator(lang='en', parser=parser, base=base),
             'malt-es': MaltTranslator(lang='es', parser=parser, base=base),
             'malt-ru': MaltTranslator(lang='ru', parser=parser, base=base),
             'malt-fa': MaltTranslator(lang='fa', parser=parser, base=base), }
    return txtor[parser].translate(deps, sents, process, keep)


def parse(lang, sentences, translate=translate):
    """Parse sentence in a specific language.

    :param lang: one of 'en', 'es', 'ru', 'fa'.
    :param sentences: a sequence of sentences.
    :param translate: apply translate to the list of dependency trees
    :returns: a string contaning a list of dependency trees, one for each
        input sentence.

    """
    return parser_for(lang).parse(sentences, translate)


def getopt(args, opt, default):
    return default if opt not in args else args[args.index(opt) + 1]


def to_dict(keygen, ns):
    """Apply keygen to block.
    """
    return dict((k, f(ns)) for k, f in keygen.iteritems())

# _____________________________________________________________________
# Freeling stuff
#
# These are the keys that are to be created in the JSON object.
# All the ns arguments are list of `Node`s.
FREELING_KEYGEN = dict(id=lambda ns: int(ns[0].sent_id),
                       idx=lambda ns: int(ns[0].sent_id) - 1,
                       ctext=lambda ns: u' '.join(n.word for n in ns),
                       text=lambda ns: u' '.join(n.word for n in ns),
                       word=lambda ns: [dict(idx=n.n - 1,
                                             n=n.n,
                                             form=n.word,
                                             lem=n.lemma,
                                             pos=n.pos,
                                             start=n.beg,
                                             end=n.end,
                                             dep=dict(type=n.rel, head=n.parent.n)) for n in ns])


def combine_freeling(js, block):
    js.append(to_dict(FREELING_KEYGEN, to_nodelist(block)))
    return js

# _____________________________________________________________________
# Conll-X
#
CONLLX_KEYGEN = dict(id=lambda _: 1,
                     idx=lambda _: 0,
                     ctext=lambda ns: u' '.join(n.form for n in ns),
                     text=lambda ns: u' '.join(n.form for n in ns),
                     word=lambda ns: [dict(idx=int(n.id) - 1,
                                           n=int(n.id),
                                           form=n.form,
                                           lem=n.lemma,
                                           pos=n.postag,
                                           start=-1,
                                           end=-1,
                                           dep=dict(type=n.deprel, head=int(n.head))) for n in ns])


def combine_conllx(js, block):
    j = to_dict(CONLLX_KEYGEN, list(starmap(ConllxRecord, block)))
    l = len(js)
    j.update(id=l + 1, idx=l)
    j.update(lms=[]) # to keep the viewer happy
    js.append(j)
    return js


# TODO: rename to something more sensible.
def to_json(combine, blocks):
    """Returns a list of 'sentence' elements.
    """
    return reduce(combine, blocks, [])


def test_freeling_to_json():
    u"""
    >>> import sys
    >>> from pprint import pprint
    >>> from depparsing.util import uwriter
    >>> pprint(test_freeling_to_json(), stream=uwriter(sys.stdout))
    [{'ctext': u'Monopolios chupan dinero .',
      'id': 1,
      'idx': 0,
      'word': [{'dep': {'head': 2, 'type': u'subj'},
                'end': u'10',
                'form': u'Monopolios',
                'idx': 0,
                'lem': u'monopolio',
                'n': 1,
                'pos': u'NCMP000',
                'start': u'0'},
               {'dep': {'head': 0, 'type': u'top'},
                'end': u'17',
                'form': u'chupan',
                'idx': 1,
                'lem': u'chupar',
                'n': 2,
                'pos': u'VMIP3P0',
                'start': u'11'},
               {'dep': {'head': 2, 'type': u'dobj'},
                'end': u'24',
                'form': u'dinero',
                'idx': 2,
                'lem': u'dinero',
                'n': 3,
                'pos': u'NCMS000',
                'start': u'18'},
               {'dep': {'head': 2, 'type': u'term'},
                'end': u'25',
                'form': u'.',
                'idx': 3,
                'lem': u'.',
                'n': 4,
                'pos': u'Fp',
                'start': u'24'}]},
     {'ctext': u'El dinero corrompe , no tiene salida .',
      'id': 3,
      'idx': 2,
      'word': [{'dep': {'head': 2, 'type': u'espec'},
                'end': u'85',
                'form': u'El',
                'idx': 0,
                'lem': u'el',
                'n': 1,
                'pos': u'DA0MS0',
                'start': u'83'},
               {'dep': {'head': 3, 'type': u'subj'},
                'end': u'92',
                'form': u'dinero',
                'idx': 1,
                'lem': u'dinero',
                'n': 2,
                'pos': u'NCMS000',
                'start': u'86'},
               {'dep': {'head': 0, 'type': u'top'},
                'end': u'101',
                'form': u'corrompe',
                'idx': 2,
                'lem': u'corromper',
                'n': 3,
                'pos': u'VMIP3S0',
                'start': u'93'},
               {'dep': {'head': 3, 'type': u'term'},
                'end': u'102',
                'form': u',',
                'idx': 3,
                'lem': u',',
                'n': 4,
                'pos': u'Fc',
                'start': u'101'},
               {'dep': {'head': 6, 'type': u'espec'},
                'end': u'105',
                'form': u'no',
                'idx': 4,
                'lem': u'no',
                'n': 5,
                'pos': u'RN',
                'start': u'103'},
               {'dep': {'head': 3, 'type': u'modnomatch'},
                'end': u'111',
                'form': u'tiene',
                'idx': 5,
                'lem': u'tener',
                'n': 6,
                'pos': u'VMIP3S0',
                'start': u'106'},
               {'dep': {'head': 6, 'type': u'dobj'},
                'end': u'118',
                'form': u'salida',
                'idx': 6,
                'lem': u'salida',
                'n': 7,
                'pos': u'NCFS000',
                'start': u'112'},
               {'dep': {'head': 6, 'type': u'term'},
                'end': u'119',
                'form': u'.',
                'idx': 7,
                'lem': u'.',
                'n': 8,
                'pos': u'Fp',
                'start': u'118'}]}]
        """
    s = split(dedent(u"""\
        1:grup-verb/top/(chupan chupar VMIP3P0 11 17 -) [
        1:  sn/subj/(Monopolios monopolio NCMP000 0 10 -)
        1:  sn/dobj/(dinero dinero NCMS000 18 24 -)
        1:  F-term/term/(. . Fp 24 25 -)
        1:]
        
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
    return to_json(combine_freeling, list(blocks(lambda l: len(l) > 0, s)))


def test():
    pprint(test_freeling_to_json())


def main(args):
    """Main program.
    """
    lang = args.lang
    uout = uwriter(sys.stdout)

    def openf(fn):
        return uopen(fn) if fn != '-' else ureader(sys.stdin)

    def output(json_doc):
        """Write our JSON file out in a 'standard' way.
        """
        dump(json_doc, uout, encoding='utf-8', sort_keys=True, indent=2, ensure_ascii=False, separators=(',', ': '))

    def process_conllx(args):
        sin = openf(args.conllx_fn)
        json_out = dict(JDATA)
        json_out.update(sentences=to_json(combine_conllx, blocks(lambda r: len(r) > 1, lines(sin, u'\t'))))
        output(json_out)

    def process_json(args):
        sin = openf(args.json_fn)
        json_in = load(fp=sin, encoding='utf-8')
        sentences_in = json_in['sentences']
        try:
            json_out = parse(lang, [sanitized(s['ctext']) for s in sentences_in])
        except KeyError:
            #         from nltk.tokenize import TreebankWordTokenizer
            #         _tokenize = TreebankWordTokenizer().tokenize
            _j = u' '.join

            def make_ctext(s): # this has side effects
                ctext = sanitized(s['text'])
                s['ctext'] = ctext
                return ctext
            json_out = parse(lang, [make_ctext(s) for s in sentences_in])

        json_out.update((k, v) for k, v in json_in.items() if k != 'sentences')
        # Sanity check: verify we haven't modified ctext
        if False:
            for idx, (sent_in, sent_out) in enumerate(zip(json_in['sentences'], json_out['sentences']), start=1):
                ctext_in, ctext_out = sent_in['ctext'], sent_out['ctext']
                try:
                    assert ctext_in == ctext_out
                except AssertionError:
                    dprint(u'error at line {}:\n  {}  \n!=\n  {}'.format(idx, ctext_in, ctext_out))

        output(json_out)

    if args.test:
        import doctest
        doctest.testmod()
#   elif args.freeling_fn:
#       process_freeling(args)
    elif args.conllx_fn:
        process_conllx(args)
    else:
        process_json(args)


def argparser():
    p = ArgumentParser(description='Parse sentences in a JSON file')
    p.add_argument('-j', dest='json_fn', default='-', metavar='<filename>',
                   help='JSON input file name (read from <stdin> if not given)')
    p.add_argument('-d', dest='conllx_fn', metavar='<filename>',
                   help='Dependency input file name (Conll-X format)')
    p.add_argument('-l', dest='lang', required=True, choices=['en', 'es', 'fa', 'ru'],
                   help='Language')
    p.add_argument('-t', dest='test', action='store_true',
                   help='Run tests')
    return p

if __name__ == '__main__':
    main(argparser().parse_args())


def test_1():
    parser, base, depn, sentn = sys.argv[1:5]
    # with uopen(depn) as depf, uopen(sentn) as sentf:
    with open(depn) as depf, uopen(sentn) as sentf:
        deps = [l.rstrip() for l in depf]
        sents = [l.rstrip() for l in sentf]
        dump(translate(deps, sents, int(base), parser, None, None), uout, ensure_ascii=False, encoding='utf-8', indent=2)
