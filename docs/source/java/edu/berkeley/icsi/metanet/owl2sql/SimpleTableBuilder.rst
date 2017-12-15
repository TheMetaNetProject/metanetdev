.. java:import:: java.io IOException

.. java:import:: java.sql SQLException

.. java:import:: java.sql Statement

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Map.Entry

.. java:import:: java.util Set

.. java:import:: org.semanticweb.owlapi.model OWLAnnotation

.. java:import:: org.semanticweb.owlapi.model OWLAnnotationProperty

.. java:import:: org.semanticweb.owlapi.model OWLAnnotationSubject

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

SimpleTableBuilder
==================

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public class SimpleTableBuilder implements TableBuilder

   Class that handles building a simplified translation of an OWL ontology to RDB tables. Rather than using tables to capture abstract entities and relationships in an OWL ontology, this class builds tables corresponding to actual classes in the OWL schema.

   :author: brandon

Constructors
------------
SimpleTableBuilder
^^^^^^^^^^^^^^^^^^

.. java:constructor::  SimpleTableBuilder(OWLOntology ont, Statement stmt, boolean verbose)
   :outertype: SimpleTableBuilder

   Basic constructor

   :param ont: - The OWL ontology
   :param stmt: - A Statement created from a Connection to the database server

Methods
-------
build
^^^^^

.. java:method:: @Override public void build() throws SQLException
   :outertype: SimpleTableBuilder

enableErrorLogging
^^^^^^^^^^^^^^^^^^

.. java:method:: @Override public void enableErrorLogging(String logPath) throws IOException
   :outertype: SimpleTableBuilder

initTables
^^^^^^^^^^

.. java:method:: protected void initTables() throws SQLException
   :outertype: SimpleTableBuilder

   Initializes the tables in the database

populateIndividuals
^^^^^^^^^^^^^^^^^^^

.. java:method:: protected void populateIndividuals() throws SQLException
   :outertype: SimpleTableBuilder

setPointers
^^^^^^^^^^^

.. java:method:: protected void setPointers()
   :outertype: SimpleTableBuilder

   Sets pointers to each of the appropriate OWL classes, object properties, and data properties

statusUpdate
^^^^^^^^^^^^

.. java:method:: protected void statusUpdate(String msg)
   :outertype: SimpleTableBuilder

   Handles status updates to STDOUT

   :param msg:

