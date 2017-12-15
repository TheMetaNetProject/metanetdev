#!/usr/bin/env python
"""
NOTE: THIS IS THE OLD VERSION OF FIND_METAPHORS WRITTEN BY CHRIS XIE.
THE PLAN IS TO USE THIS UNTIL THE NEW VERSION IS READY, SINCE
WE NEED TO KEEP PULLING LMS INTO THE REPOSITORY

THIS VERSION RUNS ON A SINGLE SEED

Created on October 24, 2012

This file takes a relation type, a verb-noun pair as a seed, and an output file
name and generates metaphorical expressions based on a clustering algorithm. See
the usage() function for more details.

All of the cluster files and potential metaphor files have already been generated
from a parsed Russian web blog corpus.

@author: ChrisXie
"""

import sys, os, argparse, codecs, subprocess

reload(sys)
sys.setdefaultencoding('utf-8')

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

CLUSTERROOT = '/u/metanet/extraction/clusters'
POT_MET_FILE = {
    'en':{'verb-object':'/u/metanet/corpolexica/EN/bnc-relations/DirectObjRels.txt-uniqed-sorted',
          'verb-subject':'/u/metanet/corpolexica/EN/bnc-relations/SubjectRels.txt-uniqed-sorted'},
    'es':{'verb-object':'/u/metanet/Parsing/Results/GW/es/dobj',
          'verb-subject':'/u/metanet/Parsing/Results/GW/es/subj'},
    'ru':{'verb-object':'/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/verbObjUniq.txt',
          'verb-subject':'/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/verbSubjUniq.txt'}
    }
GRAMRELS = {
    'en': {'verb-subject':'ncsubj',
           'verb-object':'dobj'},
    'es': {'verb-subject':'subj',
           'verb-object':'dobj'},
    'ru': {'verb-subject':'verb-subject',
           'verb-object':'verb-object'}
    }
PARSE_RESULTS_DIR = {'en':'/u/metanet/Parsing/Results/bnc',
                   'es':'/u/metanet/Parsing/Results/GW/es',
                   'ru':'/tscratch/tmp/russian_metaphor_search',
                   'fa':''}

def main():

    global CLUSTERROOT, POT_MET_FILE, GRAMRELS, PARSE_RESULTS_DIR
    parser = cmdline_parser()
    name_space = parser.parse_args()
    args = vars(name_space)

    show_sentences = args['sentences']
    verbose = args['verbose']
    lang = args['language']
    rel_type = args['reltype']
    verb_seed = args['verb']
    noun_seed = args['noun']
    output_file_name = args['output_file_name']
    gramrel = GRAMRELS[lang][rel_type]
    resultscwd = PARSE_RESULTS_DIR[lang]
    
    noun_cluster_file = CLUSTERROOT+"/"+lang+"/Noun_Clusters.txt"
    verb_cluster_file = CLUSTERROOT+"/"+lang+"/Verb_Clusters.txt"
    potential_met_file = POT_MET_FILE[lang][rel_type]
    
    noun_clusters = parse_noun_cluster_file(noun_cluster_file)
    verb_clusters = parse_verb_cluster_file(verb_cluster_file)
    potential_metaphors = populate_potential_metaphor_list(noun_clusters, verb_clusters, verb_seed, noun_seed)

    # Create an output file and write out discovered metaphors to file
    # pfile = open(potential_met_file, 'r', encoding='utf-8')
    # Just for spanish stuff
    pfile = codecs.open(potential_met_file, 'r', encoding='utf-8')

    if output_file_name != None:
        if not output_file_name.endswith('.txt'):
            print >> sys.stderr, ">>> Output File name must have .txt extension!"
            sys.exit(1)
