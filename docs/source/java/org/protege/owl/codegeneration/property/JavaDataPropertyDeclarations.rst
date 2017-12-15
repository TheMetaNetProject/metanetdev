.. java:import:: java.util Map

.. java:import:: org.protege.owl.codegeneration Constants

.. java:import:: org.protege.owl.codegeneration HandledDatatypes

.. java:import:: org.protege.owl.codegeneration SubstitutionVariable

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDatatype

JavaDataPropertyDeclarations
============================

.. java:package:: org.protege.owl.codegeneration.property
   :noindex:

.. java:type:: public class JavaDataPropertyDeclarations implements JavaPropertyDeclarations

   This class represents the following java methods that are associated with an OWL dataproperty:

   .. parsed-literal::

      Collection extends ${propertyRangeForClass}> get${OwlProperty}();
      boolean has${OwlProperty}();
      void add${OwlProperty}(${propertyRange} new${OwlProperty});
      void remove${OwlProperty}(${propertyRange} old${OwlProperty});

   Note that these methods do get specialized as we move to subclasses.

   :author: tredmond

Constructors
------------
JavaDataPropertyDeclarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public JavaDataPropertyDeclarations(CodeGenerationInference inference, OWLClass owlClass, OWLDataProperty property)
   :outertype: JavaDataPropertyDeclarations

Methods
-------
configureSubstitutions
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void configureSubstitutions(Map<SubstitutionVariable, String> substitutions)
   :outertype: JavaDataPropertyDeclarations

getOwlProperty
^^^^^^^^^^^^^^

.. java:method:: public OWLDataProperty getOwlProperty()
   :outertype: JavaDataPropertyDeclarations

specializeTo
^^^^^^^^^^^^

.. java:method:: public JavaPropertyDeclarations specializeTo(OWLClass subclass)
   :outertype: JavaDataPropertyDeclarations

