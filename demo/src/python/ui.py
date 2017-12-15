"""Created on Dec 4, 2014 by @author: lucag@icsi.berkeley.edu
"""

from __future__ import print_function


from IPython.html.widgets import Button, VBox, HBox, Dropdown, Text, HTMLWidget
from IPython.display import display, clear_output

from depparsing.util import update
from index import describe_field, fields, bk, unlabel
from collections import OrderedDict
from cStringIO import StringIO
from pprint import pprint

import index
from IPython.core.display import HTML
from depparsing.util import Struct

# Init plot library
# bk.output_notebook()

def make_selector(zs, add_row):
    t = Text(description='Query string')
    t.value = 'target-concept: GUNS'
#     b = Button(description='+')
#     b.on_click(add_row)
#     d = Dropdown(values=OrderedDict((describe_field(z), z) for z in zs))
#     c = HBox(children=(d, t))
    return t
 
    
def make_aggregator(xs, ys):
    dx = Dropdown(description='"X" Axis', values=OrderedDict((describe_field(x), x) for x in xs))
    dy = Dropdown(description='"Y" Axis', values=OrderedDict((describe_field(y), y) for y in ys))
    dx.value = 'perspective'
    dy.value = 'source-schemafamilies'
    c = HBox(children=(dx, dy))
    return c
 
def make_field_chooser(x, xs, y, ys):
    """Choose values for x and y.
    """
    xd = Dropdown(description='%s:' % x, values=xs)
    yd = Dropdown(description='%s:' % y, values=ys)
    container = VBox(children=[xd, yd])
    return container
    
            
def make_vgroup(children):
    container = VBox(children=children)
    return container
    

def sentences(pairs, debug, limit=5, _index='lms-test3', kind='query_string'):
    out = StringIO()
    x, x_val = pairs[-2]
    y, y_val = pairs[-1]
    print('<h2>Example LMs</h2>', file=out)
    print('<p>%s: %s, %s: %s</p>' % (describe_field(x), x_val, describe_field(y), y_val), file=out)

    print('<ul>', file=out)
    for s in index.sentences2(pairs, limit=limit, index=_index, kind=kind, debug=debug):
        print('<li>%s</li>' % s['text'], file=out)
    print('<ul>', file=out)
    
    return HTML(out.getvalue())


class ChartForm(object):
    def __init__(self, **entries):
        update(self, entries, debug=False)
        
    def display(self, n):  # Hack!
        def add_selector(_):
            g.children = g.children[:-2] + tuple(make_selector(self.sels, add_selector)) + g.children[-2:]
        
        def get_data():
            x_val, y_val = [f.value for f in c.children]
            if self.debug: print(x_val, y_val)
            pairs = self.pairs + [(self.x, x_val), (self.y, y_val)]
            if self.debug: pprint(pairs)
            return pairs

        def out_sents(_):
            pairs = get_data()    
            display(sentences(pairs, debug=self.debug, limit=self.limit, kind=self.kind))

        s_l = HTMLWidget(value='Query')
        self.sels = [make_selector(self.sels, add_selector) for _ in range(n)]
        sels = [s_l] + self.sels

        a_l = HTMLWidget(value='Aggregations')
        self.aggs = make_aggregator(self.aggs, self.aggs)
        aggs = [a_l] + [self.aggs] 

        chart_button = Button(description=' Show Chart ')
        chart_button.on_click(self.chart4)        
        
        self.field_chooser = c = make_field_chooser('', [], '', [])
#         clear_output(wait=True)
#        display(c)
            
        self.sent_button = sent_button = Button(description=' Show LMs ')
        sent_button.on_click(out_sents)
