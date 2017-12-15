#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
m4detect
search for metaphors in input text documents
input and output in IARPA specified XML formats

Created by Jisup Hong (jhong@icsi.berkeley.edu)
'''

import subprocess
import xml.etree.ElementTree as et
import time
import argparse
import os
import sys
import codecs
import shutil
import json
from cmsextractor import postextraction
from mnformats import mnjson
import re
from lmsextractor.externalExtr import PersianMetaphorExtractor

SEPARATOR = '____'
VERBOSE = False
MIN_SCORE = 200000

def main():
    global SEPARATOR, MIN_SCORE
    cmdline = process_command_line()
    cwd = os.getcwd()
    
    if cmdline.intdir:
        intdir = cmdline.intdir
    else:
        intdir = "./int_"+os.path.basename(cmdline.infile)
    
    # if the intermediate directory exists, first delete it
    if os.path.exists(intdir):
        shutil.rmtree(intdir)
    
    os.makedirs(intdir)
    shutil.copy(cmdline.infile,intdir)

    # change to intermediate files dir
    os.chdir(intdir)
    intpath = os.getcwd()
    if intpath.endswith('/')==False:
        intpath += '/'
    
    jsonfiles = subprocess.check_output(["testset2json",
                                         "-p",
                                         "-d",
                                         SEPARATOR,
                                         cmdline.infile]).splitlines()
    jsonfiles.sort()

    METADNS = "http://www.iarpa.gov/Metaphor/DetectSchema"
    XSINS = "http://www.w3.org/2001/XMLSchema-instance"
    M4SCHEMA = 'http://www.iarpa.gov/Metaphor/DetectSchema m4detectSchema_11.xsd'
    
    et.register_namespace("metad",METADNS)
    et.register_namespace("xsi",XSINS)
    
    rsroot = et.Element('metad:ResultSet');
    rsroot.set('xsi:schemaLocation',M4SCHEMA)
    rsroot.set('xmlns:metad',METADNS)
    rsroot.set('xmlns:xsi',XSINS)
    rsroot.set('teamId',cmdline.teamname)
    rscount = 0

    logroot = et.Element('metad:LogFile');
    logroot.set('xsi:schemaLocation',M4SCHEMA)
    logroot.set('xmlns:metad',METADNS)
    logroot.set('xmlns:xsi',XSINS)
    logroot.set('teamId',cmdline.teamname)
    logcount = 0
    
    logentry = et.SubElement(logroot, 'metad:TestStartTime')
    logentry.text = get_time()
    
    processor = postextraction.SimpleWordlistSystem(cmdline.extdir)
    prdir = None
    if cmdline.extdir:
        prdir = cmdline.extdir + '/persian'
    persianextractor = PersianMetaphorExtractor(prdir)
    
    for jfile in jsonfiles:
        lmflag = "0"
        lmsentno = "999"
        lmtarget = ""
        lmsource = ""
        
        # process filename
        (fbase,textid) = os.path.splitext(jfile)[0].split(SEPARATOR)

        # get lang from inside
        jfdoc = mnjson.loadfile(jfile)
        lang = jfdoc['lang']

        # start log entry
        logentry = et.SubElement(logroot, 'metad:LogEntry')
        logentry.set('id',textid)

        # record start time
        logstart = et.SubElement(logentry, 'metad:StartTime')
        logstart.text = get_time()
        print >> sys.stderr, logstart.text,"- starting processing on",textid
        
        # run pipeline
        result = et.SubElement(rsroot, 'metad:Result')
        result.set('id',textid)

        procfilename = 'processed.'+jfile
        errfilename = 'errfile.'+jfile
        errfile = codecs.open(errfilename,"w+",encoding='utf-8')
        
        seed_start_time = time.time()
        
        parsemetcmd = ['parsemet',
                       '-l',lang,
                       '-s','seeds.ei',
                       '-j',jfile]
        russiancmd = ['pipeline_russian',
                      '-f',jfile,
                      '-t','json',
                      '-o',procfilename]
                
        if cmdline.extdir:
            parsemetcmd.append('-d')
            parsemetcmd.append(cmdline.extdir+'/seeds')

        if lang=="en":
            parsemetcmd.insert(1, '-x')
            procfile = codecs.open(procfilename,"w",encoding='utf-8')
            subprocess.call(parsemetcmd,
                            stdout=procfile,
                            stderr=errfile)
            procfile.flush()
            procfile.close()
        elif (lang=="es") or (lang=="ru"):
            procfile = codecs.open(procfilename,"w",encoding='utf-8')
            subprocess.call(parsemetcmd,
                            stdout=procfile,
                            stderr=errfile)
            procfile.flush()
            procfile.close()
        elif lang=="fa":
            jobj = mnjson.loadfile(jfile)
            jobj = persianextractor.find_LMs(jobj)
            persianextractor.writejson(jobj, procfilename)

        procfile = codecs.open(procfilename,"r",encoding='UTF-8')

        seed_elapsed_time = time.time() - seed_start_time
        msgpf("SBS processing time: %fs",(seed_elapsed_time))

        # load the resulting json file
        # do post_processing
        word_start_time = time.time()
        doc = processor.post_process(json.load(procfile,encoding='UTF-8'))
        word_elapsed_time = time.time() - word_start_time
        msgpf("SWS processing time: %fs",(word_elapsed_time))
        
        # save the resulting json for debugging
        mnjson.writefile(procfilename+'.post', doc)
        
        highscorelmlist = []
        for sentence in doc['sentences']:
            if 'lms' in sentence:
                lmlist = sentence['lms']
                if len(lmlist) < 1:
                    continue
                highscorelmlist.append((lmlist[0],sentence))
        
        # choose the highest scoring lm from all the sentences in the json
        if len(highscorelmlist) > 0:
            highscorelmlist.sort(key=lambda lmtuple:lmtuple[0]['score'], reverse=True)
            (lm, sentence) = highscorelmlist[0]
            if lm['score'] >= MIN_SCORE:
                lmflag = "1"
                lmsentno = sentence['id'].split(':')[-1]
                # use text if there, or lemma if not
                if 'text' in lm['target']:
                    lmtarget = lm['target']['text']
                else:
                    lmtarget = lm['target']['lemma']
                    tmatch = re.search('^(\w+)\.(a|v|n|j)$',lmtarget)
                    if tmatch:
                        lmtarget = tmatch.group(1)
                if 'text' in lm['source']:
                    lmsource = lm['source']['text']
                else:
                    lmsource = lm['source']['lemma']
                    smatch = re.search('^(\w+)\.(a|v|n|j)$',lmsource)
                    if smatch:
                        lmsource = smatch.group(1)

        # check doc if LMs were found
        # currently reports only 1st LM match in the whole text
        rsflag = et.SubElement(result,'metad:LmFlag')
        rsflag.text = lmflag
        rssent = et.SubElement(result,'metad:LmSentence')
        rssent.text = lmsentno
        rstarget = et.SubElement(result,'metad:LmTargetText')
        rstarget.text = lmtarget
        rssource = et.SubElement(result,'metad:LmSourceText')
        rssource.text = lmsource
        rscount += 1

        # record end time
        logend = et.SubElement(logentry, 'metad:EndTime')
        logend.text = get_time()
        print >> sys.stderr, logend.text,"- ended processing on",textid

        # record processing flag
        logflag = et.SubElement(logentry, 'metad:ProcessingFlag')
        logflag.text = lmflag
        print >> sys.stderr, "Processing flag for",textid,'=',lmflag
        logcount += 1

    logentry = et.SubElement(logroot, 'metad:TestEndTime')
    logentry.text = get_time()

    rsroot.set("count",str(rscount))
    logroot.set("count",str(logcount))
    
    # open the input file to read the test id
    intree = et.parse(cmdline.infile)
    inroot = intree.getroot()
    testid = inroot.get('testId')
    rsroot.set('testId',testid)
    logroot.set('testId',testid)

    # write result file
    tmpoutfile = os.path.basename(cmdline.outfile)
    rstree = et.ElementTree(rsroot)
    rstree.write(tmpoutfile,encoding='UTF-8',xml_declaration=True)
    tmplogfile = os.path.basename(cmdline.logfile)
    logtree = et.ElementTree(logroot)
    logtree.write(tmplogfile,encoding='UTF-8',xml_declaration=True)

    # change back to original cwd
    os.chdir(cwd)

    # copy out pretty printed file using xmllint
    finaloutfile = codecs.open(cmdline.outfile,"w",encoding='utf-8')
    subprocess.call(['xmllint','--format',intpath+tmpoutfile],
                    stdout=finaloutfile)
    finallogfile = codecs.open(cmdline.logfile,"w",encoding='utf-8')
    subprocess.call(['xmllint','--format',intpath+tmplogfile],
                    stdout=finallogfile)
    finaloutfile.flush()
    finallogfile.flush()
    return 0

def get_time():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())

def msgpf(msgbase, tuple):
    global VERBOSE
    if VERBOSE:
        msg = msgbase % tuple
        print msg

def process_command_line():
    """
    Return a command line parser object
    """
    global IXSCHEMA, VERBOSE
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Reads IARPA format input XML file and runs LM" \
        " detection.  Outputs results as well as log information in" \
        " IARPA specified XML formats.",
        epilog="")
    
    # required (positional) args
    parser.add_argument("infile", help="TestSet.xml")
    parser.add_argument("outfile", help="ResultSet.xml")
    parser.add_argument("logfile", help="LogFile.xml")
    parser.add_argument("-t","--team",
                        help="To change the team name specified in"\
                        " the output files.",default="ICSI",dest="teamname")
    parser.add_argument("-i","--intermediate-files-dir",
                        help="To change the directory on the system "\
                        "where intermediate files are generated. "\
                        "(default: ./int_<infile>)",
                        dest="intdir")
    parser.add_argument("-v","--verbose",dest="verbose",
                        help="To print more status messages",
                        action="store_true")
    parser.add_argument("-d","--resource-dir",dest="extdir",
                        help="To override directory to find resources",
                        default=None)
    cmdline = parser.parse_args()
    VERBOSE = cmdline.verbose
    return cmdline

if __name__ == "__main__":
    status = main()
    sys.exit(status)
