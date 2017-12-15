.. java:import:: java.lang.reflect Constructor

.. java:import:: java.util Collection

.. java:import:: java.util HashSet

.. java:import:: java.util Set

.. java:import:: org.protege.owl.codegeneration CodeGenerationRuntimeException

.. java:import:: org.protege.owl.codegeneration HandledDatatypes

.. java:import:: org.protege.owl.codegeneration WrappedIndividual

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLAxiom

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

CodeGenerationHelper
====================

.. java:package:: org.protege.owl.codegeneration.impl
   :noindex:

.. java:type:: public class CodeGenerationHelper

Constructors
------------
CodeGenerationHelper
^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public CodeGenerationHelper(OWLOntology owlOntology, OWLNamedIndividual individual, CodeGenerationInference inf)
   :outertype: CodeGenerationHelper

Methods
-------
addPropertyValue
^^^^^^^^^^^^^^^^

.. java:method:: public void addPropertyValue(OWLNamedIndividual i, OWLObjectProperty p, WrappedIndividual j)
   :outertype: CodeGenerationHelper

addPropertyValue
^^^^^^^^^^^^^^^^

.. java:method:: public void addPropertyValue(OWLNamedIndividual i, OWLDataProperty p, Object o)
   :outertype: CodeGenerationHelper

getLiteralFromObject
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public static OWLLiteral getLiteralFromObject(OWLDataFactory owlDataFactory, Object o)
   :outertype: CodeGenerationHelper

getObjectFromLiteral
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public static Object getObjectFromLiteral(OWLLiteral literal)
   :outertype: CodeGenerationHelper

getOwlIndividual
^^^^^^^^^^^^^^^^

.. java:method:: public OWLNamedIndividual getOwlIndividual()
   :outertype: CodeGenerationHelper

getOwlOntology
^^^^^^^^^^^^^^

.. java:method:: public OWLOntology getOwlOntology()
   :outertype: CodeGenerationHelper

getPropertyValues
^^^^^^^^^^^^^^^^^

.. java:method:: public <X> Collection<X> getPropertyValues(OWLNamedIndividual i, OWLObjectProperty p, Class<X> c)
   :outertype: CodeGenerationHelper

getPropertyValues
^^^^^^^^^^^^^^^^^

.. java:method:: public <X> Collection<X> getPropertyValues(OWLNamedIndividual i, OWLDataProperty p, Class<X> c)
   :outertype: CodeGenerationHelper

removePropertyValue
^^^^^^^^^^^^^^^^^^^

.. java:method:: public void removePropertyValue(OWLNamedIndividual i, OWLObjectProperty p, WrappedIndividual j)
   :outertype: CodeGenerationHelper

removePropertyValue
^^^^^^^^^^^^^^^^^^^

.. java:method:: public void removePropertyValue(OWLNamedIndividual i, OWLDataProperty p, Object o)
   :outertype: CodeGenerationHelper

