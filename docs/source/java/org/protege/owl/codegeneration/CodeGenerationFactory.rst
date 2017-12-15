.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyStorageException

CodeGenerationFactory
=====================

.. java:package:: org.protege.owl.codegeneration
   :noindex:

.. java:type:: public interface CodeGenerationFactory

Methods
-------
as
^^

.. java:method::  <X extends WrappedIndividual> X as(WrappedIndividual resource, Class<? extends X> javaInterface)
   :outertype: CodeGenerationFactory

canAs
^^^^^

.. java:method::  boolean canAs(WrappedIndividual resource, Class<? extends WrappedIndividual> javaInterface)
   :outertype: CodeGenerationFactory

flushOwlReasoner
^^^^^^^^^^^^^^^^

.. java:method::  void flushOwlReasoner()
   :outertype: CodeGenerationFactory

getInference
^^^^^^^^^^^^

.. java:method::  CodeGenerationInference getInference()
   :outertype: CodeGenerationFactory

getJavaInterfaceFromOwlClass
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  Class<?> getJavaInterfaceFromOwlClass(OWLClass cls)
   :outertype: CodeGenerationFactory

getOwlClassFromJavaInterface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  OWLClass getOwlClassFromJavaInterface(Class<?> javaInterface)
   :outertype: CodeGenerationFactory

getOwlOntology
^^^^^^^^^^^^^^

.. java:method::  OWLOntology getOwlOntology()
   :outertype: CodeGenerationFactory

saveOwlOntology
^^^^^^^^^^^^^^^

.. java:method::  void saveOwlOntology() throws OWLOntologyStorageException
   :outertype: CodeGenerationFactory

