# Encoding: UTF-8

"""Created on Jul 1, 2014; @author: lucag
"""

import sys

from depparsing.edeps import  process_malt_raw_relation, process_rasp_plus_relation, process_freeling_plus_relation
from depparsing.edeps import  process_rasp_raw_relation, rasp_plus_keep, malt_keep
from depparsing.edeps import freeling_keep, process_freeling_raw_relation
from depparsing.split import tokenizer
from depparsing.util import Environment, Struct
from pprint import pprint


# The configuration environment
config = Environment({'TOOLS': '/u/metanet/tools',
                      'RU_TOOLS': '/u/metanet/corpolexica/RU/parsers/tools/parser',
                      'FA_TOOLS': '/u/metanet/nlptools/maltparser-1.7.2',
                      'TMP': '/tmp/parsemet',
                      'SEED_DIR': '/u/metanet/extraction/seeds'})

# A map from <lang> to the parser name and the rules needed to extract relations
_parser_desc = {'es': ('freeling', (process_freeling_plus_relation, freeling_keep)),
#                 'en': ('rasp', (process_rasp_raw_relation, rasp_plus_keep)),
                'en': ('rasp', (process_rasp_plus_relation, rasp_plus_keep)),
                'ru': ('malt-ru', (process_malt_raw_relation, malt_keep)),
                'fa': ('malt-fa', (process_malt_raw_relation, malt_keep))}


# Command lines and arguments for starting different parsers
_command = {'rasp':
                config(['{TOOLS}/rasp3os/scripts/rasp.sh', '-m']),
            'freeling':
                #config(['{TOOLS}/bin/analyzer', '--nec', '-f', '{TOOLS}/etc/dep.cfg']),
                config(['{TOOLS}/freeling-3.1/bin/analyzer', '--nec', '-f', '{TOOLS}/etc/dep.es.cfg']),
            'malt-ru':
                config(['{RU_TOOLS}/russian-malt-alt.sh']),
            'malt-fa':
                config(['{FA_TOOLS}/persian-malt.sh'])}

def parserdesc(lang):
    name, config = _parser_desc[lang]
    command = _command[name]
    return Struct(name=name, config=config, command=command, tokenizer=tokenizer(name))


def sanitized(line):
    """Clean all lines in iterable it, removing some Unicode characters.
    Adds a terminator if it's not there. Inefficient.
    """
    line = line[:]

    line = line.replace(u"’", u"'")
    line = line.replace(u'“', u'"')
    line = line.replace(u'”', u'"')
    line = line.replace(u'\xab', u'"')
    line = line.replace(u'\xbb', u'"')

    # Soft hyphen
    line = line.replace(u'\xad', u'')

    # Newline...
    line = line.replace(u'\n', u' ')

    # Graphical characters
    line = line.replace(u'\xb4', u"'")
    line = line.replace(u'\xb7', u'-')

    # Em and en dashes
    line = line.replace(u'\u2011', u"-")
    line = line.replace(u'\u2013', u'-')
    line = line.replace(u'\u2014', u'-')

    line = line.replace(u'\u2018', u"'")
    line = line.replace(u'\u2019', u"'")
    line = line.replace(u'\u2022', u"-")
    line = line.replace(u'\u2212', u'-')
    line = line.replace(u'\u2032', u"'")
#     line = line.replace(u'\u2026', u'...')
    # XXX: Replacing '...' with ellipsis and 2 spaces to preserve length
    line = line.replace(u'...', u' \u2026 ')
    line = line.replace(u'\u2028', u' ')
    line = line.replace(u'\u2029', u' ')

#     if len(line) == 0 or line[-1] not in (u'.', u'?', u'!'):
#         line += u'.'

    return line

