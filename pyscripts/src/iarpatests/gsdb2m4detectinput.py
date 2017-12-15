#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: comparegold
    :platform: Unix
    :synopsis: Gold standard testing comparison script

Script for downloading gold standard data from the gold standard
annotation collection website into XML and CSV files to be used for
testing and evaluation.

.. moduleauthor:: Luke Gottlieb<luke@icsi.berkeley.edu>,
    Jisup Hong<jhong@icsi.berkeley.edu>,
    Jason Bolton <jebolton@icsi.berkeley.edu>
"""
import sys, os, argparse, codecs, logging, pprint
import xml.etree.ElementTree as ET
from xml.dom import minidom
import urllib2
from HTMLParser import HTMLParser
import unicodecsv as csv
import ftfy


def prettify(elem):
    """ Prettify the XML for printing.
    :param elem: XML element
    :type elem: XML Element
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    file_handle = open("filename.xml", "wb")
    return reparsed.toprettyxml(indent="  ", encoding='utf-8')


class MyHTMLParser(HTMLParser):
    """ The gold standard annotation is published on an HTML page in tabular format.
    That page is accessed and parsed.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.tableData = []
    
    def print_sentences(self, html):
        self.tag_stack = []
        self.positive = True
        self.source = ""
        self.target = ""
        self.sword = ""
        self.tword = ""
        self.sspan = ""
        self.tspan = ""
        self.cxn = ""
        self.sframe = ""
        self.tframe = ""
        self.tconc = ""
        self.sconc = ""
        self.url = ""
        self.last = ""
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        newtag = tag
        for attr in attrs:
            if attr[1] == "sentence":
                newtag = tag + "." + attr[1]
            if attr[1] == "negative":
                self.positive = False
            elif attr[1] == "positive":
                self.positive = True
            if attr[0] == "source":
                self.source = attr[1]        
            if attr[0] == "target":
                self.target = attr[1]
                # print self.target
            if attr[0] == "sword":
                self.sword = attr[1]        
            if attr[0] == "tword":
                self.tword = attr[1]
            if attr[0] == "tconc":
                self.tconc = attr[1]
            if attr[0] == "sconc":
                self.sconc = attr[1]
            if attr[0] == "tspan":
                self.tspan = attr[1]
            if attr[0] == "sspan":
                self.sspan = attr[1]
            if attr[0] == "tframe":
                self.tframe = attr[1]
            if attr[0] == "sframe":
                self.sframe = attr[1]
            if attr[0] == "cxn":
                self.cxn = attr[1]
            if attr[0] == "url":
                self.url =  attr[1]
        self.tag_stack.append(newtag)
        
    def handle_endtag(self, tag):
        self.tag_stack.pop()

    def handle_data(self, data):
        if len(self.tag_stack) > 1:
            if self.tag_stack[-1] == 'td.sentence':    
                #if data != self.last:
            #         print self.positive, data
                text = data.strip()
                if not text:
                    self.logger.warning(u'skipping row with null sentence text')
                    return
                outlin = [self.url, data, self.cxn,
                            self.tword, self.sword,
                            self.tspan, self.sspan,
                            self.target, self.source, 
                            self.tframe, self.sframe,
                            self.tconc.replace(u' ',u'_'),
                            self.sconc.replace(u' ',u'_')]
                self.tableData.append(outlin)
                self.last = data

    def getTableData(self):
        return self.tableData

    
def main():
    """
    extract gold data and create 2 output files: a csv reference file, and an XML input file
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Pull gold examples from website and create comparison and input files",
        epilog="")

    # required (positional) args
    parser.add_argument("lang",
                        help="Language to get gold data for")
    parser.add_argument("outputfilebase",
                        help="Output file name base (no extension)")
    parser.add_argument("targetconcepts",
                        help="Comma-separated list of target concepts to limit to")
    parser.add_argument("-v","--verbose",action='store_true',
                        help="Display verbose error messages")
    cmdline = parser.parse_args()
    
    logLevel = logging.WARN
    if cmdline.verbose:
        logLevel = logging.INFO
    logging.basicConfig(level=logLevel,
                        format='%(asctime)s %(levelname)s %(message)s')
    
    lang = cmdline.lang
    if cmdline.targetconcepts:
        tconlist = set(cmdline.targetconcepts.split(u','))
    else:
        tconlist = None
            
    url = 'https://ambrosia.icsi.berkeley.edu:2080/goldstandard/show_all.php?language=%s' % lang
    response = urllib2.urlopen(url)
    
    parser = MyHTMLParser()
    
    hdata = response.read()

    parser.print_sentences(hdata)
    goldData = parser.getTableData()
    
    # f = codecs.open(sys.argv[2], 'w', encoding='utf-8')
    
    ln = len(goldData)
    c1 = ln / 5
    numSentsPerTI = 5
    cm = ln % 5
    
    # Create a csv for lemma (%s.csv and wordform %s2.csv
    outcsv = "%s.csv" % cmdline.outputfilebase
    ofile = open(outcsv, 'wb')
    writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
    theader = ['ti_num','sent_num',
               'url','sent_text','cxn',
               'tform','sform','tspan','sspan','tlemma','slemma',
               'tframe','sframe','tconc','sconc']
    writer.writerow(theader)
    #testItemNo = 1
    #sentNo = 1
    # start testItemNo and sentNo at 0 now
    testItemNo = 0
    sentNo = 0
    lasttext = None
    ET.register_namespace('metad', "http://www.iarpa.gov/Metaphor/DetectSchema")
    root = ET.Element('{http://www.iarpa.gov/Metaphor/DetectSchema}TestSet')
    root.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    root.set('testId', '%sdetect' % lang)
    root.set('xsi.frameLocation', "http://www.iarpa.gov/Metaphor/DetectSchema m4detectSchema_22.xsd")

    # Note: the goldData LMs must be sorted by sentence text
    # so that sentences with multiple LMs do not end being
    # duplicated in the XML
    #
    for line in goldData:
        try:
            line[1] = unicode(line[1], 'utf-8')
            text = line[1]
        except:
            line[1] = line[1].decode('cp1252')
            text = line[1]

        tform = line[3].strip()
        sform = line[4].strip()
        tconc = line[11]
        #logging.info('tform=%s   sform=%s',line[2],line[3])
        if ((tform and (not sform)) or 
            ((not tform) and sform)):
            # skip if only 1 of target or source is given
            logging.info(u'skipping %d:%d because incomplete LM: tform=%s sform=%s',
                         testItemNo, sentNo, pprint.pformat(tform), pprint.pformat(sform))
            continue
        if tconlist and tconc and tconc.strip():
            tcon = tconc.strip()
            if (tcon not in tconlist):
                logging.debug(u'skipping %d:%d because out of target: %s',
                             testItemNo, sentNo, pprint.pformat(line))
                continue
        if (lang=='en') and (u'gun' in unicode(tform, 'utf-8').lower()):
            # hack to skip all the gun control LMs which have inconsistent tconc marking
            logging.debug(u'skipping %d:%d because contains "gun": %s',
                          testItemNo, sentNo, pprint.pformat(line))
            continue
        try:
            # validate spans, or else skip
            tspan = line[5].strip()
            sspan = line[6].strip()
            valstrpos = []
            valstrpos.extend(tspan.split(',',1))
            valstrpos.extend(sspan.split(',',1))
            for stridx in valstrpos:
                nidx = int(stridx)
        except:
            logging.info(u'skipping %d:%d because of invalid target or source spans:%s,%s\n%s',
                          testItemNo,sentNo,tspan,sspan,pprint.pformat(line))
            continue
            

        # first update sentNo and testItemNo so they're correct for this line
        if text != lasttext:
            # this means a brand new sentence
            # first update sentNo
            if sentNo < numSentsPerTI:
                sentNo += 1
            else:
                sentNo = 1
            # if sentNo == 1 , update testItemNo to the next testItem
            # this will be triggered on the first iteration since sentNo was 0 < numSentsPerTI
            if sentNo == 1:
                testItemNo += 1

        if sentNo == 1 and (lasttext != text):
            TIid = "%s%03d" % (lang,testItemNo)
            child = ET.SubElement(root, '{http://www.iarpa.gov/Metaphor/DetectSchema}TestItem', {'id':TIid, 'lang':lang})
            # this is updated above now
            # testItemNo += 1

        # note now testItemNo is set to match the current line being entered , need to get rid of -1
        #csvline = [testItemNo - 1, sentNo] + line
        csvline = [testItemNo, sentNo] + line
        writer.writerow(csvline)
        
        if text != lasttext:
            child2 = ET.SubElement(child, '{http://www.iarpa.gov/Metaphor/DetectSchema}S', {'id':str(sentNo)})
            child2.text = text

        # update the sentence count of the test set element
        child.set('count', str(sentNo))
            # this is taken care of above now after the first text != lasttext
            #if sentNo < numSentsPerTI:
                #sentNo += 1
            #else:
                #sentNo = 1
        # lasttext is used to not repeat sentences in the XML for those with multiple LMs
        lasttext = text
    
    #root.set('count', str(testItemNo - 1))
    root.set('count', str(testItemNo))
    tree = ET.ElementTree(root)
    outxml = "%s.xml" % cmdline.outputfilebase
    tree.write(outxml, xml_declaration=True, encoding='utf-8', method="xml")




if __name__ == "__main__":
    status = main()
    sys.exit(status)
