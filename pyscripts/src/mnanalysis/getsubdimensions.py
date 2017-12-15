#!/usr/bin/env python
# encoding: utf-8
'''
Tool for converting the subdimensions google docs into a RTF
format tables for Monthly reports sent to IARPA.

jhong
'''

import sys
import os
import csv
import re
import urllib2
import codecs
import argparse
import json
import urllib2
from rtfng import *
from rtfng.PropertySets import TabPropertySet, BorderPropertySet, FramePropertySet, Colour
from rtfng.Elements import Document, StyleSheet, Section
from rtfng.document.paragraph import Paragraph, Table, Cell
from rtfng.document.character import TEXT, Text
from rtfng.Renderer import Renderer

LANGS = {"en": "English",
         "es": "Spanish",
         "fa": "Persian",
         "ru": "Russian"}

class SubdimensionsConverter:
    '''
    subdimensions converter: per language
    '''
    colnames = {"CM#": 0,
                "TARGET": 1,
                "SEMANTIC CLUSTERS": 4,
                "SOURCE SUB-DIMENSIONS": 5,
                "SOURCE": 6,
                "SENTENCE": 1,
                "FRAGMENT": 2,
                "TRANSLATION": 5
                }
    subdimensions = {}
    subdim_glosses = {}
    sentences = []
    
    def __init__(self, lang, cfg, plog):
        self.lang = lang
        self.cfg = cfg
        if lang in plog:
            self.plog = plog[lang]
        else:
            self.plog = {}
        thin_edge  = BorderPropertySet( width=10, style=BorderPropertySet.SINGLE )
        self.thin_frame  = FramePropertySet( thin_edge,  thin_edge,  thin_edge,  thin_edge )

    
    def add_tables(self, section):
        self.get_subdimensions()
        self.get_sentences()
        self.filter_dimensions()
        #
        self.add_subdimensions_table(section)
        self.add_sentences_table(section)        
        
    def add_subdimensions_table(self, section):
        global LANGS
        p = Paragraph( self.ss.ParagraphStyles.Heading1 )
        p.append(TEXT('Proposed Common Program Sources and Source Sub-dimensions ({0})'.format(LANGS[self.lang]),bold=True))
        section.append( p )

        table = Table(TabPropertySet.DEFAULT_WIDTH * 1,
                      TabPropertySet.DEFAULT_WIDTH * 2,
                      TabPropertySet.DEFAULT_WIDTH * 3,
                      TabPropertySet.DEFAULT_WIDTH * 4,
                      TabPropertySet.DEFAULT_WIDTH * 3 )
              
        h1 = self.cell("CM#",True)
        h2 = self.cell("Target",True)
        h3 = self.cell("Semantic Clusters",True)
        h4 = self.cell("Source Sub-dimensions",True)
        h5 = self.cell("Source",True)
        table.AddRow(h1,h2,h3,h4,h5)
        for id in sorted(self.subdimensions, key=lambda key: float(key)):
            color=None
            # if there is a previous log, color new things red
            if self.plog:
                color=self.ss.Colours.Red
                if 'subdimensions' in self.plog:
                    if id in self.plog['subdimensions']:
                        color=None
            c1 = self.cell(id,False,color)
            c2 = self.cell(self.subdimensions[id][0],False,color)
            c3 = self.cell(self.subdimensions[id][1],False,color)
            c4 = self.cell(self.subdimensions[id][2],False,color)
            c5 = self.cell(self.subdimensions[id][3],False,color)
            table.AddRow(c1,c2,c3,c4,c5)
            if (self.lang=='fa') and (id in self.subdim_glosses):
                t1 = self.cell('',False,color)
                t2 = self.cell(self.subdim_glosses[id][0],False,color)
                t3 = self.cell(self.subdim_glosses[id][1],False,color)
                t4 = self.cell(self.subdim_glosses[id][2],False,color)
                t5 = self.cell(self.subdim_glosses[id][3],False,color)
                table.AddRow(t1,t2,t3,t4,t5)
        section.append(table)

    def cell(self,text,bold=False,color=None):
        return Cell(Paragraph(self.ss.ParagraphStyles.Normal,
                              TEXT(rtf_encode(text),bold=bold,colour=color)),
                    self.thin_frame)

    def add_sentences_table(self, section):
        global LANGS
        p = Paragraph( self.ss.ParagraphStyles.Heading1 )
        p.append(TEXT('Example Sentences ({0})'.format(LANGS[self.lang]),bold=True))
        section.append( p )
        
        table = Table(TabPropertySet.DEFAULT_WIDTH * 1,
                      TabPropertySet.DEFAULT_WIDTH * 9,
                      TabPropertySet.DEFAULT_WIDTH * 3)
        
        thin_edge  = BorderPropertySet( width=10, style=BorderPropertySet.SINGLE )
        thick_edge = BorderPropertySet( width=80, style=BorderPropertySet.SINGLE )

        thin_frame  = FramePropertySet( thin_edge,  thin_edge,  thin_edge,  thin_edge )
        thick_frame = FramePropertySet( thick_edge, thick_edge, thick_edge, thick_edge )
        mixed_frame = FramePropertySet( thin_edge,  thick_edge, thin_edge,  thick_edge )
        
        h1 = self.cell("CM#",True)
        h2 = self.cell("Sentence",True)
        h3 = self.cell("Fragment",True)
        table.AddRow(h1,h2,h3)
        for (id, sent, frag, trans) in sorted(self.sentences,key=lambda key: float(key[0])):
            color=None
            # if there is a previous log, color new things red
            if self.plog:
                color=self.ss.Colours.Red
                if 'sentences' in self.plog:
                    for (lid, lsent, lfrag) in self.plog['sentences']:
                        if (rtf_encode(id)==lid) and (rtf_encode(sent)==lsent) and (rtf_encode(frag)==lfrag):
                            color=None
                            break
            c1 = self.cell(id, False, color)
            c2 = self.cell(sent, False, color)
            c3 = self.cell(frag, False, color)
            table.AddRow(c1,c2,c3)
            # put sentence translation on next line for non-EN and if trans is present
            if (self.lang != "en") and trans:
                c1 = self.cell("", False, color)
                c2 = self.cell(trans, False, color)
                c3 = self.cell("", False, color)
                table.AddRow(c1,c2,c3)
        section.append(table)

    def filter_dimensions(self):
        usednos = {}
        for (cmno, sent, frag, trans) in self.sentences:
            usednos[cmno] = 1
        for cmno in self.subdimensions.keys():
            if cmno not in usednos:
                del self.subdimensions[cmno]
            
    
    def get_subdimensions(self):
        sd_url = self.get_tab_url(self.cfg["gdoc_url"],
                                  self.cfg["subdimtab"])
        page = urllib2.urlopen(sd_url)
        reader = csv.reader(page)
        rownum = -1
        subdlist = {}
        subdgloss= {}
        c = self.colnames
        for row in reader:
            rownum += 1
            if rownum < 2:
                continue
            cmno = row[c["CM#"]]
            target = row[c["TARGET"]]
            semcl = row[c["SEMANTIC CLUSTERS"]]
            srcsd = row[c["SOURCE SUB-DIMENSIONS"]]
            src = row[c["SOURCE"]]
            # include only if all fields are filled
            if cmno and target and semcl and srcsd and src:
                # skip if the ID num is not float-compatible
                # or if the ID has already been processed
                try:
                    float(cmno)
                except:
                    continue
                if cmno in subdlist:
                    # if the cm id is already in there, then skip it,
                    # except if it is Persian, then store it as glosses
                    if self.lang=='fa':
                        subdgloss[cmno] = (target,semcl,srcsd,src)
                    continue
                subdlist[cmno] = (target,semcl,srcsd,src)
        self.subdimensions = subdlist
        self.subdim_glosses = subdgloss
    
    def get_sentences(self):
        '''
        should run after running get_subdimensions
        '''
        sentences = []
        for tabname in self.cfg['exampletabs']:
            tab_url = self.get_tab_url(self.cfg["gdoc_url"],
                                       self.cfg["exampletabs"][tabname])
            page = urllib2.urlopen(tab_url)
            reader = csv.reader(page)
            rownum = -1
            c = self.colnames
            for row in reader:
                rownum += 1
                if rownum == 0:
                    continue
                cmno = row[c["CM#"]]
                sent = row[c["SENTENCE"]]
                frag = row[c["FRAGMENT"]]
                trans = None
                if self.lang != "en":
                    trans = row[c["TRANSLATION"]]
                if cmno and sent and frag:
                    if ',' in cmno:
                        cmnos = cmno.split(',')
                    else:
                        cmnos = [cmno]
                    for cmn in cmnos:
                        if cmn in self.subdimensions:
                            # skip if the ID number is not float-compatible
                            try:
                                float(cmn)
                            except:
                                continue
                            sentences.append((cmn,sent,frag,trans))
        self.sentences = sentences
    
    def get_tab_url(self, doc_url, tab_number_str):
        url = doc_url + "&single=true&gid={0}&output=csv".format(tab_number_str)
        return url
    
    def add_to_json(self,jsondoc):
        jsondoc[self.lang] = {'subdimensions': self.subdimensions,
                              'sentences': self.sentences}
    
    def set_ss(self, ss):
        self.ss = ss

