.. java:import:: java.util HashSet

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: java.util.regex Pattern

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLClassExpression

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLNamedObject

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLObjectPropertyExpression

.. java:import:: org.semanticweb.owlapi.model OWLOntology

Utilities
=========

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public class Utilities

   :author: brandon

Methods
-------
extractClasses
^^^^^^^^^^^^^^

.. java:method:: public static HashSet<OWLClass> extractClasses(OWLClassExpression owlClassExp)
   :outertype: Utilities

   Returns the of disjunct OWL classes in the given OWLClassExpression. Handles named OWL classes and disjunct anonymous classes but ignores other types of anonymous classes.

   :param owlClassExp:
   :return: the set of disjunct OWL classes in the given class expression

format
^^^^^^

.. java:method:: public static String format(String str)
   :outertype: Utilities

   Takes the given string and returns it in a SQL-acceptable format (i.e. with escaped characters)

getDatatype
^^^^^^^^^^^

.. java:method:: public static String getDatatype(int maxKeyLength, int keySize)
   :outertype: Utilities

getInsertString
^^^^^^^^^^^^^^^

.. java:method:: public static String getInsertString(String tableName, Map<String, String> fieldValueMap)
   :outertype: Utilities

   Returns a SQL INSERT statement for the given table and with the given values. Automatically truncates data values that are too long.

   :param tableName: - name of the target table
   :param fieldValueMap: - maps the name of each field to the string representation of its value. If the value is itself a string, it should not be delimitted by apostrophes. For example, "value" rather than "'value'".
   :return: a SQL INSERT statement

getName
^^^^^^^

.. java:method:: public static String getName(OWLNamedObject obj)
   :outertype: Utilities

   Finds the human-readable name of an OWL object

   :param obj: - A named OWL object

getSubClasses
^^^^^^^^^^^^^

.. java:method:: public static HashSet<OWLClass> getSubClasses(OWLClass owlClass, Set<OWLOntology> ontClosure)
   :outertype: Utilities

   Returns the set of all named subclasses of the given OWL class, including the given OWL class

   :param owlClass: - the named OWL class
   :param ont: - the ontology containing the OWL class
   :return: the set of all named subclasses, including the given OWL class

getSuperClasses
^^^^^^^^^^^^^^^

.. java:method:: public static HashSet<OWLClass> getSuperClasses(OWLClass owlClass, Set<OWLOntology> ontClosure)
   :outertype: Utilities

   Returns the set of all named super-classes of the given OWL class, including the given OWL class

   :param owlClass: - the named OWL class
   :param ont: - the ontology containing the OWL class
   :return: the set of all named subclasses, including the given OWL class

getSuperProps
^^^^^^^^^^^^^

.. java:method:: public static HashSet<OWLObjectProperty> getSuperProps(OWLObjectProperty objProp, Set<OWLOntology> ontClosure)
   :outertype: Utilities

   Returns the set of all named super-properties of the given object property, including the given object property itself

   :param objProp: - the named OWL object property
   :param ont: - the OWL ontology containing the object property
   :return: the set of all named superproperties of the given object property, including the given object property itself

getSuperProps
^^^^^^^^^^^^^

.. java:method:: public static HashSet<OWLDataProperty> getSuperProps(OWLDataProperty dataProp, Set<OWLOntology> ontClosure)
   :outertype: Utilities

   Returns the set of all named super-properties of the given data property including the given data property itself

   :param dataProp: - the named OWL data property
   :param ont: - the OWL ontology containing the data property
   :return: the set of all named superproperties of the given data property, including the given data property itself

getUpdateString
^^^^^^^^^^^^^^^

.. java:method:: public static String getUpdateString(String tableName, String pkName, int pkValue, Map<String, String> fieldValueMap)
   :outertype: Utilities

isValidDBName
^^^^^^^^^^^^^

.. java:method:: public static boolean isValidDBName(String dbName)
   :outertype: Utilities

   Checks if the given string is a valid MySQL database name

   :param dbName: - the proposed database name
   :return: true if the name is valid, false if not

