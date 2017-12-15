'''
MetaNet Wiki Python Tools

Created on Jul 29, 2013
@author: jhong
'''

import sys, argparse, codecs
import wikipedia as pywikibot
import query
import json

class MetaNetQuery:
    '''
    Class for making queries on the metanet wiki: retrieving lists of metaphors, etc.
    '''
    limit = 50
    def __init__(self,lang):
        self.site = pywikibot.getSite(lang, 'metanet')

    def getParams(self,querystring):
        params = {'action':'ask',
                  'query':querystring,
                  'format':'json'}
        return params
    
    def getMetaphors(self,propdict=None):
        querybuf = ['[[Category:Metaphor]]']
        if propdict:
            for (prop, val) in propdict.items():
                querybuf.append(u'[[%s::%s]]'%(prop,val))
        querybuf.append(u'|limit=%d'%(self.limit))
        querystring = ''.join(querybuf)
        result = query.GetData(self.getParams(querystring), self.site)
        mlist = result['query']['results'].keys()
        biglist = []
        biglist += mlist
        offset=0
        while (len(mlist) == self.limit):
            offset += self.limit
            offsetparam = "|offset=%d"%(offset)
            result = query.GetData(self.getParams(querystring+offsetparam), self.site)
            if type(result['query']['results']) is dict:
                mlist = result['query']['results'].keys()
                biglist += mlist
            else:
                break
        return sorted(biglist)
def main():
    '''
    This method here for testing
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Test",
        epilog="")
    parser.add_argument("infile",
                        help="input file")
    cmdline = parser.parse_args()
    m = MetaNetQuery('en')
#    metaphors = m.getMetaphors({'Tag':'Program sources'})
    metaphors = m.getMetaphors()
    print metaphors, len(metaphors)

if __name__ == '__main__':
    sys.exit(main())
    
