.. java:import:: java.util Collections

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Map

.. java:import:: java.util Map.Entry

.. java:import:: java.util Set

.. java:import:: java.util TreeSet

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.protege.owl.codegeneration.names CodeGenerationNames

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLEntity

.. java:import:: org.semanticweb.owlapi.model OWLObject

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

JavaPropertyDeclarationCache
============================

.. java:package:: org.protege.owl.codegeneration.property
   :noindex:

.. java:type:: public class JavaPropertyDeclarationCache

   This class provides a java property declarations object for any class and property. The primary responsibility of this class is to ensure that if

   ..

   * A class or interface X has a method m,
   * A class or interface Y extends/implements the class X

   then it must be true that the class or interface Y has a method that specializes the method m. By putting the code to ensure this property here we release other classes (such as the code generation inference) from concerning themselves with this issue.

Constructors
------------
JavaPropertyDeclarationCache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public JavaPropertyDeclarationCache(CodeGenerationInference inference, CodeGenerationNames names)
   :outertype: JavaPropertyDeclarationCache

Methods
-------
get
^^^

.. java:method:: public JavaPropertyDeclarations get(OWLClass clazz, OWLEntity property)
   :outertype: JavaPropertyDeclarationCache

getDataPropertiesForClass
^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<OWLDataProperty> getDataPropertiesForClass(OWLClass owlClass)
   :outertype: JavaPropertyDeclarationCache

getObjectPropertiesForClass
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Set<OWLObjectProperty> getObjectPropertiesForClass(OWLClass owlClass)
   :outertype: JavaPropertyDeclarationCache

