#!/usr/bin/env python
# coding=utf-8

"""Created on Nov 19, 2012
@author: lucag@icsi.berkeley.edu, jhong@ICSI.Berkeley.EDU"""

from __future__ import print_function

import json
import sys
import copy

from argparse import ArgumentParser
from collections import Counter
from depparsing.edeps import JsonDepBuilder
from depparsing.util import Struct, json_dump, dforeach
from itertools import groupby, izip
from pprint import pprint, pformat

from depparsing.parser.util import parserdesc
from edeps import dependencies
from findmet import MetaphorBuilder, read_clusters, extended, tagged
from util import update, uopen, read_seed, N, V, uwriter, ureader, dprint, dpprint
from depparsing.dep2json import parser_for, translate
from textwrap import dedent
from functools import partial
from os.path import splitext
import gzip


METANET_IXSCHEMA = u'https://metaphor.icsi.berkeley.edu/metaphor/ixjschema.json'
JDATA = {'encoding': 'UTF-8',
         'lang': None,
         'jsonschema': METANET_IXSCHEMA,
         'documents': [],
         'sentences': []}


class RelationExtractor(object):
    def __init__(self, **entries):
        update(self, entries)

    # sentences here is actually the content of the 'sentences' key
    def extract(self, sentences):
        pdesc = parserdesc(self.lang)
        process, keep = pdesc.config
        # Patch: the RASP pos is in rpos
        key = Struct(form='form', pos=('rpos' if pdesc.name == 'rasp' else 'pos'), lem='lem')
        recs = []
        for _, deps in JsonDepBuilder(key=key).build(sentences, keep=keep):
            recs.extend([(sid, process(dep)) for sid, dep in deps])
        return recs


def build_extractor(lang):
    """Builds an extractor that optionally calls a parser.

    :param lang: one of 'en', 'es', 'ru'.
    :param invoke_parser: whether or not we have to actually extract input.
    """
    return RelationExtractor(lang=lang, encoding='utf-8')

# Some useful join shortcuts
spj = u' '.join     # by spaces
nlj = u'\n'.join    # by newlines
j = ''.join         # by nothings


def extract(json_in, lang, invoke_parser=False):
    """Extract all the relations from the sentences in the JSON input,
    optionally parsing sentences in the given language <lang>.

    :param json_in
    :param lang: one of 'en', 'es', 'ru'.
    :returns: a pair <relations, json-output>, where relations contains all the relations in the input sentences.
    """

    from depparsing.parser.util import WordTokenizer
    _tokenize = WordTokenizer().tokenize
    _j = u' '.join

    def ctext(s):
        def tokenized(s):
            return  _j(_tokenize(s['text']))
        return tokenized(s)

    sentences = json_in['sentences']
    if invoke_parser:
        # Let's try to do it efficiently
        parser = parser_for(lang)
        ss = [ctext(s) for s in sentences]
        raw_deps = parser.parse(ss, translate=None) # do not translate to JSON, we'll do it later
        process, keep, = parser.config
        dep_list = list(dependencies(iter(raw_deps), parser.name, iter(ss), keep=keep))
        relations = [(sid, process(dep)) for _, deps in dep_list for sid, dep in deps]
        json_out = translate(raw_deps, ss, base=0, parser=parser.name, process=process, keep=keep)
        # TODO: this is not efficient
        for o, i in izip(json_out['sentences'], json_in['sentences']):
            o['text'] = i['text']
    else:
        relations = build_extractor(lang).extract(sentences)
        json_out = copy.deepcopy(json_in)
    return relations, json_out


def cluster(lang):
    from findmet import cluster
    return cluster[lang]

uerr = uwriter(sys.stderr)

def dump((n, v), indent=0, stream=uerr):
    """Dump a relation onto <stream>.
    """
    dprint(u' ' * indent, u'{0[0]}.{0[1]} {1[0]}.{1[1]}'.format(n, v))


class MetaphorFinderEx(object):
    """Metaphor finder. Efficient version.
    """
    def __init__(self, lang, seed_fname, extend_seeds):
        def tag_ext(pos): return lambda words: extended(tagged(words, pos))
        def tag(pos): return lambda words: tagged(words, pos)
        noun_fn, verb_fn = cluster(lang)
        with uopen(seed_fname) as lines:
            seeds = read_seed(l.rstrip().split() for l in lines)
        op = tag_ext if extend_seeds else tag
        with uopen(noun_fn) as nlines, uopen(verb_fn) as vlines:
            nclusters = read_clusters((l.rstrip().split() for l in nlines), op(N))
            vclusters = read_clusters((l.rstrip().split() for l in vlines), op(V))
        update(self, mbuilder=MetaphorBuilder(lang, nclusters, vclusters, seeds))

    def find(self, relations):
        """Find metaphors in relations.

        :param ralations: a list of triple: <relation, seed-pair, metaphor-pair>,
            where each pair is a <noun, verb> pair.
        """
        metaphors = self.mbuilder.find(relations)
        return [(rel, (sn, sv), (n, v)) for n, v, rel, sn, sv in metaphors]


# Record types: ours to the parser's
rtype = {'en': {'verb-subject': 'ncsubj',
                'verb-object': 'dobj'},
         'es': {'verb-subject': 'subj',
                'verb-object': 'dobj'},
         'ru': {'verb-subject': u'предик',
                'verb-object': u'1-компл'}}



