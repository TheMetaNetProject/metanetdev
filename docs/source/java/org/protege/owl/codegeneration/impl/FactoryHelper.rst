.. java:import:: java.lang.reflect Constructor

.. java:import:: java.util Collection

.. java:import:: java.util HashSet

.. java:import:: java.util Set

.. java:import:: org.protege.owl.codegeneration CodeGenerationRuntimeException

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

FactoryHelper
=============

.. java:package:: org.protege.owl.codegeneration.impl
   :noindex:

.. java:type:: public class FactoryHelper

Constructors
------------
FactoryHelper
^^^^^^^^^^^^^

.. java:constructor:: public FactoryHelper(OWLOntology ontology, CodeGenerationInference inference)
   :outertype: FactoryHelper

Methods
-------
createWrappedIndividual
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public <X extends WrappedIndividualImpl> X createWrappedIndividual(String name, OWLClass type, Class<X> c)
   :outertype: FactoryHelper

flushOwlReasoner
^^^^^^^^^^^^^^^^

.. java:method:: public void flushOwlReasoner()
   :outertype: FactoryHelper

getWrappedIndividual
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public <X extends WrappedIndividualImpl> X getWrappedIndividual(String name, OWLClass type, Class<X> c)
   :outertype: FactoryHelper

getWrappedIndividuals
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public <X extends WrappedIndividualImpl> Collection<X> getWrappedIndividuals(OWLClass owlClass, Class<X> c)
   :outertype: FactoryHelper

