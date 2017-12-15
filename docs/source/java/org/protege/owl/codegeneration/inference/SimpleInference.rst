.. java:import:: java.util Collection

.. java:import:: java.util Collections

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: java.util TreeMap

.. java:import:: java.util TreeSet

.. java:import:: org.protege.owl.codegeneration.names CodeGenerationNames

.. java:import:: org.protege.owl.codegeneration.property JavaDataPropertyDeclarations

.. java:import:: org.protege.owl.codegeneration.property JavaObjectPropertyDeclarations

.. java:import:: org.protege.owl.codegeneration.property JavaPropertyDeclarations

.. java:import:: org.semanticweb.owlapi.model AxiomType

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLClassExpression

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyDomainAxiom

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyRangeAxiom

.. java:import:: org.semanticweb.owlapi.model OWLDataRange

.. java:import:: org.semanticweb.owlapi.model OWLDatatype

.. java:import:: org.semanticweb.owlapi.model OWLDatatypeRestriction

.. java:import:: org.semanticweb.owlapi.model OWLEntity

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectIntersectionOf

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyDomainAxiom

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyRangeAxiom

.. java:import:: org.semanticweb.owlapi.model OWLOntology

SimpleInference
===============

.. java:package:: org.protege.owl.codegeneration.inference
   :noindex:

.. java:type:: public class SimpleInference implements CodeGenerationInference

Constructors
------------
SimpleInference
^^^^^^^^^^^^^^^

.. java:constructor:: public SimpleInference(OWLOntology ontology)
   :outertype: SimpleInference

Methods
-------
canAs
^^^^^

.. java:method:: public boolean canAs(OWLNamedIndividual i, OWLClass c)
   :outertype: SimpleInference

flush
^^^^^

.. java:method:: public void flush()
   :outertype: SimpleInference

getDataPropertyValues
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<OWLLiteral> getDataPropertyValues(OWLNamedIndividual i, OWLDataProperty p)
   :outertype: SimpleInference

getIndividuals
^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLNamedIndividual> getIndividuals(OWLClass owlClass)
   :outertype: SimpleInference

getJavaPropertyDeclarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<JavaPropertyDeclarations> getJavaPropertyDeclarations(OWLClass cls, CodeGenerationNames names)
   :outertype: SimpleInference

getOWLOntology
^^^^^^^^^^^^^^

.. java:method:: public OWLOntology getOWLOntology()
   :outertype: SimpleInference

getObjectPropertyValues
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<? extends OWLIndividual> getObjectPropertyValues(OWLNamedIndividual i, OWLObjectPropertyExpression p)
   :outertype: SimpleInference

getOwlClasses
^^^^^^^^^^^^^

.. java:method:: public Collection<OWLClass> getOwlClasses()
   :outertype: SimpleInference

getRange
^^^^^^^^

.. java:method:: public OWLClass getRange(OWLObjectProperty p)
   :outertype: SimpleInference

getRange
^^^^^^^^

.. java:method:: public OWLClass getRange(OWLClass owlClass, OWLObjectProperty p)
   :outertype: SimpleInference

getRange
^^^^^^^^

.. java:method:: public OWLDatatype getRange(OWLDataProperty p)
   :outertype: SimpleInference

getRange
^^^^^^^^

.. java:method:: public OWLDatatype getRange(OWLClass owlClass, OWLDataProperty p)
   :outertype: SimpleInference

getSubClasses
^^^^^^^^^^^^^

.. java:method:: public Collection<OWLClass> getSubClasses(OWLClass owlClass)
   :outertype: SimpleInference

getSuperClasses
^^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLClass> getSuperClasses(OWLClass owlClass)
   :outertype: SimpleInference

getTypes
^^^^^^^^

.. java:method:: public Collection<OWLClass> getTypes(OWLNamedIndividual i)
   :outertype: SimpleInference

preCompute
^^^^^^^^^^

.. java:method:: public void preCompute()
   :outertype: SimpleInference

