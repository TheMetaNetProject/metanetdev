"""
Created on Aug 31, 2012

What this file does is operates on an excel file of parsed Russian sentences
from web blogs. It searches for relations (5 relations total), finds the index
of the corresponding relation, and checks if it is a verb-noun relation. If it
is, the verb-noun relation is grouped and written to the corresponding output
file. The lemmas are written to the file, not the words themselves.

Also, all the verbs and all the nouns are written to respective text files.

@author: ChrisXie
"""

import unicodedata as unic
import argparse

def extract_relations(parsed_file):
 
#    parser = create_parser()
#    name_space = parser.parse_args()
#    args = vars(name_space)
   
    relation1 = 'предик' # Verb-Subject
    relation2 = '1-компл' # Verb-Object

    relations_list = [relation1,relation2]

    
    # Unacceptable character list
    noGoodCharList = ['0','1','2','3','4','5','6','7','8','9',',','.',';',':','?','<','>','/','\\','|','`','~','[',']','{','}',
			'!','@','#','$','%','^','&','*','(',')','=','+']

    verbSubj_file = open('verbSubj.txt', 'w', encoding='utf-8')
    verbObj_file = open('verbObj.txt', 'w', encoding='utf-8')
    
#    rfile = open(args['file'], 'r', encoding='utf-8')
    rfile = open(parsed_file, 'r', encoding='utf-8')

    output_file_mapper = {relation1: verbSubj_file,
                         relation2: verbObj_file}

    sentence_number = 0
    line = rfile.readline()
    while line != '':
        
        sentence_words = []
        sentence_dict= {} # a dictionary whose keys are the word indexes
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
                    string = temp[2] + " - " + word[2] # Grabbing both lemmas
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
    # End main
        

#def create_parser():
#	parser = argparse.ArgumentParser()
#	parser.add_argument('-f', '--file', required=True, dest='file', help='Required argument. This file must be the parsed input file')
#	return parser



#if __name__ == '__main__':
#    main()
