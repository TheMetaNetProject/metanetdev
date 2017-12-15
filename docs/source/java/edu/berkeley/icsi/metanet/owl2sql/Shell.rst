.. java:import:: java.io File

.. java:import:: java.io IOException

.. java:import:: java.sql Connection

.. java:import:: java.sql SQLException

.. java:import:: java.sql Statement

.. java:import:: java.util List

.. java:import:: org.apache.commons.cli CommandLine

.. java:import:: org.apache.commons.cli CommandLineParser

.. java:import:: org.apache.commons.cli HelpFormatter

.. java:import:: org.apache.commons.cli Options

.. java:import:: org.apache.commons.cli ParseException

.. java:import:: org.apache.commons.cli PosixParser

.. java:import:: org.semanticweb.owlapi.apibinding OWLManager

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

Shell
=====

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public abstract class Shell

Fields
------
port
^^^^

.. java:field::  int port
   :outertype: Shell

server
^^^^^^

.. java:field::  String server
   :outertype: Shell

tb
^^

.. java:field::  TableBuilder tb
   :outertype: Shell

verbose
^^^^^^^

.. java:field::  boolean verbose
   :outertype: Shell

Methods
-------
establishConnection
^^^^^^^^^^^^^^^^^^^

.. java:method:: abstract Connection establishConnection()
   :outertype: Shell

getDBName
^^^^^^^^^

.. java:method:: abstract String getDBName()
   :outertype: Shell

initTableBuilder
^^^^^^^^^^^^^^^^

.. java:method:: abstract TableBuilder initTableBuilder(OWLOntology ont, Statement stmt)
   :outertype: Shell

   Initializes a table builder

main
^^^^

.. java:method:: @SuppressWarnings public static void main(String args)
   :outertype: Shell

printHelp
^^^^^^^^^

.. java:method:: static void printHelp(Options options)
   :outertype: Shell