#       output_file = codecs.open(output_file_name, 'w', encoding='utf-8')
        # Just for spanish stuff
        output_file = codecs.open(output_file_name, 'w', encoding='utf-8')
        output_file.write("Original Seed is: " + verb_seed + " - " + noun_seed + "\n\n")
        output_file.write("Here are the discovered metaphors:\n")
   
    line = pfile.readline()

    if verbose:
        if output_file_name != None:
            print "Searching for metaphors and saving to output file..."
        else:
            print "Searching for metaphors..."

    index = 0
    while line != '':

        # Check for blank lines
        if line == '\n':
            line = pfile.readline()
            continue
        line = line.strip()
        freq = ""  # russian doesn't have freq

        # Only for Spanish and English Clusters
        if lang != 'ru':
            line = line.split()
            if len(line) != 3:
                line = pfile.readline()
                continue 
            freq = line[0]
            verb = line[2]
            noun = line[1]
            line = line[2] + ' - ' + line[1]
        else:
            segs = line.split()
            verb = line[0]
            noun = line[2]

        # Search potential metaphor list
        if line in potential_metaphors:
            if output_file_name != None:
                output_file.write("\t" + line + "\n")
            if show_sentences:
                print '----------------------------------------------------'
            print "Discovered metaphor:",line,freq
            if show_sentences:
                try:
                    sents = unicode(
                        subprocess.check_output(['./findrel', gramrel,
                                                 verb, noun],
                                                cwd=resultscwd),'utf-8')
                    for s in sorted(set(sents.splitlines())):
                        print "-",s
                except subprocess.CalledProcessError:
                    print >> sys.stderr, 'Error looking up examples for',line
            index += 1

        line = pfile.readline()
        # End while loop
    pfile.close()
    if verbose:
        print "Found {0} metaphors!".format(index)

    # End main


def parse_noun_cluster_file(noun_cluster_file):
    # Populate the noun_cluster dictionary
    noun_clusters = {}
    nfile = codecs.open(noun_cluster_file, 'r', encoding='utf-8')
    line = nfile.readline()
    while line != '':
        line = line.strip().split()
        noun_clusters[line[0]] = line[1:]
        line = nfile.readline()
    nfile.close()
    return noun_clusters

def parse_verb_cluster_file(verb_cluster_file):
    # Populate the verb_cluster dictionary
    verb_clusters = {}
    vfile = codecs.open(verb_cluster_file, 'r', encoding='utf-8')
    line = vfile.readline()
    while line != '':
        line = line.strip().split()
        verb_clusters[line[0]] = line[1:]
        line = vfile.readline()
    vfile.close()
    return verb_clusters

def populate_potential_metaphor_list(noun_clusters, verb_clusters, verb_seed, noun_seed):

    potential_metaphors = []
    verb_cluster_name = None
    noun_cluster_name = None

        # Search verb and noun clusters
    for cluster in verb_clusters.keys():
        if verb_seed in verb_clusters[cluster]:
            verb_cluster_name = cluster
            break
    for cluster in noun_clusters.keys():
        if noun_seed in noun_clusters[cluster]:
            noun_cluster_name = cluster
            break

    if verb_cluster_name and noun_cluster_name:
        # If they exist, store all combinations in potential metaphors list
        for _verb in verb_clusters[verb_cluster_name]:
            for _noun in noun_clusters[noun_cluster_name]:
                potential_metaphors.append(_verb + ' - ' + _noun)
    else:
        print >> sys.stderr, ">>> Clusters for verb and/or noun don't exist!"
        sys.exit(0)

    return potential_metaphors


def cmdline_parser():
    global POT_MET_FILE
    """Creates a parser using the argparse module"""
    parser = argparse.ArgumentParser(description='Metaphor Search Using Metaphorical Seeds',
                                     epilog='--ChrisXie 2012.09.24')
    parser.add_argument('-l', '--language', required=True, choices=POT_MET_FILE.keys(),
                        dest='language',
                        help='Language to run search on')
    parser.add_argument('-r', '--rel-type', required=True, choices=POT_MET_FILE['en'].keys(),
                        help='Relation type', dest='reltype')
    parser.add_argument('-v', '--verb', required=True, dest='verb', help='Verb Seed')
    parser.add_argument('-n', '--noun', required=True, dest='noun', help='Noun Seed')
    parser.add_argument('-o', '--output', dest='output_file_name',
                        help='If this option is specified and an argument passed in, '\
                        'the output is written to a file created with this name in the '\
                        'current directory (or path, if specified). Please have the'\
                        ' .txt extension at the end of the file name')
    parser.add_argument('-vv','--verbose',action='store_true',
                        help="Print more information along the way",dest='verbose')
    parser.add_argument('-s','--show-sentences',dest='sentences',action='store_true',
                        help='Show the example sentences for each LM found. Note:'\
                        ' this currently only words for English and Spanish.')
    return parser


if __name__ == "__main__":
    status = main()
    sys.exit(status)
