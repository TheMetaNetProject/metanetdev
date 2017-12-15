#!/n/banquet/dc/lucag/local/bin/python

"""Created on Aug 29, 2012
@author: lucag
"""

from itertools import imap
 
def collect(it, categories):
    """Group stuff.
    
    >>> from pprint import pprint
    >>> l = [(0, 1, 2), (1, 3, 4)]
    >>> pprint(collect(l, 'ab'))
    [defaultdict(<class 'collections.Counter'>, {1: Counter({2: 1})}),
     defaultdict(<class 'collections.Counter'>, {3: Counter({4: 1})})]
    """
    from collections import Counter, defaultdict
    
    sources = [defaultdict(Counter) for _ in categories]
    for cat, src, tgt in it: 
        sources[cat][src][tgt] += 1
    return sources


def collect2(it):
    """Count src, tgt, and src -> tgt pairs.
    """
    from collections import Counter, defaultdict
    
    sources, targets = [Counter() for _ in range(2)]
    pairs = defaultdict(Counter)
    for _, src, tgt in it: 
        sources[src] += 1
        targets[tgt] += 1
        pairs[src][tgt] += 1
    return pairs, sources, targets


def collect3(it, categories):
    """Count src, tgt, and src -> tgt pairs.
    """
    from collections import Counter, defaultdict
    
    sources, targets = [[Counter() for _ in categories] for _ in range(2)]
    pairs = [defaultdict(Counter) for _ in categories]
    for cat, src, tgt in it: 
        sources[cat][src] += 1
        targets[cat][tgt] += 1
        pairs[cat][src][tgt] += 1
    return zip(pairs, sources, targets)


def usage():
    from os.path import basename
    print """\
        Usage: {} [-r] (-n | -c <context_file> | -p) -f <source_lang_id> <target_lang_id> <pair_file> <ouput_base>
        """.format(basename(sys.argv[0]))
    sys.exit(-1)


def process(collected, out_streams, categories, src_lang, tgt_lang, reverse=False):
    spacejoin = u' '.join
    for outs, dd in zip(out_streams, collected): 
        for source, targets in dd.iteritems():
            if type(source) is str:
                print >> outs, u'{}_{}'.format(source, src_lang)
            else:
                print >> outs, spacejoin(u'{}_{}'.format(s, src_lang) for s in source)
            histogram = sorted(targets.iteritems(), key=lambda (_, cnt): cnt, reverse=True)
            outs.writelines(u'\t{0[0]}_{1}_{0[1]}\n'.format(p, tgt_lang) for p in histogram)
            print >> outs, u'-' * 72


def process_p(collected, out_streams, src_lang, tgt_lang):
    from math import log
    from functools import partial

    pairs, sources, targets = collected 
    # Reverse-sort by count (or log probability) 
    rsorted = partial(sorted, key=lambda (_, x): x, reverse=True)
    for src, tgts in pairs.iteritems():
        tgts_items = tgts.items()
        pp = [[(tgt, log(f) - log(targets[tgt])) for tgt, f in tgts_items],
              [(tgt, log(f) - log(sources[src]) - log(targets[tgt])) for tgt, f in tgts_items]]  
        hh = map(rsorted, pp)
        for outs, h in zip(out_streams, hh):
            print >> outs, u'{}_{}'.format(src, src_lang)
            outs.writelines(u'\t{0[0]}_{1}_{0[1]}\n'.format(p, tgt_lang) for p in h)
            print >> outs, u'-' * 72


def process_p2(collected, out_streams, src_lang, tgt_lang):
    from math import log
    from functools import partial

    # Reverse-sort by count (or log probability) 
    rsorted = partial(sorted, key=lambda (_, x): x, reverse=True)
    spacejoin = u' '.join
    for outs_pair, (pairs, sources, targets) in zip(out_streams, collected): 
        for src, tgts in pairs.iteritems():
            tgts_items = tgts.items()
            pp = [[(tgt, log(f) - log(targets[tgt])) for tgt, f in tgts_items],
                  [(tgt, log(f) - log(sources[src]) - log(targets[tgt])) for tgt, f in tgts_items]]  
            hh = map(rsorted, pp)
            for outs, h in zip(outs_pair, hh):
                if type(src) is str:
                    print >> outs, u'{}_{}'.format(src, src_lang)
                else:
                    print >> outs, spacejoin(u'{}_{}'.format(s, src_lang) for s in src)
                outs.writelines(u'\t{0[0]}_{1}_{0[1]}\n'.format(p, tgt_lang) for p in h)
                print >> outs, u'-' * 72


