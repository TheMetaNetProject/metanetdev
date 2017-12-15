#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
m4extract
search for metaphors in input text documents
input and output in MetaNet JSON formats

Created by Jisup Hong (jhong@icsi.berkeley.edu)
'''

import subprocess, gzip
import time
import argparse
import os
import stat
import sys
import codecs
import shutil
from cmsextractor import postextraction
from mnformats import mnjson
from lmsextractor.externalExtr import PersianMetaphorExtractor
from multiprocessing import Pool

PROCESSES = 5
CHUNKSIZE = 1

reload(sys)
sys.setdefaultencoding("UTF-8")  # @UndefinedVariable

SEPARATOR = '____'

def main():
    global PROCESSES, CHUNKSIZE
    cmdline = process_command_line()
    if cmdline.parallel > 1:
        poolitems = []
        for infilename in cmdline.infiles:
            poolitems.append((infilename,cmdline))
            # initialize 5 workers
        pool = Pool(cmdline.parallel)
        pool.map(process_one, poolitems, CHUNKSIZE)
    else:
        for infilename in cmdline.infiles:
            process_one((infilename,cmdline))

def process_one((infile, cmdline)):
    
    # file names
    infilebase = os.path.basename(infile)
    intdir = cmdline.intdir+infilebase
    postsbs = infilebase + '.postsbs'
    outfilename = cmdline.outpref+infilebase+cmdline.outsuff
    cmsinfile = infilebase
    
    # skip option
    if cmdline.skipexisting:
        if os.path.exists(outfilename):
            print >> sys.stderr, "Skipping %s because output file already exists." % (infile)
            return
    
    # if the intermediate directory exists, first delete it
    if os.path.exists(intdir):
        if cmdline.force:
            shutil.rmtree(intdir)
    else:
        os.makedirs(intdir)
        shutil.copy(infile,intdir)

    # change to intermediate files dir
    cwd = os.getcwd()
    os.chdir(intdir)

    if cmdline.usesbs:
        run_sbs(infilebase,postsbs,cmdline)
        if infile.endswith('.gz'):
            f_in = open(postsbs, 'rb')
            f_out = gzip.open(postsbs+'.gz', 'wb')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            postsbs += '.gz'
        if cmdline.usecms:
            if os.stat(postsbs)[stat.ST_SIZE] > 0:
                cmsinfile = postsbs
        else:
            shutil.copy(postsbs,outfilename)

    if cmdline.usecms:
        run_cms(cmsinfile,outfilename,cmdline)
            
    shutil.copy(outfilename,cwd)
    os.chdir(cwd)

def run_cms(jfile, procfilename, cmdline):
    processor = postextraction.SimpleConstructionMatchingSystem(cmdline.extdir,None,None,cmdline.verbose)
    doc = processor.post_process(mnjson.loadfile(jfile),
                                 None,
                                 cmdline.matchfield,
                                 cmdline.posfield,
                                 cmdline.reportfield,
                                 cmdline.forcetagger)
    mnjson.writefile(procfilename, doc)


def run_sbs(jfile, procfilename, cmdline):
    
    # bypass if the output file already exists and has non-zero size
    if os.path.exists(procfilename):
        if os.path.getsize(procfilename):
            return 0
    
    errfilename = 'error.'+jfile
    errfile = codecs.open(errfilename,'w+',encoding='utf-8')
    
    #open the file to see what language it is
    lang = cmdline.lang

    seedfile = "seeds."+cmdline.seedext
    parsemetcmd = ['parsemet','-l', lang,'-s', seedfile,'-j', jfile]
    if cmdline.extdir:
        parsemetcmd.append('-d')
        parsemetcmd.append(cmdline.extdir+'/seeds')
    
    if lang=="fa":     
        prdir = None
        if cmdline.extdir:
            prdir = cmdline.extdir + '/persian'
        persianextractor = PersianMetaphorExtractor(prdir)
        jobj = mnjson.loadfile(jfile)
        persianextractor.parse(jobj)
        jobj = persianextractor.find_LMs(jobj)
        persianextractor.writejson(jobj, procfilename)
    else:
        if cmdline.noparse:
            parsemetcmd.append('-n')
        if lang=='en':
            parsemetcmd.append('-x')
        procfile = codecs.open(procfilename,"w",encoding='utf-8')
        subprocess.call(parsemetcmd,
                        stdout=procfile,
                        stderr=errfile)
        procfile.flush()
        procfile.close()

def get_time():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())

def process_command_line():
    """
    Return a command line parser object
    """
    global IXSCHEMA
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Reads MetaNet format input JSON file and runs LM" \
        " detection.  Outputs results in JSON.",
        epilog="")
    
    # required (positional) args
    parser.add_argument("infiles", help="Input file(s) in JSON format",
                        metavar='infile',
                        type=str,
                        nargs='+')
    parser.add_argument("-op","--output-prefix", dest="outpref",
                        help="Output file prefix.  If none is given,"\
                        " output defaults to processed.<infile>",
                        default='processed.')
    parser.add_argument("-os", "--output-suffix", dest="outsuff",
                        help="Output file suffix.",
                        default='')
    parser.add_argument("-i","--intermediate-files-dir-prefix",
                        help="To change the directory on the system "\
                        "where intermediate files are generated.",
                        dest="intdir",
                        default='./int_')
    parser.add_argument("-s","--seed-ext",dest="seedext",
                        help="The extension to use to pick out a "\
                        "seed file from /u/metanet/extraction/seeds (SBS)",
                        default='govei')
    parser.add_argument("-cms","--use-cms",
                        help="Employ cxn matching system",
                        action="store_true",dest="usecms")
    parser.add_argument("-sbs","--use-sbs",
                        help="Employ the seed-based system for en, es, ru and the LCS system for fa",
                        action="store_true",dest="usesbs")
    parser.add_argument("-d","--resources-dir",dest="extdir",
                        help="Override directory where resources are found",
                        default='/u/metanet/extraction')
    parser.add_argument("-f","--force",action="store_true",
                        help="Overwrite existing intermediate files")
    parser.add_argument("-l","--lang",dest="lang",
                        required=True,
                        help="Input file language")
    parser.add_argument("-p","--parallel",
                        default=0,
                        type=int,
                        help="Number of parallel processes to run")
    parser.add_argument("-v","--verbose",
                        action="store_true",
                        help="Display verbose messages")
    parser.add_argument("-n","--noparse",
                        help="Use parse in the JSON rather than invoking parser. (SBS)",
                        action="store_true")
    parser.add_argument("-k","--skip-existing",
                        dest="skipexisting",
                        action="store_true",
                        help="Skip if the output file already exists")
    parser.add_argument('-match','--match-field',
                        dest='matchfield',
                        help='Word dict field to search for matches (CMS)',
                        default=None)
    parser.add_argument('-pos','--pos-field',
                        dest='posfield',
                        help='Word dict field that contains POS tags (CMS)',
                        default=None)
    parser.add_argument('-report','--report-field',
                        dest='reportfield',
                        help='Word dict field to report LM strings from (CMS)',
                        default=None)
    parser.add_argument('-ftag','--force-tagger',
                        dest='forcetagger',
                        action='store_true',
                        help='Override tagger to run, and use the tags generated'\
                        ' instead of the ones in the word array (CMS)')
    cmdline = parser.parse_args()
    return cmdline


if __name__ == "__main__":
    status = main()
    sys.exit(status)
