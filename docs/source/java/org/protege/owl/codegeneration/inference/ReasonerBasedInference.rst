.. java:import:: java.util Collection

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: java.util TreeSet

.. java:import:: org.apache.log4j Logger

.. java:import:: org.protege.owl.codegeneration HandledDatatypes

.. java:import:: org.protege.owl.codegeneration.names CodeGenerationNames

.. java:import:: org.protege.owl.codegeneration.property JavaDataPropertyDeclarations

.. java:import:: org.protege.owl.codegeneration.property JavaObjectPropertyDeclarations

.. java:import:: org.protege.owl.codegeneration.property JavaPropertyDeclarations

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLClassExpression

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLDatatype

.. java:import:: org.semanticweb.owlapi.model OWLEntity

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.reasoner InferenceType

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasoner

ReasonerBasedInference
======================

.. java:package:: org.protege.owl.codegeneration.inference
   :noindex:

.. java:type:: public class ReasonerBasedInference implements CodeGenerationInference

Fields
------
LOGGER
^^^^^^

.. java:field:: public static final Logger LOGGER
   :outertype: ReasonerBasedInference

Constructors
------------
ReasonerBasedInference
^^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public ReasonerBasedInference(OWLOntology ontology, OWLReasoner reasoner)
   :outertype: ReasonerBasedInference

Methods
-------
canAs
^^^^^

.. java:method:: public boolean canAs(OWLNamedIndividual i, OWLClass c)
   :outertype: ReasonerBasedInference

flush
^^^^^

.. java:method:: public void flush()
   :outertype: ReasonerBasedInference

getDataPropertyValues
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<OWLLiteral> getDataPropertyValues(OWLNamedIndividual i, OWLDataProperty p)
   :outertype: ReasonerBasedInference

getIndividuals
^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLNamedIndividual> getIndividuals(OWLClass owlClass)
   :outertype: ReasonerBasedInference

getJavaPropertyDeclarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<JavaPropertyDeclarations> getJavaPropertyDeclarations(OWLClass cls, CodeGenerationNames names)
   :outertype: ReasonerBasedInference

getOWLOntology
^^^^^^^^^^^^^^

.. java:method:: public OWLOntology getOWLOntology()
   :outertype: ReasonerBasedInference

getObjectPropertyValues
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<? extends OWLIndividual> getObjectPropertyValues(OWLNamedIndividual i, OWLObjectPropertyExpression p)
   :outertype: ReasonerBasedInference

getOwlClasses
^^^^^^^^^^^^^

.. java:method:: public Collection<OWLClass> getOwlClasses()
   :outertype: ReasonerBasedInference

getRange
^^^^^^^^

.. java:method:: public OWLClass getRange(OWLObjectProperty p)
   :outertype: ReasonerBasedInference

getRange
^^^^^^^^

.. java:method:: public OWLClass getRange(OWLClass owlClass, OWLObjectProperty p)
   :outertype: ReasonerBasedInference

getRange
^^^^^^^^

.. java:method:: public OWLDatatype getRange(OWLDataProperty p)
   :outertype: ReasonerBasedInference

getRange
^^^^^^^^

.. java:method:: public OWLDatatype getRange(OWLClass owlClass, OWLDataProperty p)
   :outertype: ReasonerBasedInference

getSubClasses
^^^^^^^^^^^^^

.. java:method:: public Collection<OWLClass> getSubClasses(OWLClass owlClass)
   :outertype: ReasonerBasedInference

getSuperClasses
^^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLClass> getSuperClasses(OWLClass owlClass)
   :outertype: ReasonerBasedInference

getTypes
^^^^^^^^

.. java:method:: public Collection<OWLClass> getTypes(OWLNamedIndividual i)
   :outertype: ReasonerBasedInference

preCompute
^^^^^^^^^^

.. java:method:: public void preCompute()
   :outertype: ReasonerBasedInference