class SubdimensionsToWikiConverter:
    '''
    subdimensions converter: per language
    '''
    subdcolnames = {"CM#": 0,
                    "Metaphor Family": 1,
                    "General Target Schema": 2,
                    "Specific Target Schema": 3,
                    "Lexical Units in Specific Schema": 4,
                    "Specific Source Schema": 5,
                    "General Source Schema": 6,
                    "Specific Metaphor Name": 8,
                    "General Metaphor Name": 9
                    }
    excolnames= {"CM#": 0,
                 "Sentence": 1,
                 "Fragment": 2,
                 "Provenance": 3
                 }
    cmid_lookup = {}
    cms = {}
    schemas = {}
    lms = {}
    
    def __init__(self, lang, cfg):
        global LANGS
        self.lang = lang
        self.cfg = cfg
        self.language = LANGS[lang]
        self.cmid_lookup = {}
        self.cms = {}
        self.schemas = {}
        self.lms = {}
    
    def create_cms_schemas(self):
        sd_url = self.get_tab_url(self.cfg["gdoc_url"],
                                  self.cfg["subdimtab"])
        page = urllib2.urlopen(sd_url)
        reader = csv.reader(page)
        rownum = -1
        subdlist = {}
        c = self.subdcolnames
        schemas = {}
        cms = {}
        for row in reader:
            rownum += 1
            if rownum < 2:
                # skip the 2 header rows
                continue
            skiprow = False
            # skip if any of the columns of interest are blank
            for colnum in c.values():
                if not row[colnum]:
                    skiprow = True
                    break
                if self.lang == "fa":
                    if re.match(ur'[A-Za-z]+', row[colnum], flags=re.U):
                        skiprow = True
                        break
            if skiprow:
                continue

            cmid = row[c["CM#"]].strip()
            # skip if ID was already processed
            if cmid in self.cmid_lookup:
                continue
            
                
            
            # general and specific target schemas
            gtgschema = name_filter(rtf_encode(row[c["General Target Schema"]])).strip()
            stgschema = name_filter(rtf_encode(row[c["Specific Target Schema"]])).strip()
            sfam = self.get_schema_family_name(name_filter(rtf_encode(row[c["Metaphor Family"]])))            
            if gtgschema not in schemas:
                schemas[gtgschema] = {"subcase of":set(),
                                      "family":set(),
                                      "lus":set()}
            if stgschema not in schemas:
                schemas[stgschema] = {"subcase of":set(),
                                      "family":set(),
                                      "lus":set()}
            schemas[gtgschema]["family"].add(sfam)
            schemas[stgschema]["family"].add(sfam)
            schemas[stgschema]["subcase of"].add(gtgschema)

            # general and specific source schemas
            gsrschema = name_filter(rtf_encode(row[c["General Source Schema"]])).strip()
            ssrschema = name_filter(rtf_encode(row[c["Specific Source Schema"]])).strip()
            srlus = re.split(ur'[,;]',rtf_encode(row[c["Lexical Units in Specific Schema"]]).strip(),flags=re.U)
            if gsrschema not in schemas:
                schemas[gsrschema] = {"subcase of":set(),
                                      "family":set(),
                                      "lus":set()}
            if ssrschema not in schemas:
                schemas[ssrschema] = {"subcase of":set(),
                                      "family":set(),
                                      "lus":set()}
            schemas[ssrschema]["subcase of"].add(gsrschema)
            for lu in srlus:
                luname = name_filter(lu.strip())
                if luname:
                    schemas[ssrschema]["lus"].add(luname)
            
            # general and specific metaphors
            gmet = name_filter(rtf_encode(row[c["General Metaphor Name"]])).strip()
            smet = name_filter(rtf_encode(row[c["Specific Metaphor Name"]])).strip()
            mfam = self.get_metaphor_family_name(name_filter(rtf_encode(row[c["Metaphor Family"]])))
            if gmet not in cms:
                cms[gmet] = {"target":gtgschema,
                             "source":gsrschema,
                             "family": set(),
                             "level": "General",
                             "target-source subcase of": set(),
                             "target subcase of": set(),
                             "source subcase of": set()}
            if smet not in cms:
                cms[smet] = {"target":stgschema,
                             "source":ssrschema,
                             "family": set(),
                             "level": "Specific",
                             "target-source subcase of": set(),
                             "target subcase of": set(),
                             "source subcase of": set()}
            cms[gmet]["family"].add(mfam)
            cms[smet]["family"].add(mfam)
            if gtgschema != stgschema:
                if gsrschema != ssrschema:
                    cms[smet]["target-source subcase of"].add(gmet)
                else:
                    cms[smet]["target subcase of"].add(gmet)
            elif gsrschema != ssrschema:
                cms[smet]["source subcase of"].add(gmet)
            
            # make id to cm lookup
            self.cmid_lookup[cmid] = smet
        self.cms = cms
        self.schemas = schemas

    def get_metaphor_family_name(self, name):
        if self.lang=="en":
            return name + u' metaphors'
        if self.lang=="es":
            return u'Metáforas de '+name
        if self.lang=="ru":
            return u'Метафоры '+name
        if self.lang=="fa":
            return u'استعاره های '+name
    
    def get_schema_family_name(self, name):
        if self.lang=="en":
            return name + u' schemas'
        if self.lang=="es":
            return u'Esquemas de '+name
        if self.lang=="ru":
            return u'Схемы '+name
        if self.lang=="fa":
            return u'طرحواره '+name
    
    def create_lms(self):
        '''
        should run after running create_cms_schemas
        '''
        lms = {}
        for tabname in self.cfg['exampletabs']:
            tab_url = self.get_tab_url(self.cfg["gdoc_url"],
                                       self.cfg["exampletabs"][tabname])
            page = urllib2.urlopen(tab_url)
            reader = csv.reader(page)
            rownum = -1
            c = self.excolnames
            for row in reader:
                rownum += 1
                if rownum == 0:
                    continue
                cmno = row[c["CM#"]]
                sent = rtf_encode(row[c["Sentence"]])
                frag = rtf_encode(row[c["Fragment"]])
                prov = rtf_encode(row[c["Provenance"]])
                if cmno and sent and frag:
                    example = (sent,prov)
                    lmlist = re.split(ur'[,;]',frag,flags=re.U)
                    for lm in lmlist:
                        lmname = lm.strip()
                        if lmname not in lms:
                            lms[lmname] = {"instance of cm": set(),
                                           "examples":set()}
                        cmnos = cmno.split(',')
                        for cmid in cmnos:
                            cmid = cmid.strip()
                            if cmid in self.cmid_lookup:
                                lms[lmname]["instance of cm"].add(self.cmid_lookup[cmid])
                        lms[lmname]["examples"].add(example)
        self.lms = lms
    
    def get_tab_url(self, doc_url, tab_number_str):
        url = doc_url + "&single=true&gid={0}&output=csv".format(tab_number_str)
        return url
        
    def get_wiki_pages(self):
        wdoc = []
        
        # Generate schema wiki pages
        for schemaname in self.schemas:
            wdoc.append(u'xxxx')
            wdoc.append(u'\'\'\'Schema:'+schemaname+u'\'\'\'')
            wdoc.append(u'{{Schema')
            if len(self.schemas[schemaname]['family']) > 0:
                wdoc.append(u'|Family='+u','.join(self.schemas[schemaname]["family"]))            
            wdoc.append(u'|Tags=Program sources')
            snum = 0
            for relschema in self.schemas[schemaname]['subcase of']:
                if snum == 0:
                    wdoc.append(u'|Related schemas={{Related schema')
                else:
                    wdoc.append(u'}}{{Related schema')
                wdoc.append(u'|Related schema.Relation type=is subcase of')
                wdoc.append(u'|Related schema.Name='+relschema)
                snum += 1
            if snum > 0:
                wdoc.append(u'}}')
            lnum = 0
            for lu in self.schemas[schemaname]['lus']:
                if lnum == 0:
                    wdoc.append(u'|Relevant LUs={{LUs')
                else:
                    wdoc.append(u'}}{{LUs')
                wdoc.append(u'|LUs.Language='+self.language)
                wdoc.append(u'|LUs.Lemmas='+lu)
                lnum += 1
            if lnum > 0:
                wdoc.append(u'}}')
            wdoc.append(u'|Status=auto imported')
            wdoc.append(u'}}')
            wdoc.append(u'yyyy')
        
        # Generate metaphor wiki pages
        for cmname in self.cms:
            wdoc.append(u'xxxx')
            wdoc.append(u'\'\'\'Metaphor:'+cmname+u'\'\'\'')
            wdoc.append(u'{{Metaphor')
            if len(self.cms[cmname]['family']) > 0:
                wdoc.append(u'|Family='+u','.join(self.cms[cmname]["family"]))
            wdoc.append(u'|Metaphor Level='+self.cms[cmname]["level"])
            wdoc.append(u'|Target schema='+self.cms[cmname]["target"])
            wdoc.append(u'|Source schema='+self.cms[cmname]["source"])
            wdoc.append(u'|Tags=Program sources')
            mnum = 0
            for relmet in self.cms[cmname]['target-source subcase of']:
                if mnum == 0:
                    wdoc.append(u'|Related metaphors={{Related metaphor')
                else:
                    wdoc.append(u'}}{{Related metaphor')
                wdoc.append(u'|Related metaphor.Relation type=is both a source and target subcase of')
                wdoc.append(u'|Related metaphor.Name='+relmet)
                mnum += 1
            for relmet in self.cms[cmname]['target subcase of']:
                if mnum == 0:
                    wdoc.append(u'|Related metaphors={{Related metaphor')
                else:
                    wdoc.append(u'}}{{Related metaphor')
                wdoc.append(u'|Related metaphor.Relation type=is a target subcase of')
                wdoc.append(u'|Related metaphor.Name='+relmet)
                mnum += 1
            for relmet in self.cms[cmname]['source subcase of']:
                if mnum == 0:
                    wdoc.append(u'|Related metaphors={{Related metaphor')
                else:
                    wdoc.append(u'}}{{Related metaphor')
                wdoc.append(u'|Related metaphor.Relation type=is a source subcase of')
                wdoc.append(u'|Related metaphor.Name='+relmet)
                mnum += 1
            if mnum > 0:
                wdoc.append(u'}}')
            wdoc.append(u'|Status=auto imported')
            wdoc.append(u'}}')
            wdoc.append(u'yyyy')
            
        # Generate LM pages
        for lmname in self.lms:
            wdoc.append(u'xxxx')
            wdoc.append(u'\'\'\'Linguistic metaphor:'+lmname+u'\'\'\'')
            wdoc.append(u'{{Linguistic metaphor')
            wdoc.append(u'|Type=extracted')
            wdoc.append(u'|Tags=Program sources')
            lm = self.lms[lmname]
            if len(lm['instance of cm']) > 0:
                wdoc.append(u'|Instance of metaphor='+u','.join([u'Metaphor:'+x for x in lm['instance of cm']]))
            enum = 0
            for (sent,prov) in lm['examples']:
                if enum == 0:
                    wdoc.append(u'|Examples={{Example')
                else:
                    wdoc.append(u'}}{{Example')
                wdoc.append(u'|Example.Language='+self.language)
                wdoc.append(u'|Example.Text='+sent)
                wdoc.append(u'|Example.Provenance='+prov)
                enum += 1
            if enum > 0:
                wdoc.append(u'}}')
            wdoc.append(u'|Status=auto imported')
            wdoc.append(u'}}')
            wdoc.append(u'yyyy')
        return wdoc

