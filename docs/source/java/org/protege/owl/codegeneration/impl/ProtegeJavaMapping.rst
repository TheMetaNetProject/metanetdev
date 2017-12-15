.. java:import:: java.lang.reflect Constructor

.. java:import:: java.util Collection

.. java:import:: java.util HashMap

.. java:import:: java.util Map

.. java:import:: org.protege.owl.codegeneration WrappedIndividual

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.semanticweb.owlapi.apibinding OWLManager

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

ProtegeJavaMapping
==================

.. java:package:: org.protege.owl.codegeneration.impl
   :noindex:

.. java:type:: public class ProtegeJavaMapping

Methods
-------
add
^^^

.. java:method:: public void add(String protegeClassName, Class<?> javaInterface, Class<? extends WrappedIndividualImpl> javaImplementation)
   :outertype: ProtegeJavaMapping

add
^^^

.. java:method:: public void add(OWLClass protegeClass, Class<?> javaInterface, Class<? extends WrappedIndividualImpl> javaImplementation)
   :outertype: ProtegeJavaMapping

as
^^

.. java:method:: public <X extends WrappedIndividual> X as(WrappedIndividual resource, Class<? extends X> javaInterface)
   :outertype: ProtegeJavaMapping

canAs
^^^^^

.. java:method:: public boolean canAs(WrappedIndividual resource, Class<? extends WrappedIndividual> javaInterface)
   :outertype: ProtegeJavaMapping

create
^^^^^^

.. java:method:: @SuppressWarnings public <X> X create(Class<? extends X> javaInterface, String name)
   :outertype: ProtegeJavaMapping

getJavaInterfaceFromOwlClass
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Class<?> getJavaInterfaceFromOwlClass(OWLClass cls)
   :outertype: ProtegeJavaMapping

getOwlClassFromJavaInterface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public OWLClass getOwlClassFromJavaInterface(Class<?> javaInterface)
   :outertype: ProtegeJavaMapping

initialize
^^^^^^^^^^

.. java:method:: public void initialize(OWLOntology ontology, CodeGenerationInference inference)
   :outertype: ProtegeJavaMapping