#       display(sent_button)

        g = self.group = make_vgroup(sels + aggs + [chart_button, c, sent_button])
        
        display(self.group)
        
        return self.group
    
    def chart(self, _):
        pp = [[f.value for f in s.children if hasattr(f, 'value')] for s in self.sels] 
        x, y = [f.value for f in self.agg.children]

        if (self.debug):
            pprint(pp)
            print(x, y)
        
        title = ', '.join('{}: {}'.format(describe_field(f), v) for f, v in pp)
        
        c = index.chart(pp, x, y, kind=self.kind, height=self.height, width=self.width)
        c.title(title)
        
        c.show()
        
        # Add more widgets here?
        
    def chart2(self, _):
        pp = [[f.value for f in s.children if hasattr(f, 'value')] for s in self.sels] 
        x, y = [f.value for f in self.aggs.children]

        if (self.debug):
            pprint(pp)
            print(x, y)
        
        title = ', '.join('{}: {}'.format(describe_field(f), v) for f, v in pp)
        
        self.data = index.make_chart_data(pp, x, y, op='and', kind=self.kind, limit=self.limit, debug=self.debug)
        
        c = index.chart2(self.data, height=self.height, width=self.width)
        c.title(title)
        
        clear_output(wait=True)
        
        c.show()
        
        # Add more widgets here?
        mgs = self.data.mgs
        xs = [unlabel(c) for c in mgs.columns if c.startswith('doc_count')]
        ys = [k for k in mgs.key]
        sf = SentenceForm(pairs=pp, x=x, xs=xs, y=y, ys=ys, debug=False, limit=self.limit)
        sf.display()

    def chart3(self, _):
        pp   = [('query', self.sels[0].value)] 
        x, y = [f.value for f in self.aggs.children]

        if (self.debug):
            pprint(pp)
            print(x, y)
        
        title = ', '.join('{}: {}'.format(describe_field(f), v) for f, v in pp)
        
        self.data = index.make_chart_data(pp, x, y, op='and', kind=self.kind, limit=self.limit, debug=self.debug)
        
        c = index.chart2(self.data, height=self.height, width=self.width)
        c.title(title)
        
        clear_output(wait=False)
        
        c.show()
        
        # Add more widgets here?
        mgs = self.data.mgs
        xs = [unlabel(c) for c in mgs.columns if c.startswith('doc_count')]
        ys = [k for k in mgs.key]
        sf = SentenceForm(pairs=pp, x=x, xs=xs, y=y, ys=ys, kind=self.kind, debug=self.debug, limit=self.limit)
        sf.display()

    def chart4(self, _):
        self.pairs = pp = [('query', self.sels[0].value)] 
        x, y = [f.value for f in self.aggs.children]

        self.x, self.y = x, y
        
        if (self.debug):
            pprint(pp)
            print(x, y)
        
        title = ', '.join('{}: {}'.format(describe_field(f), v) for f, v in pp)
        
        self.data = index.make_chart_data(pp, x, y, 
                                          op='and', 
                                          kind=self.kind, 
                                          limit=self.limit, 
                                          debug=self.debug)
        
        self._chart = c = index.chart2(self.data, height=self.height, width=self.width)
        c.title(title)
        
        clear_output(wait=False)
        
        c.show()
        
        # Add more widgets here?
        mgs = self.data.mgs
        xs = [unlabel(c) for c in mgs.columns if c.startswith('doc_count')]
        ys = [k for k in mgs.key]
        xd, yd = self.field_chooser.children
        
        xd.description = x
        xd.values = xs
        
        yd.description = y
        yd.values = ys

#        sf = SentenceForm(pairs=pp, x=x, xs=xs, y=y, ys=ys, kind=self.kind, debug=self.debug, limit=self.limit)
#        sf.display()

class SentenceForm(object):
    def __init__(self, **entries):
        update(self, entries, debug=False)
        
    def display(self):  # Hack!
        def get_data():
            x_val, y_val = [f.value for f in c.children]
            if self.debug: print(x_val, y_val)
            pairs = self.pairs + [(self.x, x_val), (self.y, y_val)]
            if self.debug: pprint(pairs)
            return pairs

        def out_sents(_):
            pairs = get_data()    
            display(sentences(pairs, debug=self.debug, limit=self.limit, kind=self.kind))

        c = make_field_chooser(self.x, self.xs, self.y, self.ys)
#         clear_output(wait=True)
        display(c)
            
        sent_button = Button(description=' Show LMs ')
        sent_button.on_click(out_sents)
        display(sent_button)
        

def show_lms_ui(chart_form):
    mgs = chart_form.data.mgs
    xs = [unlabel(c) for c in mgs.columns if c.startswith('doc_count')]
    ys = [k for k in mgs.key]
    xd, yd = chart_form.field_chooser.children

    sf = SentenceForm(pairs=chart_form.pairs, 
                      x=chart_form.x, xs=xs, 
                      y=chart_form.y, ys=ys, 
                      kind=chart_form.kind, debug=chart_form.debug, limit=chart_form.limit)
    sf.display()
    



def show_ui(n=1, limit=5, debug=False, width=800, height=600):
    sels = [f for f in fields()]
    aggs = [f for f in fields()]
    f = ChartForm(sels=sels, aggs=sels, debug=debug, limit=limit, kind='query_string', 
                  height=height, width=width)
    f.display(n)
    
    return f

