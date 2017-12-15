.. java:import:: java.util Collection

.. java:import:: java.util Set

.. java:import:: org.protege.owl.codegeneration.names CodeGenerationNames

.. java:import:: org.protege.owl.codegeneration.property JavaPropertyDeclarations

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLDatatype

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLOntology

CodeGenerationInference
=======================

.. java:package:: org.protege.owl.codegeneration.inference
   :noindex:

.. java:type:: public interface CodeGenerationInference

Methods
-------
canAs
^^^^^

.. java:method::  boolean canAs(OWLNamedIndividual i, OWLClass c)
   :outertype: CodeGenerationInference

flush
^^^^^

.. java:method::  void flush()
   :outertype: CodeGenerationInference

getDataPropertyValues
^^^^^^^^^^^^^^^^^^^^^

.. java:method::  Collection<OWLLiteral> getDataPropertyValues(OWLNamedIndividual i, OWLDataProperty p)
   :outertype: CodeGenerationInference

getIndividuals
^^^^^^^^^^^^^^

.. java:method::  Collection<OWLNamedIndividual> getIndividuals(OWLClass owlClass)
   :outertype: CodeGenerationInference

getJavaPropertyDeclarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  Set<JavaPropertyDeclarations> getJavaPropertyDeclarations(OWLClass cls, CodeGenerationNames names)
   :outertype: CodeGenerationInference

getOWLOntology
^^^^^^^^^^^^^^

.. java:method::  OWLOntology getOWLOntology()
   :outertype: CodeGenerationInference

getObjectPropertyValues
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  Collection<? extends OWLIndividual> getObjectPropertyValues(OWLNamedIndividual i, OWLObjectPropertyExpression p)
   :outertype: CodeGenerationInference

getOwlClasses
^^^^^^^^^^^^^

.. java:method::  Collection<OWLClass> getOwlClasses()
   :outertype: CodeGenerationInference

getRange
^^^^^^^^

.. java:method::  OWLClass getRange(OWLObjectProperty p)
   :outertype: CodeGenerationInference

getRange
^^^^^^^^

.. java:method::  OWLClass getRange(OWLClass owlClass, OWLObjectProperty p)
   :outertype: CodeGenerationInference

getRange
^^^^^^^^

.. java:method::  OWLDatatype getRange(OWLDataProperty p)
   :outertype: CodeGenerationInference

getRange
^^^^^^^^

.. java:method::  OWLDatatype getRange(OWLClass owlClass, OWLDataProperty p)
   :outertype: CodeGenerationInference

getSubClasses
^^^^^^^^^^^^^

.. java:method::  Collection<OWLClass> getSubClasses(OWLClass owlClass)
   :outertype: CodeGenerationInference

getSuperClasses
^^^^^^^^^^^^^^^

.. java:method::  Collection<OWLClass> getSuperClasses(OWLClass owlClass)
   :outertype: CodeGenerationInference

getTypes
^^^^^^^^

.. java:method::  Collection<OWLClass> getTypes(OWLNamedIndividual i)
   :outertype: CodeGenerationInference

preCompute
^^^^^^^^^^

.. java:method::  void preCompute()
   :outertype: CodeGenerationInference

