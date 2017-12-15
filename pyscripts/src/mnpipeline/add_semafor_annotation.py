#!/usr/bin/env python

"""
This script appends the SEMAFOR annotation to each sentence in the input JSON
file and outputs it as a new file. Must be used on a machine that can run 
SEMAFOR

@author: bgthai@isci.berkeley.edu
Last edited: 5/7/2013

"""

from optparse import OptionParser
from xml.dom.minidom import parse
import json
import os
import subprocess
import sys
import codecs

# Try importing OrderedDict. Only works for Python 2.7
try:
    from collections import OrderedDict
    dict = OrderedDict
except:
    pass

BASEDIR = os.path.dirname(os.path.realpath(__file__))
TEMPDIR = os.path.join(BASEDIR, 'temp/')
SFDRIVER = '/u/framenet/aicorpus/semafor/semafor-semantic-parser/release/fnParserDriver.sh'

def print_err(msg):
    """
    Prints a message to STDERR and exits
    
    @param msg: the message
    
    """
    sys.stderr.write(msg + '\n')
    sys.exit(1)
    
def sentence_element_to_dict(sentence_element):
    """
    Converts a SEMAFOR sentence annotation to a Python dictionary
    
    @param sentence_element: the XML sentence element to be converted
    @type sentence_element: Element
    
    @return: an OrderedDict representation of the sentence element
    
    """
    
    sentence_dict = dict()
    # Get sentence text
    text_elements = sentence_element.getElementsByTagName('text')
    text = text_elements[0].firstChild.nodeValue
    sentence_dict['text'] = text
    
    # Iterate through annotation sets
    ann_set_dicts = list()
    sentence_dict['annotation_sets'] = ann_set_dicts
    for ann_set_element in sentence_element.getElementsByTagName('annotationSet'):
        ann_set_dict = dict()
        ann_set_dicts.append(ann_set_dict)
        ann_set_dict['id'] = int(ann_set_element.getAttribute('ID'))
        ann_set_dict['framename'] = ann_set_element.getAttribute('frameName')
        
        # Iterate through layers
        layer_dicts = list()
        ann_set_dict['layers'] = layer_dicts
        for layer_element in ann_set_element.getElementsByTagName('layer'):
            layer_dict = dict()
            layer_dicts.append(layer_dict)
            layer_dict['id'] = int(layer_element.getAttribute('ID'))
            layer_dict['name'] = layer_element.getAttribute('name')
            
            # Iterate through labels
            label_dicts = list()
            layer_dict['labels'] = label_dicts
            for label_element in layer_element.getElementsByTagName('label'):
                label_dict = dict()
                label_dicts.append(label_dict)
                label_dict['id'] = int(label_element.getAttribute('ID'))
                label_dict['name'] = label_element.getAttribute('name')
                start = int(label_element.getAttribute('start'))
                end = int(label_element.getAttribute('end'))
                label_dict['start'] = start
                label_dict['end'] = end
                label_dict['fragment'] = text[start : end + 1]
    return sentence_dict

def main():
    # Ensure temp/ directory exists
    if not os.path.exists(TEMPDIR):
        os.makedirs(TEMPDIR)
    
    # Handle command-line arguments
    usage = "usage: %prog <input-file> <output-file>"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error('Exactly two positional arguments required')
    input_file_path = os.path.abspath(args[0])
    output_file_path = os.path.abspath(args[1])
    
    if not os.path.isfile(input_file_path):
        print_err('Error: Invalid file path ' + input_file_path)
    
    # Parse JSON input file into Python object
    try:
        with codecs.open(input_file_path, encoding='utf-8') as input_file:
            try:
                input_dict = json.load(input_file)
                input_sentence_dicts = input_dict['sentences']
            except:
                print_err('Error: Unable to parse ' + input_file_path + ' as JSON file')
    except IOError:
        print_err('Unable to open file ' + input_file_path)

    # Write sentences out to temp file for SEMAFOR
    sentences_file_path = os.path.join(TEMPDIR, 'sentences.txt')
    with codecs.open(sentences_file_path, 'w', encoding='utf-8') as sentences_file:
        for sentence_dict in input_sentence_dicts:
            sentences_file.write(sentence_dict['text'] + '\n')
    
    # Call SEMAFOR
    xml_file_path = os.path.join(TEMPDIR, 'semafor-out.xml')
    if not os.path.isfile(SFDRIVER):
        print_err('Error: SEMAFOR run file ' + SFDRIVER + ' could not be found')
    return_code = subprocess.call(['srun', '-qk', '-I', '-p', 'ai', 
                                   '--mem-per-cpu', '20000', SFDRIVER, 
                                   sentences_file_path, xml_file_path])
    if return_code != 0:
        print_err('Error: SEMAFOR exited with nonzero status code ' + str(return_code))
    
    
    # Parse XML file into Document object
    try:
        with open(xml_file_path) as xml_file:
            try:
                xml_doc = parse(xml_file)
            except:
                print_err('Unable to parse ' + xml_file_path + ' as XML file')
    except IOError:
        print_err('Unable to open file ' + xml_file_path)
    doc_element = xml_doc.documentElement
    doc_element.normalize()
    
    # Iterate through input_sentence_dicts
    sentence_elements = doc_element.getElementsByTagName('sentence')
    zipped = zip(sentence_elements, input_sentence_dicts)
    for sentence_element, sentence_dict in zipped:
        sentence_dict['semafor_annotation'] = sentence_element_to_dict(sentence_element)
        
    json_output = json.dumps(input_dict, indent=4, separators=(',', ': '))
    
    # Write out to file
    try:
        with open(output_file_path, 'w') as output_file:
            try:
                output_file.write(json_output)
            except:
                print_err('Unable to write to ' + output_file_path)
    except IOError:
        print_err('Unable to open file ' + output_file_path)


if __name__ == '__main__':
    main()
