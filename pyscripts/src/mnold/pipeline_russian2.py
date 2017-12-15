#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# The above encoding declaration is required and the file must be saved as UTF-8
""" This file is the entire pipeline for extracting and searching for Russian
    Russian Metaphors. You can either pass a JSON file or a text file. If passing
    a JSON file, a edited JSON file will be written. Else, a text file will be 
    written with all discovered metaphors.
"""


import argparse, sys, os
import json
import unicodedata as unic
import io

def extract_relations(parsed_file):

    #    parser = create_parser()
#    name_space = parser.parse_args()
#    args = vars(name_space)

    relation1 = u'предик'  # Verb-Subject
    relation2 = u'1-компл'  # Verb-Object

    relations_list = [relation1, relation2]


    # Unacceptable character list
    noGoodCharList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '.', ';', ':', '?', '<', '>', '/', '\\', '|', '`', '~', '[', ']', '{', '}',
            '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '=', '+']

    verbSubj_file = io.open('verbSubj.txt', 'w', encoding='utf-8')
    verbObj_file = io.open('verbObj.txt', 'w', encoding='utf-8')

#    rfile = open(args['file'], 'r', encoding='utf-8')
    rfile = io.open(parsed_file, 'r', encoding='utf-8')

    output_file_mapper = {relation1: verbSubj_file, relation2: verbObj_file}

    sentence_number = 0
    line = rfile.readline()
    while line != '':

        sentence_words = []
        sentence_dict = {}  # a dictionary whose keys are the word indexes
        line = line.strip().split()

        if len(line) != 10:
            line = rfile.readline()
            continue

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
        # every entry looks like this: [index, .., lemma, POS, POS, ..., sentence dependency index, relation]
        # Look at the index (word[4]) and figure out how to write it out to the file. This
        # will require some extra parsing in the metaphor detection file
        for word in sentence_words:
            relation = word[7]
            if relation in relations_list and word[3] == 'N':

                try:
                    temp = sentence_dict[word[6]]
                except Exception as e:
                    continue

                if temp[3] == 'V':
                    string = temp[2] + " - " + word[2]  # Grabbing both lemmas
            # Check against noGoodCharList
                    valid = True
                    for char in string:
                        if char in noGoodCharList:
                            valid = False
                    if valid:
                        # Find index, print index with words
                        string = temp[2] + ' - ' + temp[1] + ' - ' + word[2] + ' - ' + word[1] + ' - ' + str(sentence_number)
                        output_file_mapper[relation].write("\t" + string + "\n")


        sentence_number += 1
        line = rfile.readline()
        # End while loop

    rfile.close()


