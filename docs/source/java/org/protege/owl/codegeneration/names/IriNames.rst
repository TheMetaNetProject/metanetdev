.. java:import:: org.protege.owl.codegeneration CodeGenerationOptions

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.util ShortFormProvider

.. java:import:: org.semanticweb.owlapi.util SimpleShortFormProvider

IriNames
========

.. java:package:: org.protege.owl.codegeneration.names
   :noindex:

.. java:type:: public class IriNames extends AbstractCodeGenerationNames

Constructors
------------
IriNames
^^^^^^^^

.. java:constructor:: public IriNames(OWLOntology ontology, CodeGenerationOptions options)
   :outertype: IriNames

Methods
-------
getClassName
^^^^^^^^^^^^

.. java:method:: public String getClassName(OWLClass owlClass)
   :outertype: IriNames

getDataPropertyName
^^^^^^^^^^^^^^^^^^^

.. java:method:: public String getDataPropertyName(OWLDataProperty owlDataProperty)
   :outertype: IriNames

getInterfaceName
^^^^^^^^^^^^^^^^

.. java:method:: public String getInterfaceName(OWLClass owlClass)
   :outertype: IriNames

getObjectPropertyName
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public String getObjectPropertyName(OWLObjectProperty owlObjectProperty)
   :outertype: IriNames

