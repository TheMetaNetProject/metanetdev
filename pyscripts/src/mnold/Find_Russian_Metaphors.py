"""
Created on October 24, 2012

This file takes a relation type, a verb-noun list of seeds, and an output file
name and generates metaphorical expressions based on a clustering algorithm. See
the usage() function for more details.

All of the cluster files and potential metaphor files have already been generated
from a parsed Russian web blog corpus.

@author: ChrisXie
"""

import sys, os, argparse

def search_metaphors(args):

#	parser = create_parser()
#	name_space = parser.parse_args()
#	args = vars(name_space)

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
			print(">>> Relation_type not recognized! Please input a relation type of: verb-object, verb-subject", file=sys.stderr)
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
			print(">>> Relation_type not recognized! Please input a relation type of: verb-object, verb-subject", file=sys.stderr)
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
			print(">>> Relation_type not recognized! Please input a relation type of: verb-object, verb-subject", file=sys.stderr)
			sys.exit(0)

	else:
		print(">>> Language not recognized! Please input a language of choice: English, Russian, Spanish", file=sys.stderr)
		sys.exit(0)

	noun_clusters = parse_noun_cluster_file(noun_cluster_file, encoding_scheme)
	verb_clusters = parse_verb_cluster_file(verb_cluster_file, encoding_scheme)
	potential_metaphors = populate_potential_metaphor_list(noun_clusters, verb_clusters, seeds_list)

	# Create an output file and write out discovered metaphors to file
	pfile = open(potential_met_file, 'r', encoding=encoding_scheme)

	if output_file_name != None:
		if not output_file_name.endswith('.txt'):
			print(">>> Output File name must have .txt extension!", file=sys.stderr)
			sys.exit(1)
		output_file = open(output_file_name, 'w', encoding=encoding_scheme)
		output_file.write("Original Seed is: " + verb_seed + " - " + noun_seed + "\n\n")
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
			#print("Discovered metaphor: {0}; Original seed: {1}".format(line, potential_metaphors[line]))
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
	nfile = open(noun_cluster_file, 'r', encoding=encoding_scheme)
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
	vfile = open(verb_cluster_file, 'r', encoding=encoding_scheme)
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
	seeds_file = open(seeds_list, encoding='utf-8')

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
		print(">>> No matches for verb and noun clusters for all seeds!", file=sys.stderr)
		sys.exit(0)

	return potential_metaphors


#def create_parser():
#	"""Creates a parser using the argparse module"""
#	parser = argparse.ArgumentParser(description='Metaphor Search Using Metaphorical Seeds',epilog='--ChrisXie 2012.09.24')
#	parser.add_argument('-l', '--language', required=True, choices=['english', 'spanish', 'russian'], dest='language', help='Required argument. Language must be one of the three choices and MUST BE LOWER CASE')
#	parser.add_argument('-r', required=True, choices=['verb-subject','verb-object'], help='Required argument. Relation Type must be one of the two choices and MUST BE LOWER CASE', dest='rel_type')
#	parser.add_argument('-f', '--file', required=True, dest='file', help='Required argument. File in which this script will search for metaphors')
#	parser.add_argument('-s', '--seeds', required=True, dest='seeds_list', help='Required argument. Seeds List')
#	parser.add_argument('-o', '--output', dest='output_file_name', help='Optional argument. If this option is specified and an argument passed in, the output is written to a file created with this name in the current directory (or path, if specified). Please have the .txt extension at the end of the file name')

#	return parser


#if __name__ == "__main__":
#	search_metaphors() 