# Keep this around for a while
# _parser = {'en': Parser(name='rasp',
#                         config=config['rasp+'],
#                         command=expand(['{TOOLS}/rasp3os/scripts/rasp.sh']),
#                         encoding='utf-8',
#                         ),
#            'es': Parser(name='freeling',
#                         config=config['freeling+'],
#                         command=expand(['{TOOLS}/bin/analyzer', '--nec', '-f', '{TOOLS}/etc/dep.cfg']),
#                         encoding='utf-8',
#                         ),
#            'ru': Parser(name='malt-ru',
#                         config=config['malt'],
#                         command=expand(['{RU_TOOLS}/russian-malt-alt.sh']),
#                         #command=expand(['{RU_TOOLS}/russian-malt-tt.sh']),
#                         encoding='utf-8'),
#            'fa': Parser(name='malt-fa',
#                         config=config['malt'],
#                         command=expand(['{FA_TOOLS}/persian-malt.sh']),
#                         encoding='utf-8'), }


# TODO: probably remove the following.
class PennTree(object):
    import string
    from pyparsing import Suppress, Forward, Word, OneOrMore, alphas, Group

    LPAR, RPAR = map(Suppress, '()')
    Tag = Word(string.uppercase + "$:;-'\".,?!")
    Lemma = Word(alphas + "-.,'?!")
    Pair = Group(LPAR + Tag + Lemma + RPAR)
    List = Forward()
    List << (LPAR + Tag + OneOrMore(Pair | List) + RPAR)
    List.setParseAction(lambda t: t[1:])
    Parser = List

    @staticmethod
    def test():
        s = """
            (ROOT
              (X
                (NP (NNP Tae))
                (: -)
                (FRAG
                  (NP
                    (NP
                      (NP (NNP Sung) (NNP Jeong))
                      (NP (DT Every) (NN year)))
                    (, ,)
                    (NP
                      (NP (PRP they))
                      (SBAR
                        (S
                          (NP (NN mate)
                            (CC and)
                            (NNS cubs))
                          (VP (VBP are)
                            (VP (VBN born))))))))
                (. .)))"""
        pprint(PennTree.Parser.parseString(s).asList())


