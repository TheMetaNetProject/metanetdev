#!/usr/bin/env python
# encoding: utf-8
'''
Tool for generating a source concept to schema mapping table in CSV format.

jhong
'''
import sys, os, codecs
import logging, re, argparse
from mnrepository.cnmapping import ConceptualNetworkMapper
from mnrepository.metanetrdf import MetaNetRepository
from mnanalysis.programsources import ProgramSources
import csv

reload(sys)
sys.setdefaultencoding('utf-8')

# default file to load up

def main():
    # Code for generating the cache
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Load Program Sources and generate new table with mappings to schemas",
        epilog="Note: nothing.")
    parser.add_argument('outputfile', help='CSV output file name')
    cmdline = parser.parse_args() 
    
    logging.basicConfig(level=logging.INFO)
    LANGS=['en','es','ru','fa']
    
    ps = ProgramSources()
    sconcepts = {}
    logging.info('retrieving and processing all source dimensions')
    for ssubd in ps.getAllSSubd():
        if ssubd not in sconcepts:
            sconcepts[ssubd] = {}
            for lang in LANGS:
                sconcepts[ssubd][lang] = set()
                sconcepts[ssubd][lang + '-schemas'] = set()
        for lang in LANGS:
            sconcepts[ssubd][lang].update(ps.getLUs(ssubd, lang))
            
    mr = {}
    mapper = {}
    for lang in LANGS:
        mr = MetaNetRepository(lang)
        mr.initLookups()
        mapper = ConceptualNetworkMapper(lang)
        logging.info('processing all schemas in %s', lang)
        for row in mr.getSchemas():
            schema = row.schema
            ssubd = mapper.getSourceDimensionFromSchemas([schema])
            if ssubd=='NULL.ALL':
                continue
            schemaName = mr.getNameString(schema)
            sconcepts[ssubd][lang+'-schemas'].add(schemaName)

    logging.info('writing to outputfile %s',cmdline.outputfile)
    with codecs.open(cmdline.outputfile, 'wb', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        header = ['concept', 'dimension']
        for lang in LANGS:
            header.append(lang+' words')
            header.append(lang+' schemas')
        csvwriter.writerow(header)
        for ssubd in sorted(sconcepts.keys()):
            scon, sdim = ssubd.split('.',1)
            row = [scon, sdim]
            for lang in LANGS:
                wlist = u', '.join(sorted(list(sconcepts[ssubd][lang])))
                slist = u', '.join(sorted(list(sconcepts[ssubd][lang+'-schemas'])))
                row.append(wlist)
                row.append(slist)
            csvwriter.writerow(row)
    
if __name__ == '__main__':
    status = main()
    sys.exit(status)
