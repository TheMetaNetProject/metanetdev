.. java:import:: java.util Map

.. java:import:: org.protege.owl.codegeneration Constants

.. java:import:: org.protege.owl.codegeneration SubstitutionVariable

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.protege.owl.codegeneration.names CodeGenerationNames

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

JavaObjectPropertyDeclarations
==============================

.. java:package:: org.protege.owl.codegeneration.property
   :noindex:

.. java:type:: public class JavaObjectPropertyDeclarations implements JavaPropertyDeclarations

   This class represents the following java methods that are associated with an OWL object property:

   .. parsed-literal::

      Collection extends ${propertyRange}> get${OwlProperty}();
      boolean has${OwlProperty}();
      void add${OwlProperty}(${propertyRange} new${OwlProperty});
      void remove${OwlProperty}(${propertyRange} old${OwlProperty});

   Note that these methods do not get specialized as we move to subclasses.

   :author: tredmond

Constructors
------------
JavaObjectPropertyDeclarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public JavaObjectPropertyDeclarations(CodeGenerationInference inference, CodeGenerationNames names, OWLObjectProperty property)
   :outertype: JavaObjectPropertyDeclarations

Methods
-------
configureSubstitutions
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void configureSubstitutions(Map<SubstitutionVariable, String> substitutions)
   :outertype: JavaObjectPropertyDeclarations

getOwlProperty
^^^^^^^^^^^^^^

.. java:method:: public OWLObjectProperty getOwlProperty()
   :outertype: JavaObjectPropertyDeclarations

specializeTo
^^^^^^^^^^^^

.. java:method:: public JavaPropertyDeclarations specializeTo(OWLClass subclass)
   :outertype: JavaObjectPropertyDeclarations

