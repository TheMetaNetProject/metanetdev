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

SimpleTableBuilder.BlobIDsTuple
===============================

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type::  class BlobIDsTuple
   :outertype: SimpleTableBuilder

Fields
------
ids
^^^

.. java:field::  Set<Integer> ids
   :outertype: SimpleTableBuilder.BlobIDsTuple

Methods
-------
addToBlob
^^^^^^^^^

.. java:method:: protected void addToBlob(String str)
   :outertype: SimpleTableBuilder.BlobIDsTuple

getBlob
^^^^^^^

.. java:method:: protected String getBlob()
   :outertype: SimpleTableBuilder.BlobIDsTuple

