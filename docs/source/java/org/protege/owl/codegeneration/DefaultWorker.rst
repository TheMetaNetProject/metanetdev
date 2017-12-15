.. java:import:: java.io File

.. java:import:: java.io IOException

.. java:import:: java.io InputStreamReader

.. java:import:: java.io Reader

.. java:import:: java.net URL

.. java:import:: java.util Collection

.. java:import:: java.util Date

.. java:import:: java.util EnumMap

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: java.util TreeSet

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.protege.owl.codegeneration.inference SimpleInference

.. java:import:: org.protege.owl.codegeneration.names CodeGenerationNames

.. java:import:: org.protege.owl.codegeneration.names NamingUtilities

.. java:import:: org.protege.owl.codegeneration.property JavaPropertyDeclarationCache

.. java:import:: org.semanticweb.owlapi.model OWLAnnotation

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLEntity

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.vocab OWL2Datatype

DefaultWorker
=============

.. java:package:: org.protege.owl.codegeneration
   :noindex:

.. java:type:: public class DefaultWorker implements Worker

Constructors
------------
DefaultWorker
^^^^^^^^^^^^^

.. java:constructor:: public DefaultWorker(OWLOntology ontology, CodeGenerationOptions options, CodeGenerationNames names, CodeGenerationInference inference)
   :outertype: DefaultWorker

Methods
-------
configureSubstitutions
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void configureSubstitutions(CodeGenerationPhase phase, Map<SubstitutionVariable, String> substitutions, OWLClass owlClass, OWLEntity owlProperty)
   :outertype: DefaultWorker

generateCode
^^^^^^^^^^^^

.. java:method:: public static void generateCode(OWLOntology ontology, CodeGenerationOptions options, CodeGenerationNames names) throws IOException
   :outertype: DefaultWorker

generateCode
^^^^^^^^^^^^

.. java:method:: public static void generateCode(OWLOntology ontology, CodeGenerationOptions options, CodeGenerationNames names, CodeGenerationInference inference) throws IOException
   :outertype: DefaultWorker

getDataPropertiesForClass
^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLDataProperty> getDataPropertiesForClass(OWLClass owlClass)
   :outertype: DefaultWorker

getFactoryFile
^^^^^^^^^^^^^^

.. java:method:: public File getFactoryFile()
   :outertype: DefaultWorker

getImplementationFile
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public File getImplementationFile(OWLClass owlClass)
   :outertype: DefaultWorker

getInterfaceFile
^^^^^^^^^^^^^^^^

.. java:method:: public File getInterfaceFile(OWLClass owlClass)
   :outertype: DefaultWorker

getObjectPropertiesForClass
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLObjectProperty> getObjectPropertiesForClass(OWLClass owlClass)
   :outertype: DefaultWorker

getOwlClasses
^^^^^^^^^^^^^

.. java:method:: public Collection<OWLClass> getOwlClasses()
   :outertype: DefaultWorker

getOwlDataProperties
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLDataProperty> getOwlDataProperties()
   :outertype: DefaultWorker

getOwlObjectProperties
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<OWLObjectProperty> getOwlObjectProperties()
   :outertype: DefaultWorker

getOwlOntology
^^^^^^^^^^^^^^

.. java:method:: public OWLOntology getOwlOntology()
   :outertype: DefaultWorker

getTemplate
^^^^^^^^^^^

.. java:method:: public String getTemplate(CodeGenerationPhase phase, OWLClass owlClass, Object owlProperty)
   :outertype: DefaultWorker

getVocabularyFile
^^^^^^^^^^^^^^^^^

.. java:method:: public File getVocabularyFile()
   :outertype: DefaultWorker

initialize
^^^^^^^^^^

.. java:method:: public void initialize()
   :outertype: DefaultWorker

