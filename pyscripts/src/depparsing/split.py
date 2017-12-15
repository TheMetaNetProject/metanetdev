# This Python file uses the following encoding: utf-8

from __future__ import print_function

import re, sys

from util import ureader, uwriter 
# from itertools import chain

rasp_abbrev = (r'[aApP]\.m\.|[A-Z]\.|Gov\.|MM\.|Mme\.|Mr\.|Ms\.|Mrs\.'
               + r'|Miss\.|Capt\.|Col\.|Dr\.|Drs\.|Rev\.|Prof\.|Sgt\.|Sr\.|St\.'
               + r'|Jr\.|jr\.|Co\.|Corp\.|Inc\.|[Cc]f\.|[Ee]g\.|[Ee]tc\.|[Ee]x\.'
               + r'|[Ii]e\.|[Vv]iz\.|[Vv]s\.|[Jj]an\.|[Ff]eb\.|[Mm]ar\.|[Aa]pr\.'
               + r'|[Jj]un\\.|[Jj]ul\\.|[Aa]ug\.|[Ss]ept?\.|[Oo]ct\.|[Nn]ov\.'
               + r'|[Dd]ec\.|[Ee]ds?\.|repr\.|Rep\.|Dem\.|trans\.|[Vv]ols?\.'
               + r'|p\.|pp\.|rev\.|est\.|[Ff]ig[s]?\.|[Nn]o[s]?\.|[Rr]efs?\.'
               + r'|[Ee]qs?\.|[Cc]hs?\.|[Ss]ecs?\.|mi\.|[Dd]epts?\.'
               + r'|Univ\.|[Nn]os?\.|Mol\.|Cell\.|Chem\.|Biol\.|et al\.')

_freeling_abbrev = ('aa.rr.', 'abr.', 'abrev.', 'a.c.', 'adj.', 'adm.', 'admón.', 'afma.',
                    'afmas.', 'afmo.', 'afmos.', 'ag.', 'ago.', 'am.', 'ap.', 'apdo.',
                    'art.', 'arts.', 'arz.', 'arzbpo.', 'assn.', 'atte.', 'av.', 'avda.',
                    'bros.', 'bv.', 'cap.', 'caps.', 'cg.', 'cgo.', 'cia.', 'cía.', 'cit.',
                    'co.', 'col.', 'corp.', 'cos.', 'cta.', 'cte.', 'ctra.', 'cts.', 'd.c.',
                    'dcha.', 'dept.', 'depto.', 'dic.', 'doc.', 'docs.', 'dpt.', 'dpto.', 'dr.',
                    'dra.', 'dras.', 'dres.', 'dto.', 'dupdo.', 'ed.', 'ee.uu.', 'ej.',
                    'emma.', 'emmas.', 'emmo.', 'emmos.', 'ene.', 'entlo.', 'entpo.', 'esp.',
                    'etc.', 'ex.', 'excm.', 'excma.', 'excmas.', 'excmo.', 'excmos.', 'fasc.',
                    'fdo.', 'feb.', 'fig.', 'figs.', 'fol.', 'fra.', 'gb.', 'gral.', 'hnos.',
                    'hros.', 'ib.', 'ibid.', 'ibíd.', 'id.', 'íd.', 'ilm.', 'ilma.', 'ilmas.',
                    'ilmo.', 'ilmos.', 'iltre.', 'inc.', 'intr.', 'ít.', 'izq.', 'izqda.',
                    'izqdo.', 'jr.', 'jul.', 'jun.', 'lám.', 'lda.', 'ldo.', 'lib.', 'lim.',
                    'loc.', 'ltd.', 'ltda.', 'mar.', 'máx.', 'may.', 'mín.', 'mons.', 'mr.',
                    'mrs.', 'ms.', 'mss.', 'mtro.', 'nov.', 'ntra.', 'ntro.', 'núm.', 'ob.',
                    'obpo.', 'oct.', 'op.', 'pág.', 'págs.', 'párr.', 'pd.', 'ph.', 'pje.',
                    'pl.', 'plc.', 'pm.', 'pp.', 'ppal.', 'pral.', 'prof.', 'pról.', 'prov.',
                    'ps.', 'pta.', 'ptas.', 'pte.', 'pts.', 'pza.', 'rda.', 'rdo.', 'ref.',
                    'reg.', 'rel.', 'rev.', 'revda.', 'revdo.', 'rma.', 'rmo.', 'r.p.m.', 'rte.',
                    'sdad.', 'sec.', 'secret.', 'sep.', 'sig.', 'smo.', 'sr.', 'sra.', 'sras.',
                    'sres.', 'srs.', 'srta.', 'ss.mm.', 'sta.', 'sto.', 'sust.', 'tech.', 'tel.',
                    'teléf.', 'telf.', 'ten.', 'tfono.', 'tít.', 'tlf.', 'ud.', 'uds.', 'vda.',
                    'vdo.', 'vid.', 'vol.', 'vols.', 'vra.', 'vro.', 'vta.')