class RaspOutput(object):
    from pyparsing import (Suppress, Word, OneOrMore, alphanums, Group,
                           ZeroOrMore, nums, Optional, alphas, Regex)

    LPAR, RPAR, VBAR, SEMI, PLUS, COLON, U = map(Suppress, '()|;+:_')
    String = Word(alphanums + ":;-,!?.'$~&#/%" + '"')
    Lemma = Word(alphanums + '-.$&~#/%')
    Integer = Word(nums)
    Float = Regex(r'-?[0-9]*\.[0-9]*')
    Quoted = VBAR + String + VBAR
    Simple = String | Quoted
    Rel = Regex('|'.join(('arg_mod', 'arg', 'aux', 'ccomp', 'cmod', 'conj',
                          'comma', 'poss', 'part', 'decim', 'echo', 'inv',
                          'csubj', 'det', 'dobj', 'iobj', 'ncmod', 'ncsubj',
                          'obj2', 'obj', 'passive', 'pcomp', 'pmod', 'as', 'of',
                          'tag', 'ta', 'to', 'prt', 'voc', 'ellip', 'quote',
                          'xcomp', 'xmod', 'xsubj', 'num', 'end', 'bal', 'that',
                          'range', 'colon')))
    QuotedRel = VBAR + Rel + VBAR
    Header = (Group(LPAR + OneOrMore(Simple) + RPAR) + Integer + SEMI + LPAR
              + Optional(Float) + RPAR)
    Header.setParseAction(lambda t: t[0])
    Ignore = Suppress('gr-list: 1')
    Complex = Group(VBAR + Lemma + Optional(PLUS + Optional(Word(alphas)))
                    + COLON + Integer + U + Lemma + VBAR)
    Line = Group(LPAR + QuotedRel + Optional(QuotedRel | U)
                 + OneOrMore(QuotedRel | Complex | U) + RPAR)
    Parser = ZeroOrMore(Group(Header + Ignore + Group(ZeroOrMore(Line))))

    @staticmethod
    def test1():
        s = """
            (|has| |Cho-| |won| |gotten| |any| |better| |since| |he| |started| |running| ?) 1 ; (-22.644)
            gr-list: 1
            (|aux| |win+ed:3_VVD| |have+s:1_VHZ|)
            (|ncsubj| |win+ed:3_VVD| |Cho-:2_NP1| _)
            (|passive| |get+en:4_VVN|)
            (|xcomp| _ |win+ed:3_VVD| |get+en:4_VVN|)
            (|cmod| _ |get+en:4_VVN| |since:7_ICS|)
            (|ccomp| _ |since:7_ICS| |start+ed:9_VVD|)
            (|ncsubj| |start+ed:9_VVD| |he:8_PPHS1| _)
            (|xcomp| _ |start+ed:9_VVD| |run+ing:10_VVG|)
            (|xcomp| _ |get+en:4_VVN| |better:6_JJR|)
            (|ncsubj| |better:6_JJR| |any:5_DD| _)
            (|dobj| |get+en:4_VVN| |any:5_DD|)
            """
        pprint(RaspOutput.Parser.parseString(s).asList())

    @staticmethod
    def test2():
        s1 = """
            (|Cho-| |won| |s| |heart| |is| |...| |...| |going| |pitter| |pat| |.|) 0 ; ()
            gr-list: 1
            (|dobj| |go+ing:9_VVG| |pat:11_NN1|)
            (|ncmod| _ |pat:11_NN1| |pitter:10_NN1|)
            (|ta| |bal| |be+s:6_VBZ| |...:7_...|)
            (|ncsubj| |win+ed:2_VVD| |Cho-:1_NP1| _)
            (|dobj| |win+ed:2_VVD| |heart:5_NN1|)
            (|ncmod| _ |heart:5_NN1| |s:4_ZZ1|)
            """
        s2 = """
            (|presents|) 0 ; ()
            gr-list: 1
            """
        s3 = """
            (|investment| |Manager| |:|) 0 ; ()
            gr-list: 1
            (|ncmod| _ |Manager:2_NN1| |investment:1_NN1|)
            """
        pprint(RaspOutput.Parser.parseString(s1).asList())
        pprint(RaspOutput.Parser.parseString(s2).asList())
        pprint(RaspOutput.Parser.parseString(s3).asList())

    @staticmethod
    def test4():
        s = """
            (|a| |Cineline| II |Production|) 0 ; ()
            gr-list: 1
            (|dobj| |a:1_II| |Production:4_NN1|)
            (|ncmod| _ |Production:4_NN1| |Cineline:2_NP1|)
            (|ncmod| |num| |Production:4_NN1| |II:3_MC|)
        """
        pprint(RaspOutput.Parser.parseString(s).asList())

    @staticmethod
    def test3(stream):
        p = RaspOutput.Parser
        p.parseFile(stream)
        for r in p.parseFile(stream):
            pprint(r)


# NB: The following has been lifted from NLTK and modified as noted.

import re
from nltk.tokenize.api import TokenizerI

