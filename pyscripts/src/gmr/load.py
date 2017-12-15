from __future__ import print_function

from argparse import ArgumentParser
from datetime import timedelta
from glob import iglob
from itertools import izip, count
from os import stat
from os.path import basename, splitext
from pprint import pprint
from time import sleep
from timeit import default_timer
import gzip
import re
import socket
import sys
from IPython.core.release import description

try:
    from couchbase import Couchbase  # @UnresolvedImport
except:
    print('couchbase not available')
from couchdb import PreconditionFailed
from depparsing.util import dict_dfs
from depparsing.util import ureader, flattened, update, Unbuffered, grouped
from pymongo import MongoClient
from ujson import loads
import couchdb
import couchdbkit
import restkit
import ujson

LANGS = ('en', 'es', 'ru', 'fa')

stdout = Unbuffered(sys.stdout)


class DB(object):

    def insert(self, documents):
        abstract  # @UndefinedVariable

    def drop(self, documents):
        abstract  # @UndefinedVariable

    def index(self, documents):
        abstract  # @UndefinedVariable


class MongoDB(DB):

    def __init__(self, db, collections, host='localhost', port=27017, clear=False, **_):
        conn = MongoClient(host, port)
        update(self, db=conn[db])
        if clear:
            for coll in collections:
                self.db.drop_collection('docs_%s' % coll)
                # Rebuld indices here...

    def drop(self, collection):
        self.db.drop_collection('docs_%s' % collection)
        # Rebuld indices here...

    def insert(self, collection, documents):
        self.db[collection].insert(documents)


class CouchDB(DB):

    def __init__(self, db, collections, host='localhost', port=5984, clear=False, **_):
        def create_or_open_db(dbname):
            try:
                return server.create(dbname)
            except PreconditionFailed:
                return server[dbname]

        server = couchdb.Server('http://%s:%d' % (host, port))
        update(self,
               server=server,
               databases=dict(('docs_%s' % c, create_or_open_db('%s_docs_%s' % (db, c))) for c in collections))

    def insert(self, collection, documents):
        return self.databases[collection].update(documents)


class CouchDB2(CouchDB):

    def __init__(self, db, collections, host='localhost', port=5984, clear=False, **_):
        server = couchdbkit.Server(uri='http://%s:%d' % (host, port), uuid_batch_count=20000)
        # CouchDB has no collections, so we create one db for each language, instead of one collection.
        dbnames = [('docs_%s' % coll, '%s_docs_%s' % (db, coll)) for coll in collections]
        if clear:
            all_dbs = server.all_dbs()
            for _, name in dbnames:
                if name in all_dbs:
                    server.delete_db(name)
        update(self,
               server=server,
               databases=dict((coll, server.get_or_create_db(name)) for coll, name in dbnames))

    def insert(self, collection, documents):
        return self.databases[collection].bulk_save(documents)


def unused_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    _, port = s.getsockname()
    s.close()
    return port


class CouchBase(DB):

    @staticmethod
    def _all_buckets(server):
        return set(b['name'] for b in loads(server.get('/pools/default/buckets').body_string()))

    @staticmethod
    def _delete_bucket(server, bucket):
        return server.delete('/pools/default/buckets/%s' % bucket)

    @staticmethod
    def _flush_bucket(server, bucket):
        return server.post('/pools/default/buckets/%s/controller/doFlush' % bucket)

    @staticmethod
    def _create_bucket(server, bucket):
        return server.post('/pools/default/buckets/', bucket)

    @staticmethod
    def _ensure_bucket(server, bucket):
        if not bucket in CouchBase._all_buckets(server):
            payload = dict(name=bucket, authType='none', flushEnabled=1,
                           proxyPort=unused_port(), ramQuotaMB=2048, replicaNumber=0)
            return server.post('/pools/default/buckets/', payload=payload)
        else:
            return None

    def __init__(self, db, collections, username, password, host='localhost', port=8091, clear=False, **entries):
        auth = restkit.BasicAuth(username, password)
        server = restkit.Resource('http://%s:%s' % (host, port), filters=[auth])

        def make_conn(bucket):
            self._ensure_bucket(server, bucket)
            return Couchbase.connect(bucket=bucket, host=host, port=port, timeout=5.0)

        if clear:
            all_buckets = self._all_buckets(server)
            for coll in collections:
                if coll in all_buckets:
                    self._flush_bucket(server, coll)
        update(self, server=server, connections=dict(('docs_%s' % coll, make_conn(coll)) for coll in collections))

    def drop(self, collection):
        self._flush_bucket(self.server, collection)

    def insert(self, collection, documents):
        try:
            return self.connections[collection].add_multi(dict((unicode(doc['_id']), doc) for doc in documents))
        except:
            print('Problem inserting:')
            pprint(documents[0])
            pprint(documents[1])
            raise


def monitor(path, changed, timeout=1.0):
    """Monitor a single file.
    """

    def _stat():
        try:
            return stat(path)
        except:
            return None

    s0 = _stat()
    while True:
        sleep(timeout)
        s1 = _stat()
        if s0 != s1:
            changed(s1)
        s0 = s1


def openfile(fname):
    _, ext = splitext(fname)
    if ext == '.gz':
        return ureader(gzip.open(fname))
    elif fname != '-':
        return ureader(open(fname))
    else:
        return ureader(sys.stdin)


def make_database(dbtype, dbname, collections, clear, **entries):
    if clear:
        print('Flushing %s.' % ', '.join(collections))
    builders = dict(mongodb=MongoDB, couchdb=CouchDB, couchdbkit=CouchDB2, couchbase=CouchBase)
    return builders[dbtype](dbname, collections, clear=clear, **entries)