def m4detect(lang, json_in, seed_fn, invoke_parser=False, extend_seeds=False, **kw):
    """Metaphor detection using the seed system.

    :param lang: language (one of 'en', 'es', 'ru', 'fa')
    :param json_in: the json document object (a dict) containing at least a 'sentences' key
    :param seed_fn: a list of seeds
    :param invoke_parser: invoke parser on the sentences in the json doc
    :param extended_seeds: whether or not try to extend seeds (English only)
    :returrns: a json_in with a list of the found LMs appended to each sentence
    """
    relations, json_out = extract(json_in, lang, invoke_parser)
    
    def counted(relation):
        return Counter((noun, verb) for rel, noun, verb in dependencies if rel == relation)

    tokenizer = parserdesc(lang).tokenizer

    def lm(sentence, relation, seed, noun_l, verb_l):
        """Outputs a LM with all the required keys.
        """
        def offset(lemma, idx):
            "Finds offest of <lemma> in sentence."
            words = tokenizer(sentence)
            try:
                w = words[idx]
                word = w[0] if len(w) == 2 else w
                start = sentence.find(word)
                return dict(start=start, end= start + len(word))
            except IndexError:
                dprint(u'Problem finding offset of', lemma, 'at', idx, 'in:')
                dpprint((idx, words))
                return dict(start=-1, end=-1)

        def dom(word, rel):
            return dict(offset(word.form, word.idx),
                        lpos=u'{0[0]}.{0[1]}'.format(word.lemma),
                        lemma=word.lemma[0],
                        form=word.form[0],
                        rel=rel)

        n_rel, v_rel = relation.split('-')
        noun, verb = rels[noun_l, verb_l]
        dprint('lm:', '\n  noun', noun, '\n  verb', verb)
        return dict(name=u'{0[0]} {1[0]}'.format(noun.lemma, verb.lemma),
                    target=dom(noun, n_rel),
                    source=dom(verb, v_rel),
                    seed=u' '.join(u'%s.%s' % s for s in seed))

    # TODO: optimization: this should be created once at the beginning. Perhaps on import?
    mfinder = MetaphorFinderEx(lang, seed_fn, extend_seeds)

    # TODO: this is inefficient: Python will evaluate arguments anyway
#     dprint('All possible metaphors:')
#     dforeach(partial(dump, indent=1), sorted(mfinder.mbuilder.metaphors))

    # relations grouped by sentence id
    depsbysent = groupby(relations, key=lambda (sent_id, _): sent_id)
    sentences = json_out['sentences']
    for i, deps in ((i - 1, list(deps)) for i, deps in depsbysent):
        # index deps by <noun-lemma, verb-lemma> pairs
        rels = dict(((n_l, v_l), (Struct(lemma=n_l, form=n_f, idx=int(n_idx)),
                                  Struct(lemma=v_l, form=v_f, idx=int(v_idx))))
                    for _, (n_idx, v_idx, _, n_f, n_l, v_f, v_l) in deps)
        mets = mfinder.find(rels.keys())
        sent = sentences[i]
        dprint('_' * 96, '\n', sent['text'])
        dforeach(partial(dump, indent=1), rels.keys())
        lms = [lm(sent['text'], rel, seed, noun_l, verb_l) for (rel, seed, (noun_l, verb_l)) in mets]
        dprint('found LMs:', pformat(lms))
        sent['lms'] = lms

    jsonout = dict((k, v) for k, v in json_in.items() if k != 'sentences')
    jsonout['sentences'] = sentences
    return jsonout


def all_metaphors(lang, seed_fn, extend_seeds, **_):
    mfinder = MetaphorFinderEx(lang, seed_fn, extend_seeds)
    return mfinder.mbuilder.metaphors

def argparser():
    description = dedent("""\
        Parse a Metanet JSON document (according to {}) and search for LMs.\
        """.format(METANET_IXSCHEMA))
    p = ArgumentParser(description=description)
    p.add_argument('-j', dest='json_fn', required=False, metavar='<filename>',
                   help='Input JSON document')
    p.add_argument('-l', dest='lang', choices=['en', 'es', 'ru'], required=True, metavar='<language>',
                   help='Input language')
    p.add_argument('-x', dest='extend_seeds', action='store_true',
                   help='Use experimental metaphor finder (only with English)')
    p.add_argument('-p', dest='invoke_parser', action='store_true',
                   help='Invoke parser on input')
    p.add_argument('-s', dest='seed_fn', required=True, metavar='<seed-filename>',
                   help='Seed file name')
    p.add_argument('-o', dest='out_fn', required=False, default='-', metavar='<filename>',
                   help='Output file name')
    p.add_argument('-m', dest='debug_meta', action='store_true',
                   help='Debug metaphors: output stored metaphors (language and seed file needed)')
#     p.add_argument('-d', dest='debug', action='store_true',
#                    help='Print debug output')
    return p

def open_file(fn):
    _, ext = splitext(fn)
    return ureader(gzip.open(fn)) if ext == '.gz' else uopen(fn)

def main(args):
    if args.debug_meta:
        entries = args.__dict__
        print('Metaphors for language {lang}, seed file {seed_fn}:'.format(**entries))
        for n, v in all_metaphors(**entries):
            print(u'{0[0]}.{0[1]} {1[0]}.{1[1]}'.format(n, v), file=uwriter(sys.stdout))
    else:
        with open_file(args.json_fn) as jsonf:
            json_out = m4detect(json_in=json.load(fp=jsonf, encoding='utf-8'), **args.__dict__)
            if args.out_fn == '-':
                json_dump(obj=json_out, fp=uwriter(sys.stdout))
            else:
                with uopen(args.out_fn, mode='w+b') as out_f:
                    json_dump(obj=json_out, fp=out_f)


if __name__ == '__main__':
    main(argparser().parse_args())

