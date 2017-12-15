"""Created on Dec 2, 2014 by @author: Luca Gilardi <lucag@ICSI.berkeley.edu
"""
from __future__ import print_function

import bokeh.plotting as bk
import numpy as np
import pandas as pd

from bokeh.charts import Histogram, Bar
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from pprint import pprint
from matplotlib.pyplot import xlabel
from depparsing.util import Struct
from cStringIO import StringIO


DEFAULT_INDEX, DEFAULT_TYPE = 'lms-test3', 'lms3'

# Init Bokeh here
# bk.output_notebook()

# Connect to ES here. If something goes wrong with it, reload module
_es = Elasticsearch()
_ic = IndicesClient(_es)


def fields(index=DEFAULT_INDEX, doc_type=DEFAULT_TYPE):
    ms = _ic.get_mapping(index=index, doc_type=DEFAULT_TYPE)
    return sorted(ms[index]['mappings'][doc_type]['properties'].keys())


def describe_field(field):
    return field.replace('-', ' ').replace('_', ' ').title()


def simple(x):
    return not isinstance(x, list)


def make_one(x):
    if simple(x):
        return {x: {'terms': {'field': x}}}
    else:
        return {x: make_many(x)}


def make_many(xs):
    pass
#     return


def make_aggs(tree, size=100):
    #     y = dict((n, v) for n, v in
    #     return {'aggs': y}

    for x in tree:
        if isinstance(x, list):
            return {'aggs': [make_one(y) for y in x]}
        else:
            return {'aggs': make_one(x)}


def make_aggs2(x, y, size=100, debug=False):
    aggs = {'aggs': {x: {'terms': {'field': x, 'size': size},
                         'aggs': {y: {'terms': {'field': y, 'size': size}}}}}}
    if debug:
        pprint(aggs)

    return aggs


# def make_aggs1(x, size=100, debug=False):
#     aggs = {'aggs': {x: {'terms': {'field': x, 'size': size},
#                          'aggs': {y: {'terms': {'field': y, 'size': size}}}}}}
#     if debug:
#         pprint(aggs)
#
#     return aggs


def aggregates(query, aggs, index=DEFAULT_INDEX, size=100, debug=False):
    body = dict(size=size)
    body.update(query)
    body.update(aggs)
    if debug:
        pprint(body)
    return _es.search(index=index, body=body)['aggregations']


def get_groups(aggs_result, x, y):
    """Extract the groups from result as DataFrames as (group_name, DF) pairs.
    """
    def buckets(label):
        return lambda m: m[label]['buckets']

    return dict((b['key'], pd.DataFrame(buckets(y)(b))) for b in buckets(x)(aggs_result))


def label(l):
    return 'doc_count_%s' % l


def unlabel(l):
    return l.lstrip('doc_count_')


def merge_groups(groups, x, y, limit):
    # TODO: Let's assume it's ony two groups for now
    if len(groups) != 2:
        print('Warning: only 2 groups are merged!')

    (l_label, l), (r_label, r) = groups.items()
    merged = pd.merge(l, r, suffixes=('_' + l_label, '_' + r_label), copy=True, on='key', how='outer')
    merged['diff'] = np.abs(getattr(merged, label(l_label)) - getattr(merged, label(r_label)))
    merged = merged.sort('diff', ascending=False)
#     print(merged)
    return merged[:limit]


def make_bar_chart(mgs, x, y, pairs, width=800, height=600, legend=True, stacked=False, tools=True, notebook=True):
    cols = [c for c in mgs.columns if c.startswith('doc_count')]
    return Bar(dict((describe_field(unlabel(c)), mgs[c]) for c in cols),
               [l for l in mgs.key],
               width=width,
               height=height,
               legend=legend,
               stacked=stacked,
               tools=tools,
               xlabel='%s' % describe_field(y),
               #                xlabel='%s (%s)' % (describe_field(y),
               #                                    ', '.join('%s: %s' % (describe_field(z), val)
               #                                              for z, val in pairs)),
               ylabel='Number of Instances',
               notebook=notebook)


def make_query(pairs, kind='prefix', cutoff=.65):
    return {"filter": {"bool": {"must": [{kind: {z: val}} for z, val in pairs] + [{"range": {"score": {"from": cutoff}}}]}}}


def make_query2(pairs, op='and', kind='prefix', cutoff=.65):
    return {"query": {"filtered": {"query": {"range": {"score": {"from": cutoff}}},
                                   "filter": {op: [{kind: {z: val}} for z, val in pairs]}}}}

def make_query3(pairs, op, kind, cutoff):
    z, val = pairs[0]
    return {"query": {"filtered": {"filter": {"range": {"score": {"from": cutoff}}},
                                   "query": {kind: {z: val}}}}}


def chart(pairs, x, y, op='and', kind='query_string', cutoff=.65, limit=5, height=600, width=800, debug=False):
    """Query for z prefix_of val, group by x, y.
    """
#     q = make_query(pairs, kind=kind)
#     q = make_query2(pairs, op=op, kind=kind)
    q = make_query3(pairs, op=op, kind=kind, cutoff=cutoff)
#     if debug:
#         pprint(q)
    aq = make_aggs2(x, y)
    aggs = aggregates(q, aq, debug=debug)

#     pprint(pairs)
    
    gs = get_groups(aggs, x, y)
    mgs = merge_groups(gs, x, y, limit)

    return make_bar_chart(mgs, x, y, pairs, height=height, width=width)


def make_chart_data(pairs, x, y, op='and', kind='query_string', limit=5, cutoff=.65, debug=False):
    """Query for z prefix_of val, group by x, y.
    """
    q = make_query3(pairs, op=op, kind=kind, cutoff=cutoff)
    aq = make_aggs2(x, y)
    aggs = aggregates(q, aq, debug=debug)

#     pprint(pairs)
    
    gs = get_groups(aggs, x, y)
    mgs = merge_groups(gs, x, y, limit)

    return Struct(pairs=pairs, x=x, y=y, mgs=mgs)


def chart2(data, height=600, width=800, debug=False):
    return make_bar_chart(data.mgs, data.x, data.y, data.pairs, height=height, width=width)


def sentences(pairs, limit=5, index='lms-test3', kind='query_string', debug=False):
    body = {'size': limit, 'query': {'bool': {'must': [{kind: {field: value}} for field, value in pairs]}},
            'sort': [{"source-coreness": {"order": "desc"}}]}
    if debug:
        pprint(body)

    res = _es.search(index=index, body=body)
    if debug:
        pprint(res)

    return [h['_source'] for h in res['hits']['hits']]


def sentences2(pairs, limit=5, index='lms-test3', kind='query_string', debug=False):
    def kind(f, v):
        return 'query_string' if f == 'query' else 'term'
    body = {'size': limit, 'query': {'bool': {'must': [{kind(f, v): {f: v}} for f, v in pairs]}},
            'sort': [{"source-coreness": {"order": "desc"}}]}
    if debug:
        pprint(body)

    res = _es.search(index=index, body=body)
    if debug:
        pprint(res)

    return [h['_source'] for h in res['hits']['hits']]


def main():
    bk.output_notebook()
