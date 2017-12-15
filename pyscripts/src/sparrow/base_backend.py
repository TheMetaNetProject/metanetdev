from cStringIO import StringIO
import urllib2

from sparrow.utils import (json_to_ntriples,
                           dict_to_ntriples,
                           ntriples_to_json,
                           ntriples_to_dict)
from sparrow.error import TripleStoreError

class BaseBackend(object):

    def __init__(self):
        self._pqueries = {}
        self._nsmap = {}

    def add_pquery(self,qidstring,querytext):
        self._pqueries[qidstring] = querytext
    
    def compute_query_header(self):
        self._query_header = "\n".join([u'PREFIX %s: <%s>'%(pref,ns) for pref,ns in self._nsmap.iteritems()])
        self._turtle_header = "\n".join([u'@prefix %s: <%s> .'%(pref,ns) for pref,ns in self._nsmap.iteritems()])
    
    def get_ns(self, pref):
        return self._nsmap[pref]
    
    def get_query_header(self):
        return self._query_header
    
    def get_turtle_header(self):
        return self._turtle_header
    
    def _is_uri(self, data):
        if not isinstance(data, basestring):
            return False
        return data.startswith('http://') or data.startswith('file://')

    def _get_file(self, data):
        if self._is_uri(data):
            if data.startswith('file://'):
                return open(data[7:], 'r')
            elif data.startswith('http://'):
                return urllib2.urlopen(data)
        elif (hasattr(data, 'read') and
              hasattr(data, 'seek') and
              hasattr(data, 'close')):
            return data
        
        return StringIO(data)

    def add_json(self, data, context_name):
        data = self._get_file(data)
        try:
            data = json_to_ntriples(data)
        except ValueError, err:
            raise TripleStoreError(err)
        
        self.add_ntriples(data, context_name)

    def add_dict(self, data, context_name):
        data = dict_to_ntriples(data)
        self.add_ntriples(data, context_name)

    def get_json(self, context_name):
        data = self.get_ntriples(context_name)
        return ntriples_to_json(data)

    def get_dict(self, context_name):
        data = self.get_ntriples(context_name)
        return ntriples_to_dict(data)

    def remove_json(self, data, context_name):
        data = self._get_file(data)
        data = json_to_ntriples(data)
        self.remove_ntriples(data, context_name)

    def remove_dict(self, data, context_name):
        data = dict_to_ntriples(data)
        self.remove_ntriples(data, context_name)
