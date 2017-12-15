#!/usr/bin/env python
"""
   Script to convert verb and noun clusters to JSON with an index
   nclusters is and object that takes cluster numbers to a list
   of nouns in that cluster number
   nindex takes nouns to the cluster number it is in
   the same structure applies for verbs

   jhong@icsi.berkeley.edu
"""
import argparse
import json
import sys
import re
import codecs

def main():
    """
    Main processing for jsonsizeclusters
    """
    cmdline = process_command_line()

    # Process NOUNS
    nounf = codecs.open(cmdline.nounfile,"r", encoding="utf-8")
    currentCluster = 0
    ncluster = []
    nclusters = {}
    nindex = {}
    if cmdline.format:
        # this format has clusters all on one line
        for line in nounf:
            cm = re.search('^cluster(\d+):?(.*)$',
                           line,re.UNICODE|re.IGNORECASE)
            if cm is None:
                continue
            else:
                currentCluster = int(cm.group(1))
                ncluster = cm.group(2).strip().split()
                for n in ncluster:
                    nindex[n] = currentCluster
                nclusters[currentCluster] = ncluster
    else:
        # this format has the cluster id one one line, followd by content
        # each word on a separate line
        for line in nounf:
            cm = re.search('^Cluster(\d+)$',line,re.UNICODE)
            if (cm is None):
                if currentCluster == 0:
                    continue
                wm = re.search("^\s+'(.+)'$",line,re.UNICODE)
                if wm is None:
                    # it is the end of the current cluster
                    # add clusternumber => nclusters tp nclusters
                    nclusters[currentCluster] = ncluster
                    currentCluster = 0
                    continue
                else:
                    # a word in the cluster, add to list and add to index
                    word = wm.group(1)
                    if word.startswith('&'):
                        # skip words that start with ampersand
                        continue
                    ncluster.append(word)
                    nindex[word] = currentCluster
            else:
                currentCluster = int(cm.group(1))
                ncluster = []

    nounf.close()

    # Process VERBS
    verbf = codecs.open(cmdline.verbfile,"r", encoding="utf-8")
    currentCluster = 0
    vclusters = {}
    vindex = {}
    if cmdline.format:
        # this format has verb clusters all in one line
        for line in verbf:
            cm = re.search('^cluster(\d+):?(.*)$',
                           line,re.UNICODE|re.IGNORECASE)
            if cm is None:
                continue
            else:
                currentCluster = int(cm.group(1))
                vcluster = cm.group(2).strip().split()
                for v in vcluster:
                    vindex[v] = currentCluster
                vclusters[currentCluster] = vcluster
    else:
        # this format has the cluster id on one line and the content
        # all on the following line
        for line in verbf:
            cm = re.search('^ <Cluster id="(\d+)">',line,re.UNICODE)
            if cm is None:
                if line.startswith('----'):
                    currentCluster = 0
                    continue
                elif line.startswith(' ') and currentCluster > 0:
                    cluster = line.strip().split()
                    vclusters[currentCluster] = cluster
                    for v in cluster:
                        vindex[v] = currentCluster
                    currentCluster = 0
            else:
                currentCluster = int(cm.group(1))
    verbf.close()
    data = {}
    data['vclusters'] = vclusters
    data['nclusters'] = nclusters
    data['vindex'] = vindex
    data['nindex'] = nindex
    with codecs.open(cmdline.outputfile, 'w', encoding="utf-8") as outfile:
        json.dump(data, outfile, sort_keys=True, indent=2, ensure_ascii=False)

def process_command_line():
    """
    Return a command line parser object
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Convert verb and noun cluster files into JSON format" \
        "so that scripts can play with the data more easily.  Input files" \
        "must be UTF-8.",
        epilog="")
    
    # required (positional) args
    parser.add_argument("verbfile", help="verb cluster file")
    parser.add_argument("nounfile", help="noun cluster file")
    parser.add_argument("outputfile", help="JSON output file")
    parser.add_argument("-f","--format",action="store_true",
                        help="To indicate an alternate format")
    
    cmdline = parser.parse_args()
    return cmdline


if __name__ == "__main__":
    status = main()
    sys.exit(status)