class WordTokenizer(TokenizerI):
    """
    The Treebank tokenizer uses regular expressions to tokenize text as in Penn Treebank.
    This is the method that is invoked by ``word_tokenize()``.  It assumes that the
    text has already been segmented into sentences, e.g. using ``sent_tokenize()``.

    This tokenizer performs the following steps:

    - split standard contractions, e.g. ``don't`` -> ``do n't`` and ``they'll`` -> ``they 'll``
    - treat most punctuation characters as separate tokens
    - split off commas and single quotes, when followed by whitespace
    - separate periods that appear at the end of line

        >>> from nltk.tokenize import TreebankWordTokenizer
        >>> s = '''Good muffins cost $3.88\\nin New York.  Please buy me\\ntwo of them.\\n\\nThanks.'''
        >>> TreebankWordTokenizer().tokenize(s)
        ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.',
        'Please', 'buy', 'me', 'two', 'of', 'them', '.', 'Thanks', '.']
        >>> s = "They'll save and invest more."
        >>> TreebankWordTokenizer().tokenize(s)
        ['They', "'ll", 'save', 'and', 'invest', 'more', '.']

    NB. this tokenizer assumes that the text is presented as one sentence per line,
    where each line is delimited with a newline character.
    The only periods to be treated as separate tokens are those appearing
    at the end of a line.
    """

    # List of contractions adapted from Robert MacIntyre's tokenizer.
    CONTRACTIONS2 = [re.compile(r"(?i)\b(can)(not)\b", re.UNICODE),
                     re.compile(r"(?i)\b(d)('ye)\b", re.UNICODE),
                     re.compile(r"(?i)\b(gim)(me)\b", re.UNICODE),
                     re.compile(r"(?i)\b(gon)(na)\b", re.UNICODE),
                     re.compile(r"(?i)\b(got)(ta)\b", re.UNICODE),
                     re.compile(r"(?i)\b(lem)(me)\b", re.UNICODE),
                     re.compile(r"(?i)\b(mor)('n)\b", re.UNICODE),
                     re.compile(r"(?i)\b(wan)(na) ", re.UNICODE)]
    CONTRACTIONS3 = [re.compile(r"(?i) ('t)(is)\b", re.UNICODE),
                     re.compile(r"(?i) ('t)(was)\b", re.UNICODE)]
    CONTRACTIONS4 = [re.compile(r"(?i)\b(whad)(dd)(ya)\b", re.UNICODE),
                     re.compile(r"(?i)\b(wha)(t)(cha)\b", re.UNICODE)]

    def tokenize(self, text):
        # starting quotes: modified
#         text = re.sub(r'^\"', r'``', text) # do not replace " with ``
        text = re.sub(r'(``)', r' \1 ', text)
        # added for Russian
        text = re.sub(r'([«»])', r' \1 ', text)
#         text = re.sub(r'([ (\[{<])"', r'\1 `` ', text)
        text = re.sub(r'([ (\[{<])"', r'\1 " ', text)

        #punctuation
        text = re.sub(r'([:,])([^\d])', r' \1 \2', text)
        text = re.sub(r'\.\.\.', r' ... ', text)
        text = re.sub(r'[;@#$%&]', r' \g<0> ', text)
        text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)\s*$', r'\1 \2\3 ', text)
        text = re.sub(r'[?!]', r' \g<0> ', text)

        text = re.sub(r"([^'])' ", r"\1 ' ", text)

        #parens, brackets, etc.
        text = re.sub(r'[\]\[\(\)\{\}\<\>]', r' \g<0> ', text)
        text = re.sub(r'--', r' -- ', text)

        #add extra space to make things easier
        text = " " + text + " "

        #ending quotes
        text = re.sub(r'"', ' " ', text)
        text = re.sub(r'(\S)(\'\')', r'\1 \2 ', text)

        text = re.sub(r"([^' ])('[sS]|'[mM]|'[dD]|') ", r"\1 \2 ", text)
        text = re.sub(r"([^' ])('ll|'re|'ve|n't|) ", r"\1 \2 ", text)
        text = re.sub(r"([^' ])('LL|'RE|'VE|N'T|) ", r"\1 \2 ", text)

        for regexp in self.CONTRACTIONS2:
            text = regexp.sub(r' \1 \2 ', text)
        for regexp in self.CONTRACTIONS3:
            text = regexp.sub(r' \1 \2 ', text)

        # We are not using CONTRACTIONS4 since
        # they are also commented out in the SED scripts
        # for regexp in self.CONTRACTIONS4:
        #     text = regexp.sub(r' \1 \2 \3 ', text)

        text = re.sub(" +", " ", text)
        text = text.strip()

        #add space at end to match up with MacIntyre's output (for debugging)
        if text != "":
            text += " "

        return text.split()

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)


def _test():
    RaspOutput.test1()
    RaspOutput.test2()
    RaspOutput.test4()
    RaspOutput.test3(open(sys.argv[1]))

