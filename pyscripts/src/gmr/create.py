"""Created on Sep 8, 2014 by @author: lucag
"""
from __future__ import print_function

from argparse import ArgumentParser
from functools import partial
from glob import iglob
from itertools import izip, starmap, ifilter
from multiprocessing import Pool
from os.path import splitext
from pprint import pprint
from string import atoi
from textwrap import dedent
import logging
from timeit import timeit, default_timer

from depparsing.dep2json import make_translator
from depparsing.parser.util import parserdesc
from depparsing.util import grouped, flattened, uopen, update

from gmr.load import make_database, LANGS

from IPython.parallel import Client

def lines(f):
    return (line.rstrip() for line in f)


def process(fn, writer_args, txtor_args, chunk):

    def base(fn):
        try:
            _, base = fn.split('-')
            return int(base)
        except:
            return atoi(fn, 16)

    sentence_fn, dependency_fn = '%s.ss' % fn, '%s.dep' % fn
    
    writer  = make_writer(*writer_args)
    txtor   = make_translator(*txtor_args)
    
    with open(sentence_fn) as sentence_f, open(dependency_fn) as dependency_f:
        sentences, dependencies = map(lines, (sentence_f, dependency_f))
    
        logging.info('Translation starting')
        document        = txtor.translate(dependencies, sentences, base(fn))
        logging.info('Translation ended')
        
        logging.info('Insertion starting')
        sentence_chunks = grouped(chunk, document['sentences'])
        res             = [e for e in starmap(writer, sentence_chunks)]
        logging.info('Insertion ended')
        
        return res
    

# Must be global because Pool wants to pickle it
class Writer(object):
    def __init__(self, **entries):
        update(self, entries)
    
    def __call__(self, *sentences):
        def run():
            self.db.insert('docs_%s' % self.lang, filter(None, sentences))
        return timeit(run, number=1)
    
def make_writer(dbtype, dbname, clear, lang):
    db = make_database(dbtype, dbname, LANGS, clear)

    # Working around Python's partial inability at partial...
    return Writer(db=db, lang=lang)


def argparser():
    p = ArgumentParser(description='Create in-database GMR documents.')
    p.add_argument(
        '-c',
        dest='clear',
        action='store_true',
        default=False,
        help='Clear DB first (DANGER!!!)')
    p.add_argument(
        '-t',
        dest='dbtype',
        choices=['mongodb', 'couchdb', 'couchdbkit', 'couchbase'],
        default='mongodb',
        help='Module to use')
    p.add_argument(
        '-n',
        type=int,
        dest='chunk',
        default=None,
        help='Chunk size',
        metavar='<integer>')
    p.add_argument(
        '-l',
        dest='lang',
        choices=['en', 'es', 'ru'],
        default=None,
        required=True,
        help='Language')
    p.add_argument(
        '-p',
        dest='parallel',
        type=int,
        default=1,
        help='Number of parallel processes',
        metavar='<integer>')
    p.add_argument(
        '-f',
        type=str,
        nargs='+',
        required=True,
        help='Files to import',
        metavar='<file-name>')
    return p

class Partial(object):
    def __init__(self, f, **entries):
        update(self, f=f, **entries)
        
    def __call__(self, fn):
        self.f(fn, **vars(self))
        
if __name__ == '__main__':
    args = argparser().parse_args()

    def noext(fn):
        fn, _ = splitext(fn)
        return fn

    logging.basicConfig(level=logging.INFO)
    
    fnames      = set(map(noext, flattened(iglob(a) for a in args.f)))
    desc        = parserdesc(args.lang)
    config      = desc.config
#     txtor     = make_translator(desc.name, config[0], config[1])
    txtor_args  = (desc.name, config[0], config[1])
#     writer      = make_writer(args.dbtype, 'test', args.clear, args.lang)
    writer_args = (args.dbtype, 'test', args.clear, args.lang)
#     process_fn  = partial(process, writer_args=writer_args, txtor=txtor, chunk=args.chunk)
    process_fn  = Partial(process, writer_args=writer_args, txtor_args=txtor_args, chunk=args.chunk)

    msg = """\
        Running parameters:
        --------------------------------
        Language:           {lang}
        Database:           {dbtype}
        Clear database:     {clear}
        File count:         {file_count}
        Parallel processes: {parallel}
        Chunk size:         {chunk}
        --------------------------------
        """
    print(dedent(msg).format(file_count=len(fnames), **vars(args)))
    
    parallel = min(len(fnames), args.parallel)
    if args.parallel > parallel:
        print('There are only %d files, but parallel = %d; defaulting to %d' % (len(fnames), args.parallel, parallel))
        
    def run():
        if parallel > 1:
            pool = Pool(parallel)
            result = pool.map(process_fn, fnames)
#             def start(*fns):
#                 pprint(fns)
#                 threads = [Thread(target=process_fn, args=[fn]) for fn in filter(None, fns)]
#                 for t in threads:
#                     t.daemon = True
#                     t.start()
#                 return threads
#             g = list(grouped(parallel, fnames))
#             pprint(g)
#             pprint([e for e in starmap(start, g)])
            pprint(result)
            pool.close()
            pool.join()
        else:
            map(process_fn, fnames)

    print('Elapsed time: %d s.' % timeit(run, number=1))
#     run()
    
    