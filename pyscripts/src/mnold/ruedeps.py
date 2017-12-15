#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Extract dependency relations for Russian.
#

from __future__ import print_function

import re
import os
import sys
import io
import json
import tempfile
import subprocess

from itertools import ifilter
from pprint import pprint, pformat
from collections import namedtuple

# Basic relations
VS_relation = u'предик'  # Verb-Subject
VO_relation = u'1-компл'  # Verb-Object
Relations_list = [VS_relation, VO_relation]

# Default encoding scheme
encoding_scheme = 'utf-8'

# Base path for Russian data
BASEDIR = '/u/metanet/corpolexica/RU'

# Location of the Russian MALT parser
PARSERDIR = os.path.join(BASEDIR, 'parsers/tools/parser')

# Location of various files needed for detecting valid metaphors
_noun_clus_file = os.path.join(BASEDIR, "RU-WAC/Russian Metaphor Extraction/clusterslist_RU_uncollapsed_noun3000.txt")
_verb_clus_file = os.path.join(BASEDIR, "RU-WAC/Russian Metaphor Extraction/clusterslist_RU_uncollapsed_verb3000.txt")
_vs_seeds_file = os.path.join(BASEDIR, 'RU-WAC/Russian Metaphor Extraction/RUseedsVerb-Subject.txt')
_vo_seeds_file = os.path.join(BASEDIR, 'RU-WAC/Russian Metaphor Extraction/RUseedsVerb-Object.txt')

# This is from edeps.py in ../depparsing:
deprec = namedtuple('deprec', ('rel', 'word', 'lemma', 'pos', 'wordn', 'head'))

class RuEdepsException(Exception):
    pass

def _gentmpfname():
    tf = tempfile.NamedTemporaryFile(delete=False)
    tfname = tf.name  # keep the temp file name
    tf.close()
    return tfname

def _parse_cluster_file(cluster_file, encoding_scheme):
    # Populate a cluster dictionary
    clusters = {}
    nfile = io.open(cluster_file, 'r', encoding=encoding_scheme)
    line = nfile.readline()
    while line != '':
        line = line.strip().split()
        clusters[line[0]] = line[1:]
        line = nfile.readline()
    nfile.close()
    return clusters

def _populate_potential_metaphor_list(noun_clusters, verb_clusters, seeds_list):

    # Dictionary that maps a potential metaphor to it's original seed
    potential_metaphors = {}

    # Read in verb and noun seeds from file
    # Specifically for Russian at this point
    seeds_file = io.open(seeds_list, encoding='utf-8')

    line = seeds_file.readline()
    while line != '':
        verb_seed, noun_seed = line.strip().split(', ')

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
                    potential_metaphors[_verb + ' - ' + _noun] = verb_seed + ' ' + noun_seed

        line = seeds_file.readline()
        # End while loop

    seeds_file.close()
    if len(potential_metaphors) == 0:
        # print(">>> No matches for verb and noun clusters for all seeds!", file=sys.stderr)
        sys.exit(0)

    return potential_metaphors

def dependencies(jsoninfile):
    """Extract the dependency relations from the given json input
    file, which is expected to contain Russian data.
    """

    # Extract the text from the given json file
    with io.open(jsoninfile, 'r', encoding=encoding_scheme) as f:
        input_file = json.load(f)

    # Get a temp file name
    tfname = _gentmpfname()

    # Write all of the sentences to the temp file
    with io.open(tfname, 'w', encoding=encoding_scheme) as temp:
        for entry in input_file['sentences']:
            temp.write(entry['text'])
            temp.write(u'\n')

    # Run the parser
    print("Parsing the input Russian text with malt...", end='')
    sys.stdout.flush()
    parsed_fname = _runparser(tfname)
    print("done")
    sys.stdout.flush()

    # Extract relations
    #   rel_dict will be a dict with one key for each item in the global Relations_list[]
    rel_dict = _extract_relations(parsed_fname)

#     pprint(rel_dict)

    # This is the list that will be returned. Each item in the list is a tuple
    # containing a sentence number and a deprec
    deplist = []

    # Find verb-object metaphors
    print("Searching for verb-object metaphors...", end='')
    sys.stdout.flush()
    arguments = {}
    arguments['list'] = rel_dict[VO_relation]
    arguments['rel_type'] = 'verb-object'
    vo_metaphors = _search_metaphors(arguments)
    for item in vo_metaphors:
        m4 = item['metaphor']
        seed = item['seed']  # not currently used...
        sentnum = int(m4[6])

        # Create dependency records & add to output list
        vdeprec = deprec(rel='#top#'    , lemma=m4[1], word=m4[2], pos='V', wordn=m4[0], head=())
        deplist.append((sentnum, vdeprec))
        odeprec = deprec(rel=VO_relation, lemma=m4[4], word=m4[5], pos='N', wordn=m4[3], head=vdeprec)
        deplist.append((sentnum, odeprec))

    print("done")

    # Find verb-subject metaphors
    print("Searching for verb-subject metaphors...", end='')
    sys.stdout.flush()
    arguments['list'] = rel_dict[VS_relation]
    arguments['rel_type'] = 'verb-subject'
    vs_metaphors = _search_metaphors(arguments)
    for item in vs_metaphors:
        m4 = item['metaphor']
        seed = item['seed']  # not currently used...
        sentnum = int(m4[6])

        # Create dependency records & add to output list
        vdeprec = deprec(rel='#top#'    , lemma=m4[1], word=m4[2], pos='V', wordn=m4[0], head=())
        deplist.append((sentnum, vdeprec))
        sdeprec = deprec(rel=VS_relation, lemma=m4[4], word=m4[5], pos='N', wordn=m4[3], head=vdeprec)
        deplist.append((sentnum, sdeprec))

    print("done")

    # clean up
    os.unlink(tfname)
    os.unlink(parsed_fname)

    return deplist

