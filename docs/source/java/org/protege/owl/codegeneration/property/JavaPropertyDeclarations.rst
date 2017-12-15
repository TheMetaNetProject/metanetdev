.. java:import:: java.util Map

.. java:import:: org.protege.owl.codegeneration SubstitutionVariable

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLEntity

JavaPropertyDeclarations
========================

.. java:package:: org.protege.owl.codegeneration.property
   :noindex:

.. java:type:: public interface JavaPropertyDeclarations

   This class is a representation of the interface and implementation methods that will be generated for a particular property. The reason that it became necessary to write this class is that there appears to be a fundamental conflict between OWL ontologies and the generated java code. In the java code if

   ..

   * A class or interface X has a method m,
   * A class or interface Y extends/implements the class X

   then it must be true that the class or interface Y has a method that specializes the method m.

   Most of the obvious ways of determining the way that the declarations for a java class corresponding to an OWL class do not satisfy this criterion. For example, one might think that a java interface corresponding to an OWL class, A, should have methods corresponding to any property that has A as a domain. Unfortunately this definition can violate the requirements above. In addition the java notion of \ *specializes*\  does not always correspond to the natural ways of specializing that would come from an OWL ontology.

   :author: tredmond

Methods
-------
configureSubstitutions
^^^^^^^^^^^^^^^^^^^^^^

.. java:method::  void configureSubstitutions(Map<SubstitutionVariable, String> substitutions)
   :outertype: JavaPropertyDeclarations

getOwlProperty
^^^^^^^^^^^^^^

.. java:method::  OWLEntity getOwlProperty()
   :outertype: JavaPropertyDeclarations

specializeTo
^^^^^^^^^^^^

.. java:method::  JavaPropertyDeclarations specializeTo(OWLClass subclass)
   :outertype: JavaPropertyDeclarations

