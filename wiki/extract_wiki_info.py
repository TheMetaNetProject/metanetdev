#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This is jebolton's script that parses RDF/OWL XML format version of
the conceptual network (which is converted from the MetaNet Wiki)
and generates a text format representation (to STDOUT) which can
be imported into Neo4j.

jebolton@icsi
jhong@icsi

"""

import re, argparse, codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

import xml.etree.ElementTree as ET

def main ():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Script for converting RDF/OWN XML format dump of MetaNet wiki "\
                "to a text format that is imported into neo4j.")
    parser.add_argument('inputfile', help='Input file to parse')
    cmdline = parser.parse_args()
        
    # load owl into tree
    
    tree = ET.parse(cmdline.inputfile)
    
    root = tree.getroot()
    
    # helper regexes
    
    metaphor_reggie = re.compile("#Metaphor")
    frame_reggie = re.compile("#Frame")
    lu_reggie = re.compile("LexicalUnit_[0-9]+")
    
    # list of nodes and edges
    
    metaphor_nodes = []
    frame_nodes = []
    lu_nodes = []
    
    edges = []
    
    for child in root:
    
        if metaphor_reggie.search(child.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"]):
            #print "---"
            c_key = child.attrib.keys()[0]
            new_metaphor_node = {}
            new_metaphor_node['name'] = child.attrib[c_key].split("#")[-1]
            #print "name of metaphor: "+child.attrib[c_key]
            for n in child:
                n_tag = n.tag
                n_key = n.attrib.keys()[0]
                n_val = n.attrib[n_key]
                #print (n_tag.split("}")[-1],n_key.split("}")[-1],n_val.split("}")[-1],n.text)
                if n_tag.split("}")[-1] == 'label':
                    new_metaphor_node['label'] = n.text
                if n_tag.split("}")[-1] == 'hasSourceFrame':
                    new_metaphor_node['source'] = n_val.split("}")[-1].split("#")[-1]
                if n_tag.split("}")[-1] == 'hasTargetFrame':
                    new_metaphor_node['target'] = n_val.split("}")[-1].split("#")[-1]
                if n_tag.split("}")[-1] == 'makesUseOfMetaphor':
                    other_metaphor = n_val.split("}")[-1].split("#")[-1]
                    this_metaphor = new_metaphor_node['name']
                    edge_label = 'makesUseOfMetaphor'
                    new_edge = ('metaphor_node','metaphor_node',other_metaphor,this_metaphor,edge_label)
                    edges.append(new_edge)
                if n_tag.split("}")[-1] == 'isEntailedByMetaphor':
                    other_metaphor = n_val.split("}")[-1].split("#")[-1]
                    this_metaphor = new_metaphor_node['name']
                    edge_label = 'isEntailedByMetaphor'
                    new_edge = ('metaphor_node','metaphor_node',other_metaphor,this_metaphor,edge_label)
                    edges.append(new_edge)
            metaphor_nodes.append(new_metaphor_node)
            if "source" in new_metaphor_node and "target" in new_metaphor_node:
                new_source_edge = ("frame_node","metaphor_node",new_metaphor_node["source"],
                    new_metaphor_node["name"],"hasSourceFrame")
                new_target_edge = ("frame_node","metaphor_node",new_metaphor_node["target"],
                    new_metaphor_node["name"],"hasTargetFrame")
                edges.append(new_source_edge)
                edges.append(new_target_edge)
    
        if frame_reggie.search(child.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"]):
            #print "---"
            c_key = child.attrib.keys()[0]
            new_frame_node = {}
            #print "name of frame: "+child.attrib[c_key]
            new_frame_node['name'] = child.attrib[c_key].split("#")[-1]
            for n in child:
                n_tag = n.tag
                n_key = n.attrib.keys()[0]
                n_val = n.attrib[n_key]
                #print (n_tag.split("}")[-1],n_key.split("}")[-1],n_val.split("}")[-1],n.text)
                if n_tag.split("}")[-1] == 'label':
                    new_frame_node['label'] = n.text
                if n_tag.split("}")[-1] == 'hasLexicalUnit':
                    lu_name = n_val.split("}")[-1].split("#")[-1]
                    frame_name = child.attrib[c_key].split("#")[-1]
                    edge_type = 'hasLexicalUnit'
                    edges.append(("lu_node", "frame_node", lu_name, frame_name,edge_type))
                    #print ("lu_node", "frame_node", lu_name, frame_name)
                if n_tag.split("}")[-1] == 'isSubcaseOfFrame':
                    #print (n_tag.split("}")[-1],n_key.split("}")[-1],n_val.split("}")[-1],n.text)
                    #print (n_tag.split("}")[-1],n_val.split("}")[-1].split("#")[-1])
                    edge_type = "isSubcaseOfFrame"
                    super_frame = n_val.split("}")[-1].split("#")[-1]
                    sub_frame = child.attrib[c_key].split("#")[-1]
                    new_edge = ("frame_node","frame_node",super_frame,sub_frame,edge_type)
                    edges.append(new_edge)
                if n_tag.split("}")[-1] == 'makesUseOfFrame':
                    edge_type = 'makesUseOfFrame'
                    other_frame = n_val.split("}")[-1].split("#")[-1]
                    this_frame = child.attrib[c_key].split("#")[-1]
                    new_edge = ("frame_node","frame_node",other_frame,this_frame,edge_type)
                    edges.append(new_edge)
    
            frame_nodes.append(new_frame_node)
        
        if lu_reggie.search(child.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"]):
            c_key = child.attrib.keys()[0]
            new_lu_node = {}
            #print "---"
            new_lu_node['name'] = child.attrib[c_key].split("#")[-1]
            #print "name of LU: "+child.attrib[c_key]
            for n in child:
                n_tag = n.tag
                n_key = n.attrib.keys()[0]
                n_val = n.attrib[n_key]
                #print (n_tag.split("}")[-1],n_key.split("}")[-1],n_val.split("}")[-1],n.text)
                if n_tag.split("}")[-1] == 'label':
                    new_lu_node['label'] = n.text
            lu_nodes.append(new_lu_node)
    
    #for metaphor_node in metaphor_nodes:
        #print metaphor_node
    
    for lu_node in lu_nodes:
        print "lu_node#"+lu_node['name']+"#"+lu_node['label']
    
    for frame_node in frame_nodes:
        print "frame_node#"+frame_node['name']+"#"+frame_node['label']
    
    for metaphor_node in metaphor_nodes:
        print "metaphor_node#"+metaphor_node["name"]+"#"+metaphor_node['label']
    
    for edge in edges:
        print "edge#"+edge[0]+"#"+edge[1]+"#"+edge[2]+"#"+edge[3]+"#"+edge[4]
    
    #for metaphor_node in metaphor_nodes:
        #print metaphor_node


if __name__ == "__main__":
    status = main()
    sys.exit(status)
    