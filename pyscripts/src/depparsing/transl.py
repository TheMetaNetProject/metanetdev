"""
Created on Aug 10, 2012
@author: lucag
"""

import gzip, codecs, string, sys
from itertools import izip, izip_longest, imap, tee, groupby
from functools import partial
from pprint import pprint, pformat

def tripletwise(it):
    a, b, c = tee(it, 3)
    next(b, None)
    next(c, None); next(c, None)
    return izip_longest(a, b, c)

dash_split = partial(string.split, sep='-')
    
def translations(source, target, tmap):
#    from pprint import pprint
    from string import lower
    
    for (i, src), (_, tgt), (_, pairs) in izip(source, target, tmap):
        for s, t in ((int(s), int(t)) for (s, t) in imap(dash_split, pairs)):
            try:
                yield [i + 1] + map(lower, (src[s], tgt[t]))
            except IndexError:
                pprint((src, tgt, pairs), sys.stderr)
                raise


def translations2(source, target, tmap):
    def index(recs):
        def tolower2(t):
            l = list(t)
            l[2] = l[2].lower()
            return l
        return dict((r[1], tolower2(r)) for r in recs)
    
    NV = ('N', 'V')
    for (i1, _src), (i2, _tgt), (i3, pairs) in izip(source, target, tmap):
        assert i1 == i2 == i3, pformat((i1, list(_src), i2, list(_tgt), i3, pairs))
        src, tgt = map(index, (_src, _tgt)) 
        for s, t in imap(dash_split, pairs):
            try:
                src_rec, tgt_rec = src[s], tgt[t]
                # (sent_id, word_id, lemma, POS) tuples
                src_pos, tgt_pos = src_rec[3][0], tgt_rec[3][0]
                if src_pos in NV and tgt_pos in NV and src_pos == tgt_pos:
                    yield map(unicode, src[s] + tgt[t][1:])
            except KeyError:
                pass
#                pprint((s, t, src, tgt, pairs), sys.stderr)

create_pair = """
    create table if not exists {0} (sent_id     integer, 
                                    src_word_id integer, 
                                    src_lemma   text,
                                    src_pos     text, 
                                    tgt_word_id integer,
                                    tgt_lemma   text, 
                                    tgt_pos     text);
    """.format

delete_pair = """
    delete from {0};
    """.format

insert_into_pair = """
    insert into {0} values (?, ?, ?, ?, ?, ?, ?)
    """.format

tabjoin = u'\t'.join

def main2(args):
    import sqlite3, util
#    from itertools import islice

    def filler(sent_id):
        return (sent_id, -1, '?', '?')
        
    def key((sent_id, _1, _2, _3)):
        return sent_id

    def tokenized(stream):
        return enumerate(imap(string.split, stream), start=1)

    filled = partial(util.filled, filler=filler, key=key, start=1)

    USAGE = """
        Usage: {0[0]} <source> <target> <output.db> <output file> <corpus> <src_lang> <tgt_lang> <source-to-taget-translation>
        """.format

    if len(args) != 9:
        print USAGE(args)
        return 
    
    
    source, target, output = map(sqlite3.connect, args[1:4])
    corpus_id, src_lang_id, tgt_lang_id = args[5:8] 

    tmap = codecs.getreader('utf-8')(gzip.open(args[8]))
    print 'txt out:', args[4]
    outstream = codecs.getwriter('utf-8')(gzip.open(args[4], 'wb'))

    pair_name = '{0}_to_{1}'.format(src_lang_id, tgt_lang_id)
    
    select = """
        select sent_id, word_id, lemma, pos from {0}_{1} order by sent_id, word_id;
        """.format
    
    #with source, target, tmap, output, outstream:
    with source, target, tmap, outstream:
        src_stream = groupby(filled(source.execute(select(corpus_id, src_lang_id))), key)
        tgt_stream = groupby(filled(source.execute(select(corpus_id, tgt_lang_id))), key)
        #output.execute(create_pair(pair_name))
        #output.execute(delete_pair(pair_name))
        #output.execute('create index if not exists target on pair(target)')
        #output.commit()
        sys.stdout.write('Translating {0[5]} into {0[6]}: '.format(args))
        sys.stdout.flush()
        values = []
        for i, t in enumerate(translations2(src_stream, tgt_stream, tokenized(tmap))):
        #for i, t in enumerate(islice(translations2(src_stream, tgt_stream, tokenized(tmap)), 10)):
            values.append(t)
            if i % 100000 == 0:
                #pprint(values)
                #output.executemany(insert_into_pair, values)
                #output.commit()
                outstream.writelines(tabjoin(v) + u'\n' for v in values)
                values = []
                sys.stdout.write('.')
                sys.stdout.flush()
        else:
            #pprint(values)
            #output.executemany(insert_into_pair, values)
            #output.commit()
            outstream.writelines(tabjoin(v) + u'\n' for v in values)

def main(args):
    import sqlite3, util

    def filler(sent_id):
        return (sent_id, -1, '?', '?')
        
    def key((sent_id, _1, _2, _3)):
        return int(sent_id)

    def tokenized(stream):
        return enumerate(imap(string.split, stream), start=1)

    tabsplit = partial(string.split, sep='\t')
    
    def as_record(stream):
        for r in imap(tabsplit, stream):
            if len(r) > 1:
                yield r[0], r[1], r[3], r[4] 
   
#    filled = partial(util.normalized, filler=filler, key=key, start=1)
    filled = partial(util.filled, filler=filler, key=key, start=1)

    usage = """
        Usage: {0[0]} <source> <target> <alignment> <source lang id> <target lang id> <output>""".format

    if len(args) != 7:
        print usage(args)
        return 
    
    source, target, alignment = map(codecs.getreader('utf-8'), map(gzip.open, args[1:4]))
    outstream = codecs.getwriter('utf-8')(gzip.open(args[6] + '.gz', 'wb'))
#    src_lang_id, tgt_lang_id = args[4:6]
#    pair_name = '{0}_to_{1}'.format(src_lang_id, tgt_lang_id)
    
    #with source, target, alignment, sqlite3.connect(args[6] + '.db') as output, outstream:
    with source, target, alignment, outstream:
        #output.execute(create_pair(pair_name))
        #output.execute(delete_pair(pair_name))
        #output.execute('create index if not exists target on pair(target)')
        #output.commit()
        sys.stdout.write('Translating {0[4]} into {0[5]} '.format(args))
        sys.stdout.flush()
        values = []
        src_stream = groupby(filled(as_record(imap(string.strip, source))), key)
        tgt_stream = groupby(filled(as_record(imap(string.strip, target))), key)
        for i, t in enumerate(translations2(src_stream, tgt_stream, tokenized(alignment))):
            values.append(t)
            if i % 100000 == 0:
                #output.executemany(insert_into_pair(pair_name), values)
                #output.commit()
                outstream.writelines(tabjoin(v) + u'\n' for v in values)
                values = []
                sys.stdout.write('.')
                sys.stdout.flush()
        else:
            #pprint(values)
            #output.executemany(insert_into_pair(pair_name), values)
            #output.commit()
            outstream.writelines(tabjoin(v) + u'\n' for v in values)
    
    
if __name__ == '__main__':
    #main2(sys.argv)
    main(sys.argv)