def trans(s):
    return '[{0}{1}]{2}'.format(s[0].lower(), s[0].upper(), s[1:]).replace('.', r'\.')

freeling_abbrev = '|'.join(map(trans, sorted(_freeling_abbrev, reverse=True)))
#print freeling_abbrev

abbrev = {'rasp': rasp_abbrev, 
          'freeling': freeling_abbrev}

number = r'\d+\.\d+|\d+'
number2 = r'\d+[.,]\d+'

def splitter(parser):
    """Try to imitate the way the various parsers tokenize expressions.
    """
#    return re.compile(number + '|' + abbrev[parser] + '|' + r'\w+[~-]*?|\.\.\.|--|\S', re.UNICODE)
    if parser == 'freeling':
        return re.compile(number + '|' + abbrev[parser] + '|' + r"\w+[~-]*|\.\.\.|--|\S", re.UNICODE)
    elif parser in ('malt', 'malt-ru'):
        #return re.compile(number2 + '|' + r'[\w\d/-]+|\.\.\.|--|\d+|\S', re.UNICODE)
        #return re.compile(r'--|[\w\d/:\.-]+\b|\.\.\.|\S' + '|' + number2, re.UNICODE)
        return re.compile(r'[^ ]+', re.UNICODE)
    elif parser in ('malt-fa',):
        return re.compile(number2 + '|' + r'[\w\d/-]+|\.\.\.|--|\d+|\S', re.UNICODE)
    elif parser == 'rasp':
        return re.compile((r'%s(?:st|nd|rd|th)?' % number) + abbrev[parser] + '|' + r"[-\w]+(?!'t)|n't|'(?:m|d|s|re|ll|ve)|\.\.\.|--|\S", 
                          re.UNICODE | re.IGNORECASE)
    else:
        raise TypeError('Unknown parser type: {}'.format(parser))


def tokenizer(parser):
    return splitter(parser).findall

def usage(args):
    print('Usage: {0[0]} -p rasp|freeling|malt [-l]'.format(args), file=sys.stderr)
     

def cleaned(line):
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
    line = line.replace(u'\u2019', u"'")
    line = line.replace(u'\u2022', u"-")
    line = line.replace(u'\u2212', u'-')
    line = line.replace(u'\u2032', u"'")
    line = line.replace(u'\u2026', u'...')
    return line


spacejoin = u' '.join
nljoin = u'\n'.join

def clean(args):
    sin = ureader(sys.stdin)
    sout = uwriter(sys.stdout)
    for line in sin:
        print >> sout, cleaned(line),

def split(args):
    try:
        assert '-p' in args
    
        parser_kind = args[args.index('-p') + 1] 
        split_re = splitter(parser_kind)
        
        #sin = ureader(sys.stdin)
        sin = sys.stdin
        sout = uwriter(sys.stdout)
        tokenjoin = spacejoin if '-l' not in args else nljoin
        eos = [args[args.index('-eos') + 1]] if '-eos' in args else []
        lines = (l.rstrip().decode('utf8') for l in sin)
        for line in lines:
            print(tokenjoin(split_re.findall(line) + eos), file=sout)
            # Perhaps add blank line
            #if '-b' in args:
            #    print(file=sout)
            print(file=sout)
            
    except AssertionError:
        usage(args)
    
def main(args):
    if '-c' in args:
        clean(args)
    else:
        split(args)
        
        
if __name__ == '__main__':
    main(sys.argv)