def process_counts(collected, out_streams, src_lang, tgt_lang):
    spacejoin = u' '.join
    for outs, sources in zip(out_streams, collected): 
        for (src, tgt), deps in sources.iteritems():
            print >> outs, spacejoin(u'{}_{}'.format(w, l) for w, l in zip((src, tgt), (src_lang, tgt_lang)))
            outs.writelines(u'\t{}_{}_{}\n'.format(dep, tgt_lang, n) for dep, n in deps.most_common())
            print >> outs, u'-' * 72


def main(argv):
    import gzip, os
    from itertools import ifilter
    from util import ureader, uwriter, closing, Dictionary, SpanishSet, EnglishSet
    
    if '-h' in sys.argv: 
        usage()
     
    # Reverse source and target during collection
    reverse = '-r' in argv
    _contextual = '-c' in argv
    _probabilities = '-p' in argv
    
    if not '-f' in argv:
        usage()
        
    p_args = 1 + argv.index('-f')    
    src_lang, tgt_lang, in_fname, out_fname = argv[p_args:p_args + 4]

    # The input stream
    def check_record(categories):
        def _do_check((sent_id, src_id, src_word, src_pos, tgt_id, tgt_word, tgt_pos)):
            "Check <en, es> is a pair of words with pos in categories."
            pos = src_pos[0] # same as tgt_pos[0]
            return pos in categories and is_word(src_word, 'en') and is_word(tgt_word, 'es')
        return _do_check
            
    print 'Creating dictionaries ...',
    dictionary = Dictionary(en=EnglishSet(), es=SpanishSet())
    is_word = dictionary.is_word
    print 'done.'
    
    def streams_for(categories, mode):
        return map(lambda c: uwriter(gzip.open('{}.{}.gz'.format(out_fname, c.lower()), mode)), categories)

    def noncontextual():
        if '-c' in argv or '-p' in argv:
            # Just to be sure: -c and -n are mutually exclusive
            usage()
            
        categories = 'nv'
        idx = categories.index
        def fields(rec): 
            return idx(rec[3][0]), rec[2], rec[5]
        
        print 'Reading', in_fname, '...',
        in_stream = ifilter(check_record(categories), map(lambda l: l.lower().split(), ureader(gzip.open(in_fname))))
        print 'done.'

        # Output files, one for each category
        with closing(*streams_for(categories, 'wb')) as out_streams:
            print 'Processing noncontextually', in_stream, 'for', categories, '...',
            in_recs = imap(fields, in_stream)
            collected = collect(in_recs, categories, reverse=reverse)
            process(collected, out_streams, src_lang, tgt_lang, categories, reverse)
            print 'done.'
    
    def contextual():
        """Contextual, with probabilities.
        """
        from itertools import product
        from util import grouped
        fname = argv[1 + argv.index('-c')]
        if not os.access(fname, os.F_OK):
            print 'Cannot access', fname
            usage()
        
        print 'Reading relations ...',
        lines = ureader(gzip.open(fname)).readlines()
        print 'done.'

        print 'Extracting records ...',
        recs = [l[:-1].lower().split() for l in lines]
        print 'done.'

        print 'Indexing relations ...',
        ctx = dict(((int(dep[0]), int(dep[2])), dep) for dep in recs)
        print 'done.'
        
        UNK = u'__unk__'
        
        print 'Gathering categories ...',
        categories = list(set(r[3] for r in recs)) + [UNK]
        print '({})'.format(u', '.join(categories)), 'done.'
        
        idx = categories.index 
        src, tgt, src_id = (2, 5, 1) if not reverse else (5, 2, 4)
        def fields(rec):
            s_id, w_id = int(rec[0]), int(rec[src_id])
            try:
                dep = ctx[(s_id, w_id)]
            except KeyError:
                dep = [UNK] * 6
            return idx(dep[3]), (rec[src], dep[4]), rec[tgt] 
        
        print 'Reading', in_fname, '...',
        in_stream = ifilter(check_record('v'), map(lambda l: l.lower().split(), ureader(gzip.open(in_fname))))
        print 'done.'

        # Output files, one for each category
        dotjoin = '.'.join
        fnames = [dotjoin(p) for p in product(categories, ('px', 'pmi'))] 
        with closing(*streams_for(fnames, 'wb')) as out_streams:
            print 'Processing', in_fname, 'for', categories, '...',
            in_recs = imap(fields, in_stream)
            collected = collect3(in_recs, categories, reverse=reverse)
            print 'done.\nOutputting files', ', '.join(fnames), '...' 
            process_p2(collected, grouped(2, out_streams), src_lang, tgt_lang)
            print 'done.'
            
    def contextual_noprob():
        """Contextual, without probabilities.
        """
        fname = argv[1 + argv.index('-c')]
        if not os.access(fname, os.F_OK):
            print 'Cannot access', fname
            usage()
            
        print "Contextual, no probabilities."
        
        print 'Reading relations ...',
        lines = ureader(gzip.open(fname)).readlines()
        print 'done.'

        print 'Extracting records ...',
        recs = [l[:-1].lower().split() for l in lines]
        print 'done.'

        print 'Indexing relations ...',
        # Record schema: sentence_id, noun_id, verb_id, noun, verb
        ctx = dict(((int(dep[0]), int(dep[2])), dep) for dep in recs)
        print 'done.'
        
        UNK = u'__unk__'
        
        print 'Gathering categories ...',
        categories = list(set(r[3] for r in recs)) + [UNK]
        print '({})'.format(u', '.join(categories)), 'done.'
        
        index = categories.index 
        src, tgt, src_id = (2, 5, 1) if not reverse else (5, 2, 4)
        def fields(rec):
            s_id, w_id = int(rec[0]), int(rec[src_id])
            try:
                dep = ctx[(s_id, w_id)]
            except KeyError:
                dep = [UNK] * 6
            return index(dep[3]), (rec[src], rec[tgt]), dep[4] 
        
        print 'Reading', in_fname, '...',
        in_stream = ifilter(check_record('v'), map(lambda l: l.lower().split(), ureader(gzip.open(in_fname))))
        print 'done.'

        # Output files, one for each category
        with closing(*streams_for(categories, 'wb')) as out_streams:
            print 'Processing', in_fname, 'for', categories, '...',
            in_recs = imap(fields, in_stream)
            collected = collect(in_recs, categories)
            print 'done.'
            
            assert len(collected) == len(out_streams), '{} != {}'.format(collected, out_streams)
            
            print 'Outputting files', ', '.join(categories), '...' 
            process_counts(collected, out_streams, src_lang, tgt_lang)
            print 'done.'
            
            
    def probabilities():
        if '-c' in argv or '-n' in argv:
            # Just to be sure: -c and -n are mutually exclusive
            usage()
            
        src, tgt = (2, 5) if not reverse else (5, 2)    
        
        def fields(rec): 
            return rec[3][0], rec[src], rec[tgt]
        
#        categories = ['v.px', 'v.pmi'] 
        categories = ['n.px', 'n.pmi'] 

        print 'Reading', in_fname, '...',
        in_stream = ifilter(check_record('n'), map(lambda l: l.lower().split(), ureader(gzip.open(in_fname))))
        print 'done.'

        # Output files, one for each category
        with closing(*streams_for(categories, 'wb')) as out_streams:
            in_recs = imap(fields, in_stream)
            print 'Processing probabilities in', in_fname, 'for', categories, '...',
            collected = collect2(in_recs, reverse=reverse)
            print 'done.'
            
            print 'Outputting files ...',
            process_p(collected, out_streams, src_lang, tgt_lang)
            
            print 'done.'
    
    if not _contextual:
        noncontextual()
    elif not _probabilities:
        contextual_noprob()
    else:
        probabilities()
    
if __name__ == '__main__':
    import sys
    from util import Unbuffered
    try:
        original_stdout = sys.stdout
        sys.stdout = Unbuffered(sys.stdout)
        main(sys.argv)
    finally:
        sys.stdout = original_stdout