def main():
    """
    Main processing for command line invocation
    """
    cmdline = process_command_line()
    cfg = json.load(file(cmdline.configfile))
    if cmdline.lang:
        langs = [cmdline.lang]
    else:
        langs = LANGS
    
    if cmdline.wiki:
        for lang in sorted(langs):
            conv = SubdimensionsToWikiConverter(lang,cfg[lang])
            conv.create_cms_schemas()
            conv.create_lms()
            ofname = lang + '_' + cmdline.outfile
            lines = conv.get_wiki_pages()
            with codecs.open(ofname,"w",encoding="utf-8") as of:
                for line in lines:
                    print >> of, line
    else:
        plog = {}
        if cmdline.prevlog:
            plog = json.load(file(cmdline.prevlog),encoding='utf-8')
        doc = Document()
        section = Section()
        doc.Sections.append(section)
        ss = doc.StyleSheet
        logdoc = {}
        for lang in sorted(langs):
            conv = SubdimensionsConverter(lang,cfg[lang],plog)
            conv.set_ss(ss)
            conv.add_tables(section)
            conv.add_to_json(logdoc)
        DR = Renderer()
        ofile = codecs.open(cmdline.outfile, "w", encoding="utf-8")
        DR.Write( doc, ofile )
        lfile = codecs.open(cmdline.outfile+'.log', "w", encoding="utf-8")
        json.dump(logdoc, lfile, indent=2, encoding='utf-8')
    
    return 0

def rtf_encode(unistr):
    return unicode(unistr,encoding='utf-8')

def name_filter(str):
    return re.sub(ur'\n',ur'',re.sub(ur' \([^\(\)]*\)',ur'',str,re.U),re.U)

def process_command_line():
    """
    Return a command line parser object
    """
    global LANGS
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Retrieves sub-dimensions from google docs"\
        " based on the contents of the configfile.",
        epilog="")

    # required (positional) args
    parser.add_argument("configfile",
                        help="configuration file")
    parser.add_argument("outfile",
                        help="output file name")
    parser.add_argument("-l","--lang",
                        help="only do this language",
                        choices=LANGS.keys())
    parser.add_argument("-p","--previous-log",dest="prevlog",
                        help="log file from previous run "\
                        "for coloring new items red")
    parser.add_argument("-w","--wiki",dest="wiki",
                        help="convert for wiki import rather than RTF",
                        action="store_true")
    
    cmdline = parser.parse_args()
    
    return cmdline

if __name__ == '__main__':
    status = main()
    sys.exit(status)