def search_metaphors(args):

    # 	parser = create_parser()
    # 	name_space = parser.parse_args()
    # 	args = vars(name_space)

    language = args['language']
    rel_type = args['rel_type']
    seeds_list = args['seeds_list']
    output_file_name = args['output_file_name']

    # Set the encoding scheme, cluster files, and potential metaphor files depending on the language
    if language.lower() == 'russian':
        encoding_scheme = 'utf-8'
        noun_cluster_file = "/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/clusterslist_RU_uncollapsed_noun3000.txt"
        verb_cluster_file = "/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/clusterslist_RU_uncollapsed_verb3000.txt"
        if rel_type.lower() == "verb-object":
            potential_met_file = args['file']
        elif rel_type.lower() == "verb-subject":
            potential_met_file = args['file']
        else:
            # print(">>> Relation_type not recognized! Please input a relation type of: verb-object, verb-subject", file=sys.stderr)
            sys.exit(0)

    elif language.lower() == 'spanish':
        encoding_scheme = 'latin-1'
        noun_cluster_file = "/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/Spanish Clusters/Noun_Clusters_uncollapsed.txt"
        verb_cluster_file = "/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/Spanish Clusters/Verb_Clusters_uncollapsed.txt"
        if rel_type.lower() == "verb-object":
            potential_met_file = "/u/metanet/Parsing/Results/GW/es/dobj"
        elif rel_type.lower() == "verb-subject":
            potential_met_file = "/u/metanet/Parsing/Results/GW/es/subj"
        else:
            # print(">>> Relation_type not recognized! Please input a relation type of: verb-object, verb-subject", file=sys.stderr)
            sys.exit(0)

    elif language.lower() == 'english':
        encoding_scheme = 'utf-8'
        noun_cluster_file = "/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/English Clusters/Noun_Clusters.txt"
        verb_cluster_file = "/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/English Clusters/Verb_Clusters.txt"
        if rel_type.lower() == "verb-object":
            potential_met_file = "/u/metanet/corpolexica/EN/bnc-relations/DirectObjRels.txt-uniqed-sorted"
        elif rel_type.lower() == "verb-subject":
            potential_met_file = "/u/metanet/corpolexica/EN/bnc-relations/SubjectRels.txt-uniqed-sorted"
        else:
            # print(">>> Relation_type not recognized! Please input a relation type of: verb-object, verb-subject", file=sys.stderr)
            sys.exit(0)

    else:
        # print(">>> Language not recognized! Please input a language of choice: English, Russian, Spanish", file=sys.stderr)
        sys.exit(0)

    noun_clusters = parse_noun_cluster_file(noun_cluster_file, encoding_scheme)
    verb_clusters = parse_verb_cluster_file(verb_cluster_file, encoding_scheme)
    potential_metaphors = populate_potential_metaphor_list(noun_clusters, verb_clusters, seeds_list)

    # Create an output file and write out discovered metaphors to file
    pfile = io.open(potential_met_file, 'r', encoding=encoding_scheme)

    if output_file_name != None:
        if not output_file_name.endswith('.txt'):
            # print(">>> Output File name must have .txt extension!", file=sys.stderr)
            sys.exit(1)
        output_file = io.open(output_file_name, 'w', encoding=encoding_scheme)
        output_file.write("Original Seed is: " + verb_seed + " - " + noun_seed + "\n\n")  # @UndefinedVariable
        output_file.write("Here are the discovered metaphors:\n")

    line = pfile.readline()

    if output_file_name != None:
        print("Searching for metaphors and saving to output file...")
    else:
        print("Searching for metaphors...")

    index = 0
    discovered_metaphors = []
    while line != '':

        # Check for blank lines
        if line == '\n':
            line = pfile.readline()
            continue

        original_line = line.strip().split(' - ')
        line = original_line[0] + ' - ' + original_line[2]

        # Only for Spanish and English Clusters
        if language.lower() != 'russian':
            line = line.split()
            if len(line) != 3:
                line = pfile.readline()
                continue
            line = line[2] + ' - ' + line[1]

            # Search potential metaphor dictionary
        if line in potential_metaphors:
            if output_file_name != None:
                output_file.write("\t" + line + "\n")
            # print("Discovered metaphor: {0}; Original seed: {1}".format(line, potential_metaphors[line]))
            discovered_metaphors.append({'metaphor': original_line, 'seed': potential_metaphors[line]})
            index += 1

        line = pfile.readline()
        # End while loop
    pfile.close()
    print("Found {0} metaphors!".format(index))

    return discovered_metaphors

# End search_metaphors()


def parse_noun_cluster_file(noun_cluster_file, encoding_scheme):
    # Populate the noun_cluster dictionary
    noun_clusters = {}
    nfile = io.open(noun_cluster_file, 'r', encoding=encoding_scheme)
    line = nfile.readline()
    while line != '':
        line = line.strip().split()
        noun_clusters[line[0]] = line[1:]
        line = nfile.readline()
    nfile.close()
    return noun_clusters

def parse_verb_cluster_file(verb_cluster_file, encoding_scheme):
    # Populate the verb_cluster dictionary
    verb_clusters = {}
    vfile = io.open(verb_cluster_file, 'r', encoding=encoding_scheme)
    line = vfile.readline()
    while line != '':
        line = line.strip().split()
        verb_clusters[line[0]] = line[1:]
        line = vfile.readline()
    vfile.close()
    return verb_clusters

def populate_potential_metaphor_list(noun_clusters, verb_clusters, seeds_list):

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


