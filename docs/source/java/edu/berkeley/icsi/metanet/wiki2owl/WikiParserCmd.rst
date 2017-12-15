.. java:import:: java.io File

.. java:import:: java.io IOException

.. java:import:: java.net MalformedURLException

.. java:import:: java.net URISyntaxException

.. java:import:: java.net URL

.. java:import:: java.util Collections

.. java:import:: java.util.logging Level

.. java:import:: java.util.logging Logger

.. java:import:: org.apache.commons.cli CommandLine

.. java:import:: org.apache.commons.cli CommandLineParser

.. java:import:: org.apache.commons.cli HelpFormatter

.. java:import:: org.apache.commons.cli Option

.. java:import:: org.apache.commons.cli Options

.. java:import:: org.apache.commons.cli ParseException

.. java:import:: org.apache.commons.cli PosixParser

.. java:import:: org.semanticweb.owlapi.apibinding OWLManager

.. java:import:: org.semanticweb.owlapi.io RDFXMLOntologyFormat

.. java:import:: org.semanticweb.owlapi.model AddImport

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyCreationException

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.model OWLOntologyStorageException

.. java:import:: org.semanticweb.owlapi.util DefaultPrefixManager

.. java:import:: org.semanticweb.owlapi.util OWLEntityRemover

.. java:import:: java.io Console

.. java:import:: org.semanticweb.owlapi.util SimpleIRIMapper

WikiParserCmd
=============

.. java:package:: edu.berkeley.icsi.metanet.wiki2owl
   :noindex:

.. java:type:: public class WikiParserCmd

   Class to house main method for command line invocation of the WikiParser

   :author: jhong

Methods
-------
main
^^^^

.. java:method:: public static void main(String args)
   :outertype: WikiParserCmd

   :param args: the command line arguments