def _search_metaphors(args):
    '''Compare the potential metaphors with a list of known metaphors. Return a list of
    dicts representing the found metaphors. Each dict has two keys: 
       "metaphor" and "seed"
    '''
    rel_type = args['rel_type']
    if rel_type.lower() == "verb-object":
        potential_met_list = args['list']
        valid_metaphors = VO_metaphors
    elif rel_type.lower() == "verb-subject":
        potential_met_list = args['list']
        valid_metaphors = VS_metaphors
    else:
        raise(RuEdepsException("Invalid relation type."))

    discovered_metaphors = []
    for line in potential_met_list:
        try:
            lemma_head = line[1]
            lemma_word = line[4]
        except:
            raise(RuEdepsException("Invalid potential metaphor."))

        # Search valid-metaphor dictionary to find a matching seed
        idx = lemma_head + ' - ' + lemma_word
        if idx in valid_metaphors:
            discovered_metaphors.append({'metaphor': line,
                                         'seed': valid_metaphors[idx]})

    return discovered_metaphors


def _runparser(infilename):
    '''Run the MALT parser on a file of sentences, one sentence per line.'''
    original_dir = os.getcwd()
    if original_dir.endswith('/') == False:
        original_dir += '/'
    os.chdir(PARSERDIR)

    # Get a temp file name for the parsed output
    outfilename = _gentmpfname()

    # Parse the file leaving the parsed output in a temp file
    cmd = "./russian-malt.sh < {0} > {1}".format(infilename, outfilename)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if(process.returncode != 0):
        raise RuEdepsException(err)

    # Restore the original dir
    os.chdir(original_dir)

    return outfilename

def _extract_relations(parsed_file):
    '''Extract relations from the given parsed file.'''
    output_mapper = {VS_relation: [], VO_relation: []}

    # Unacceptable character list
    noGoodCharList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '.', ';', ':', '?', '<', '>', '/', '\\', '|', '`', '~', '[', ']', '{', '}',
            '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '=', '+']

    rfile = io.open(parsed_file, 'r', encoding=encoding_scheme)
    sentence_number = 0
    line = rfile.readline()
    while line != '':

        line = line.strip().split()
        if len(line) != 10:
            line = rfile.readline()
            continue

        sentence_words = []
        sentence_dict = {}  # a dictionary whose keys are the word indexes

        # Add all lines to sentence_words list
        while line[5] != 'SENT':
            sentence_words.append(line)
            line = rfile.readline()
            line = line.strip().split()
            while len(line) != 10:
                line = rfile.readline()
                line = line.strip().split()
                continue

        # Turn list into a dictionary of indexes to object
        for word in sentence_words:
            if len(word) != 10:
                sentence_words.remove(word)
                continue
            sentence_dict[word[0]] = word

        # Run through all words and check for relations (the words must be nouns)
        # every entry looks like this:
        #  [index, .., lemma, POS, POS, ..., sentence dependency index, relation]
        # Look at the index (word[4]) and figure out how to write it out to the file. This
        # will require some extra parsing in the metaphor detection file
        for word in sentence_words:
            relation = word[7]
            if relation in Relations_list and word[3] == 'N':

                try:
                    temp = sentence_dict[word[6]]
                except Exception as e:
                    continue

                if temp[3] == 'V':
                    lemmastring = temp[2] + " - " + word[2]  # Grabbing both lemmas
                    # Check against noGoodCharList
                    valid = True
                    for char in lemmastring:
                        if char in noGoodCharList:
                            valid = False
                    if valid:
                        # head_index, head_lemma, head_word, index, lemma, word, sentnum
                        reltup = (int(temp[0]) - 1, temp[2], temp[1],  # head word
                                  int(word[0]) - 1, word[2], word[1],  # word
                                  sentence_number)
                        output_mapper[relation].append(reltup)


        sentence_number += 1
        line = rfile.readline()
        # End while loop

    rfile.close()

    return output_mapper

#
# Set up the known-metaphors
#

# Load the noun and verb cluster files
_noun_clusters = _parse_cluster_file(_noun_clus_file, encoding_scheme)
_verb_clusters = _parse_cluster_file(_verb_clus_file, encoding_scheme)

# valid verb-subject metaphors
VS_metaphors = _populate_potential_metaphor_list(_noun_clusters, _verb_clusters, _vs_seeds_file)

# valid verb-object metaphors
VO_metaphors = _populate_potential_metaphor_list(_noun_clusters, _verb_clusters, _vo_seeds_file)

if __name__ == '__main__':
    testfile = sys.argv[1]

    deps = dependencies(testfile)
    for snum, reltup in sorted(deps):
        print(snum, end=': ')
        outstr = json.dumps(reltup, indent=2, sort_keys=True, ensure_ascii=False, encoding="utf-8")
        print(outstr)

