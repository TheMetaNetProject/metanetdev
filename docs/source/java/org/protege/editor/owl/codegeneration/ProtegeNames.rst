.. java:import:: org.protege.editor.owl.model OWLModelManager

.. java:import:: org.protege.owl.codegeneration CodeGenerationOptions

.. java:import:: org.protege.owl.codegeneration.names AbstractCodeGenerationNames

.. java:import:: org.protege.owl.codegeneration.names NamingUtilities

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

ProtegeNames
============

.. java:package:: org.protege.editor.owl.codegeneration
   :noindex:

.. java:type:: public class ProtegeNames extends AbstractCodeGenerationNames

Constructors
------------
ProtegeNames
^^^^^^^^^^^^

.. java:constructor:: public ProtegeNames(OWLModelManager manager, CodeGenerationOptions options)
   :outertype: ProtegeNames

Methods
-------
getClassName
^^^^^^^^^^^^

.. java:method:: public String getClassName(OWLClass owlClass)
   :outertype: ProtegeNames

getDataPropertyName
^^^^^^^^^^^^^^^^^^^

.. java:method:: public String getDataPropertyName(OWLDataProperty owlDataProperty)
   :outertype: ProtegeNames

getInterfaceName
^^^^^^^^^^^^^^^^

.. java:method:: public String getInterfaceName(OWLClass owlClass)
   :outertype: ProtegeNames

getObjectPropertyName
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public String getObjectPropertyName(OWLObjectProperty owlObjectProperty)
   :outertype: ProtegeNames

