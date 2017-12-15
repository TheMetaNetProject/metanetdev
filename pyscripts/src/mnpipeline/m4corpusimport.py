#!/usr/bin/env python
'''
Given a domain name (abbreviation), retrieve seeds from wiki,
find metaphors, retrieve example sentences, and import into
the wiki.

Created on April 16, 2013
@jhong@ICSI.Berkeley.EDU
'''

import os
import sys
import argparse
import subprocess

domains = ['ei','gov','test']
subdomains = {
    'poverty':'ei',
    'taxation':'ei',
    'wealth':'ei',
    'education':'ei'}
steps = ['getseeds','extract','createwiki','importwiki']

def main():
    """
    Main processing for testset2json
    """
    global subdomains,steps
    cmdline = process_command_line()

    # this is like ei, or gov
    seedid = cmdline.domain

    # control flow variables
    dogetseeds = True
    doextract = True
    docreatewiki = True
    doimportwiki = True

    if cmdline.skipto=='extract':
        dogetseeds = False
    elif cmdline.skipto=='createwiki':
        dogetseeds = False
        doextract = False
    elif cmdline.skipto=='importwiki':
        dogetseeds = False
        doextract = False
        docreatewiki = False

    # call getseeds
    getseedscmd = ["getseedsfromwiki"]
    if cmdline.subdomain:
        seedid = cmdline.subdomain
        if subdomains[cmdline.subdomain] != cmdline.domain:
            raise Exception('Incompatible subdomain and domain')
        getseedscmd.append("-b")
        getseedscmd.append(cmdline.subdomain)
    getseedscmd.append(cmdline.domain)
    if dogetseeds:
        subprocess.call(getseedscmd)
        
    # call metaphor extractor
    if doextract:
        subprocess.call(["extractmetaphorsfromcorpora","-s",seedid,"-x"])

    # retrieve sentences for wiki import
    createwikicmd = ["createwikiimport","-g",seedid]
    langs = ["en","es","ru"]
    for l in langs:
        createwikicmd.append("output."+l+"."+seedid+".txt")
    if docreatewiki:
        subprocess.call(createwikicmd)

    # do import into wiki
    if doimportwiki:
        for l in langs:
            filename = os.getcwd()+"/"+"output."+l+"."+seedid+".txt.wiki"
            subprocess.call(["python",
                             "metapagefromfile.py",
                             "-lang:"+l,
                             "-mergetemplates",
                             "-notitle",
                             "-putthrottle:1",
                             "-start:xxxx",
                             "-end:yyyy",
                             "-file:"+filename],cwd=cmdline.pywiki)
    return 0

def process_command_line():
    """
    Return a command line parser object
    """
    global domains,subdomains,steps
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Given a domain name (abbreviation), retrieve seeds"\
        " from wiki, find metaphors, retrieve example sentences, and"\
        " import into the wiki.",
        epilog="Note: intermediate files, including seeds, are generated"\
        " in the current working directory")
    
    # required (positional) args
    parser.add_argument("-d","--domain", dest="domain",
                        help="Target domain abbreviation",
                        choices=domains)
    parser.add_argument("-w","--pywiki", dest="pywiki",
                        help="Path to pywiki installation",
                        default="/u/metanet/repository/pywikipedia")
    parser.add_argument("-b","--subdomain", dest="subdomain",
                        help="Target subdomain abbreviation",
                        choices=subdomains.keys())
    parser.add_argument("-k","--skip-to",dest="skipto",
                        help="Skip to a specific step",
                        choices=steps)
    cmdline = parser.parse_args()
    return cmdline


if __name__ == "__main__":
    status = main()
    sys.exit(status)