def CountingPred(n):
    """Produces <n> True values, a False, <n> True values...
    """

    def pred1(_):
        return next(it) % (n + 1) != 0

    it = count(start=1)
    return pred1


def mload(lang, fn, sentences, chunk):
    """Bulk load sentences.
    """
    WORD = re.compile(r'[a-zA-Z_]+', re.UNICODE)

    def update_various(n, sentence):
        "In-place update!"
        _id = (fn.split('_', 1)[1], n) if fn.startswith('Result_') else (fn, n)
        sentence['file'], sentence['n'] = _id
        sentence['_id'] = '%s:%.5d' % _id
        if 'lms' in sentence:
            for lm in sentence['lms']:
                # print(lm['target']['schema'])
                if 'schema' in lm['target']:
                    _, prefix_schema = lm['target']['schema'].split('#')
                    schema = prefix_schema.split('_')
                    lm['target']['schemaname'] = ' '.join(schema[1:])
                    lm['source']['lemma'] = lm['source']['lemma'].lower()
                    lm['target']['lemma'] = lm['target']['lemma'].lower()
                # Fix up the 'concept' and 'concepts' keys.
                source = lm['source']
                source['concepts'] = WORD.findall(source['concept'] or '') if 'concept' in source else []
        return sentence

    t0 = default_timer()
    if not chunk:
        db.insert('docs_%s' % lang, map(update_various, *izip(*enumerate(sentences, start=1))))
        return (default_timer() - t0, len(sentences))
    else:
        l = 0
        total_l = len(sentences)
        for i, b in enumerate(grouped(chunk, sentences)):
            sentences = filter(None, b)
            l += len(sentences)
            if i % 20 == 0:
                print('{:3d}%\b\b\b\b'.format(int(l * 100.0 / total_l)), end='', file=stdout)
            db.insert('docs_%s' % lang, map(update_various, *izip(*enumerate(sentences, start=1 + chunk * i))))
        print('100%', end='', file=stdout)
        assert l == total_l, 'l (%d) != total_l(%d)' % (l, total_l)
        return (default_timer() - t0, l)


def size(d):
    """Computes the size of a dictionary.
    :param d:
    """
    return sum(len(e) for e in dict_dfs(d))


def main(db, fnames, chunk, collection, watchfile=None):
    def get_perspective(documents):
        if (isinstance(documents, list)
            and len(documents) > 0
            and 'perspective' in documents[0]):
            return documents[0].perspective.replace(' ', '_')
        if isinstance(documents, dict) and 'perspective' in documents:
            return documents.perspective.replace(' ', '_')
        return None

    def do_load():
        print('Starting up: %s...' % ('(dest. collection: %s)' % collection if collection else ''))
        t0 = default_timer()
        total_ins_t = 0.0
        total_count = 0
        for fn in fnames:
            with openfile(fn) as f:
                print('  %s: loading,' % fn, end=' ', file=stdout)
                data = ujson.load(f)
                documents = data['documents']
                perspective = get_perspective(documents)
                if perspective:
                    # Assign perspective to all sentences
                    print('[p = %s],' % perspective, end=' ', file=stdout)
                    for s in data['sentences']:
                        s['perspective'] = perspective
                print('inserting,', end=' ', file=stdout)
                coll = data['lang'] if not collection else collection
                ins_t, count = mload(coll, basename(fn), data['sentences'], chunk=chunk)
                print('done; %d sentences inserted in %.2fs (%.2f sent/s).' %
                      (count, ins_t, count / ins_t), file=stdout)
            total_count += count
            total_ins_t += ins_t
        print('Processed %d sentences in %s (%.2f sent/s).' %
              (total_count, timedelta(seconds=default_timer() - t0), total_count / total_ins_t),
              file=stdout)
        return 0  # All ok

    if watchfile:
        def changed(s):
            print('%s changed: reloading.' % watchfile)
            print(s.st_atime, file=sys.stderr)
            db.drop(collection)
            return do_load()

        print('Watching %s ...' % watchfile)
        return monitor(watchfile, changed)
    else:
        return do_load()


def argparser():
    p = ArgumentParser(description='Import GMR files into document database.')
    p.add_argument('-c', dest='clear', action='store_true', default=False, help='clear DB first (DANGER!!!)')
    p.add_argument('-t', dest='dbtype', choices=['mongodb', 'couchdb', 'couchdbkit', 'couchbase'], default='mongodb',
                   help='module to use')
    p.add_argument('-n', type=int, dest='chunk', default=None, help='chunk size', metavar='<size>')
    p.add_argument('-l', type=str, dest='collection', default=None, help='database collection',
                   metavar='<collection-name>')
    p.add_argument('-w', type=str, dest='watchfile', default=None, help='File to watch', metavar='<file-name>')
    p.add_argument('-f', type=str, nargs='+', help='Files to import', metavar='<file-name>')
    p.add_argument('-u', type=str, dest='username', default='Administrator', help='User name')
    p.add_argument('-p', type=str, dest='password', default='-c4cc4cul0-', help='Password')
    return p


if __name__ == '__main__':
    args = argparser().parse_args()
    collections = [args.collection] if args.collection else [lang for lang in LANGS]
    db = make_database(dbname='test', collections=collections, **vars(args))
    files = sorted(flattened(iglob(a) for a in args.f)) if len(args.f) > 0 else ['-']
    sys.exit(main(db, files, args.chunk, args.collection, args.watchfile))
