.. java:import:: java.io File

.. java:import:: java.util Collection

.. java:import:: java.util Map

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLEntity

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

Worker
======

.. java:package:: org.protege.owl.codegeneration
   :noindex:

.. java:type:: public interface Worker

Methods
-------
configureSubstitutions
^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  void configureSubstitutions(CodeGenerationPhase phase, Map<SubstitutionVariable, String> substitutions, OWLClass owlClass, OWLEntity owlProperty)
   :outertype: Worker

getDataPropertiesForClass
^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  Collection<OWLDataProperty> getDataPropertiesForClass(OWLClass owlClass)
   :outertype: Worker

getFactoryFile
^^^^^^^^^^^^^^

.. java:method::  File getFactoryFile()
   :outertype: Worker

getImplementationFile
^^^^^^^^^^^^^^^^^^^^^

.. java:method::  File getImplementationFile(OWLClass c)
   :outertype: Worker

getInterfaceFile
^^^^^^^^^^^^^^^^

.. java:method::  File getInterfaceFile(OWLClass c)
   :outertype: Worker

getObjectPropertiesForClass
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  Collection<OWLObjectProperty> getObjectPropertiesForClass(OWLClass owlClass)
   :outertype: Worker

getOwlClasses
^^^^^^^^^^^^^

.. java:method::  Collection<OWLClass> getOwlClasses()
   :outertype: Worker

getOwlDataProperties
^^^^^^^^^^^^^^^^^^^^

.. java:method::  Collection<OWLDataProperty> getOwlDataProperties()
   :outertype: Worker

getOwlObjectProperties
^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  Collection<OWLObjectProperty> getOwlObjectProperties()
   :outertype: Worker

getOwlOntology
^^^^^^^^^^^^^^

.. java:method::  OWLOntology getOwlOntology()
   :outertype: Worker

getTemplate
^^^^^^^^^^^

.. java:method::  String getTemplate(CodeGenerationPhase phase, OWLClass owlClass, Object owlProperty)
   :outertype: Worker

getVocabularyFile
^^^^^^^^^^^^^^^^^

.. java:method::  File getVocabularyFile()
   :outertype: Worker

initialize
^^^^^^^^^^

.. java:method::  void initialize()
   :outertype: Worker

