.. java:import:: java.util Collections

.. java:import:: java.util Map

.. java:import:: java.util Map.Entry

.. java:import:: java.util Set

.. java:import:: java.util TreeMap

.. java:import:: java.util TreeSet

.. java:import:: org.protege.owl.codegeneration WrappedIndividual

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLClassExpression

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.util OWLEntityRemover

.. java:import:: org.semanticweb.owlapi.util ShortFormProvider

.. java:import:: org.semanticweb.owlapi.util SimpleShortFormProvider

WrappedIndividualImpl
=====================

.. java:package:: org.protege.owl.codegeneration.impl
   :noindex:

.. java:type:: public class WrappedIndividualImpl implements WrappedIndividual

   :author: z.khan

Constructors
------------
WrappedIndividualImpl
^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public WrappedIndividualImpl(OWLOntology owlOntology, IRI iri, CodeGenerationInference inf)
   :outertype: WrappedIndividualImpl

   Constructor

   :param owlDataFactory:
   :param iri:
   :param owlOntology:

WrappedIndividualImpl
^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public WrappedIndividualImpl(OWLOntology owlOntology, OWLNamedIndividual owlIndividual, CodeGenerationInference inf)
   :outertype: WrappedIndividualImpl

Methods
-------
assertOwlType
^^^^^^^^^^^^^

.. java:method:: public void assertOwlType(OWLClassExpression type)
   :outertype: WrappedIndividualImpl

   Asserts that the individual has a particular OWL type.

compareTo
^^^^^^^^^

.. java:method:: @Override public int compareTo(WrappedIndividual o)
   :outertype: WrappedIndividualImpl

delete
^^^^^^

.. java:method:: public void delete()
   :outertype: WrappedIndividualImpl

   Deletes the individual from Ontology

equals
^^^^^^

.. java:method:: @Override public boolean equals(Object obj)
   :outertype: WrappedIndividualImpl

getDelegate
^^^^^^^^^^^

.. java:method:: protected CodeGenerationHelper getDelegate()
   :outertype: WrappedIndividualImpl

getOwlIndividual
^^^^^^^^^^^^^^^^

.. java:method:: public OWLNamedIndividual getOwlIndividual()
   :outertype: WrappedIndividualImpl

getOwlOntology
^^^^^^^^^^^^^^

.. java:method:: public OWLOntology getOwlOntology()
   :outertype: WrappedIndividualImpl

   :return: the owlOntology

hashCode
^^^^^^^^

.. java:method:: @Override public int hashCode()
   :outertype: WrappedIndividualImpl

toString
^^^^^^^^

.. java:method:: @Override public String toString()
   :outertype: WrappedIndividualImpl