def main():

    parser = create_parser()
    name_space = parser.parse_args()
    args = vars(name_space)

    original_dir = os.getcwd()
    if original_dir.endswith('/') == False:
        original_dir += '/'
    os.chdir('/u/metanet/corpolexica/RU/parsers/tools/parser')

    if args['type'].lower() == 'json':

        f = io.open(original_dir + args['file'], 'r', encoding='utf-8')
        input_file = json.load(f)

        # Write all sentences to file
        temp = io.open('temp.txt', 'w', encoding='utf-8')
        for entry in input_file['sentences']:
            temp.write(entry['text'])
            temp.write(u'\n')

            # Create 'lms' key
            entry['lms'] = []
        temp.close()

        # Parse the file
        print("Parsing the text...")
        os.system('./russian-malt.sh < temp.txt > temp_output.txt')

        # Extract the relations
        print("Extracting relations...")
        extract_relations('temp_output.txt')

        # Find verb-object metaphors and add to the JSON file
        print("Searching for verb-object metaphors...")
        arguments = {'file': 'verbObj.txt', 'language': 'russian', 'rel_type': 'verb-object', 'seeds_list': '/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/RUseedsVerb-Object.txt', 'output_file_name': None}
        discovered_metaphors = search_metaphors(arguments)

        for item in discovered_metaphors:
            m4 = item['metaphor']
            seed = item['seed']
            entry = input_file['sentences'][int(m4[4])]

            met_dict = {}
            met_dict['name'] = m4[0] + ' ' + m4[2]
            met_dict['seed'] = seed

            # Noun is the target
            target = {}
            target['lemma'] = m4[2]
            target['rel'] = 'obj'
            start, end = find_index(m4[3], entry['text'])
            target['start'] = start
            target['end'] = end

            # Verb is the source
            source = {}
            source['lemma'] = m4[0]
            source['rel'] = 'verb'
            start, end = find_index(m4[1], entry['text'])
            source['start'] = start
            source['end'] = end

            met_dict['target'] = target
            met_dict['source'] = source

            entry['lms'].append(met_dict)


        # Find verb-subject metaphors and add to the JSON file
        print("Searching for verb-subject metaphors...")
        arguments['file'] = 'verbSubj.txt'
        arguments['rel_type'] = 'verb-subject'
        arguments['seeds_list'] = '/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction/RUseedsVerb-Subject.txt'
        discovered_metaphors = search_metaphors(arguments)

        for item in discovered_metaphors:
            m4 = item['metaphor']
            seed = item['seed']
            entry = input_file['sentences'][int(m4[4])]

            met_dict = {}
            met_dict['name'] = m4[0] + ' ' + m4[2]
            met_dict['seed'] = seed

            # Noun is the target
            target = {}
            target['lemma'] = m4[2]
            target['rel'] = 'subj'
            start, end = find_index(m4[3], entry['text'])
            target['start'] = start
            target['end'] = end

            # Verb is the source
            source = {}
            source['lemma'] = m4[0]
            source['rel'] = 'verb'
            start, end = find_index(m4[1], entry['text'])
            source['start'] = start
            source['end'] = end

            met_dict['target'] = target
            met_dict['source'] = source

            entry['lms'].append(met_dict)

        print("Removing temporary files...")
        os.remove('temp.txt')
        os.remove('temp_output.txt')
        os.remove('verbObj.txt')
        os.remove('verbSubj.txt')

        print("Writing to output...")
        os.chdir(original_dir)
        output = io.open(args['output'], 'w', encoding='utf-8')
        output.write(unicode(json.dumps(input_file, sort_keys=True, indent=2, ensure_ascii=False, encoding="utf-8")))
        output.close()
        f.close()

    # End main()


def find_index(word, text):

    start = text.find(word)
    return start, start + len(word)


def create_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, dest='file', help='Either text file or JSON file to perform metaphor search upon')
    parser.add_argument('-t', '--type', required=True, dest='type', choices=['json', 'text'], help='Two options: "json" or "text". Must be one of these')
    parser.add_argument('-o', '--output', required=True, dest='output', help='Name of output file')

    return parser



if __name__ == '__main__':
    main()

