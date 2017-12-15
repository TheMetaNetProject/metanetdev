.. java:import:: java.io BufferedWriter

.. java:import:: java.io File

.. java:import:: java.io FileNotFoundException

.. java:import:: java.io FileWriter

.. java:import:: java.io IOException

.. java:import:: java.sql SQLException

.. java:import:: java.sql Statement

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util LinkedList

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLClassExpression

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: com.mysql.jdbc.exceptions.jdbc4 MySQLIntegrityConstraintViolationException

FullTableBuilder
================

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public class FullTableBuilder implements TableBuilder

   This table builder builds using a static database schema

   :author: brandon

Constructors
------------
FullTableBuilder
^^^^^^^^^^^^^^^^

.. java:constructor::  FullTableBuilder(OWLOntology ont, Statement stmt, boolean verbose)
   :outertype: FullTableBuilder

   Initializes the TableBuilder object

Methods
-------
build
^^^^^

.. java:method:: public void build() throws SQLException
   :outertype: FullTableBuilder

   Creates the SQL schema and populates data on the OWL class, data property, and object property schemas and reports time taken

enableErrorLogging
^^^^^^^^^^^^^^^^^^

.. java:method:: public void enableErrorLogging(String logPath) throws IOException
   :outertype: FullTableBuilder

   Enables error logging to the given file during the table building process

   :param logFile: - a File object representing the file to wish we wish to write error logs

handleAnnotationSchema
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: protected void handleAnnotationSchema()
   :outertype: FullTableBuilder

handleClassSchema
^^^^^^^^^^^^^^^^^

.. java:method:: protected void handleClassSchema() throws SQLException
   :outertype: FullTableBuilder

   Populates the Class table with the names of each class in the ontology

handleDataPropSchema
^^^^^^^^^^^^^^^^^^^^

.. java:method:: protected void handleDataPropSchema() throws SQLException
   :outertype: FullTableBuilder

   Populates data for all data property types, domains, and relationships

handleInstances
^^^^^^^^^^^^^^^

.. java:method:: protected void handleInstances() throws SQLException
   :outertype: FullTableBuilder

   Populates data for all named individuals and their data and object properties

handleObjPropSchema
^^^^^^^^^^^^^^^^^^^

.. java:method:: protected void handleObjPropSchema() throws SQLException
   :outertype: FullTableBuilder

   Populates data for all object property types, domains, ranges, and relationships

initializeTables
^^^^^^^^^^^^^^^^

.. java:method:: protected void initializeTables() throws SQLException
   :outertype: FullTableBuilder

   Initializes the tables of the SQL schema

logError
^^^^^^^^

.. java:method:: protected void logError(String text)
   :outertype: FullTableBuilder

   Outputs the given text to the error log if error logging is enabled. Otherwise, does nothing.

   :param text:

print
^^^^^

.. java:method:: protected void print(String update)
   :outertype: FullTableBuilder

   Prints progress bar i.e. updateProgress()

   :param update:

println
^^^^^^^

.. java:method:: protected void println()
   :outertype: FullTableBuilder

   Prints empty string

println
^^^^^^^

.. java:method:: protected void println(String line)
   :outertype: FullTableBuilder

   Gives update

   :param update:

report
^^^^^^

.. java:method:: protected void report()
   :outertype: FullTableBuilder

   Reports number of errors encountered during the building

