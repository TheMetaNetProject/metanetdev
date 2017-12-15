.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Set

.. java:import:: org.semanticweb.owlapi.model AxiomType

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyAssertionAxiom

.. java:import:: org.semanticweb.owlapi.model OWLOntology

EntityLibrary
=============

.. java:package:: edu.berkeley.icsi.metanet.metavisual
   :noindex:

.. java:type:: public class EntityLibrary

Constructors
------------
EntityLibrary
^^^^^^^^^^^^^

.. java:constructor:: public EntityLibrary(OWLOntology owlModel)
   :outertype: EntityLibrary

Methods
-------
getClasses
^^^^^^^^^^

.. java:method:: public HashMap<String, OWLClass> getClasses()
   :outertype: EntityLibrary

getDataProperties
^^^^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, OWLDataProperty> getDataProperties()
   :outertype: EntityLibrary

getIndividuals
^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, OWLNamedIndividual> getIndividuals()
   :outertype: EntityLibrary

getObjectProperties
^^^^^^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, OWLObjectProperty> getObjectProperties()
   :outertype: EntityLibrary

getSubjectsSet
^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, Set<OWLNamedIndividual>> getSubjectsSet()
   :outertype: EntityLibrary

indieHashSet
^^^^^^^^^^^^

.. java:method:: public HashMap<String, OWLNamedIndividual> indieHashSet(OWLNamedIndividual individual, OWLObjectProperty property)
   :outertype: EntityLibrary

