.. java:import:: java.io File

.. java:import:: java.lang.reflect Constructor

.. java:import:: java.lang.reflect InvocationTargetException

.. java:import:: java.lang.reflect Method

.. java:import:: java.lang.reflect ParameterizedType

.. java:import:: java.lang.reflect Type

.. java:import:: java.lang.reflect WildcardType

.. java:import:: java.util Collection

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.protege.owl.codegeneration.inference ReasonerBasedInference

.. java:import:: org.protege.owl.codegeneration.inference SimpleInference

.. java:import:: org.protege.owl.codegeneration.test GenerateTestCode

.. java:import:: org.semanticweb.owlapi.apibinding OWLManager

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyCreationException

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasoner

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasonerFactory

.. java:import:: org.testng Assert

TestUtilities
=============

.. java:package:: org.protege.owl.codegeneration
   :noindex:

.. java:type:: public class TestUtilities

Fields
------
FEB_INDIVIDUALS_ONTOLOGY
^^^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static String FEB_INDIVIDUALS_ONTOLOGY
   :outertype: TestUtilities

NS01
^^^^

.. java:field:: public static String NS01
   :outertype: TestUtilities

ONTOLOGY01
^^^^^^^^^^

.. java:field:: public static String ONTOLOGY01
   :outertype: TestUtilities

PIZZA_NS
^^^^^^^^

.. java:field:: public static String PIZZA_NS
   :outertype: TestUtilities

PIZZA_ONTOLOGY
^^^^^^^^^^^^^^

.. java:field:: public static String PIZZA_ONTOLOGY
   :outertype: TestUtilities

Methods
-------
assertMethodNotFound
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public static void assertMethodNotFound(Class<?> c, String method, Class<?>... arguments)
   :outertype: TestUtilities

assertReturnsCollectionOf
^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public static void assertReturnsCollectionOf(Method m, Class<?> c)
   :outertype: TestUtilities

openFactory
^^^^^^^^^^^

.. java:method:: public static <X> X openFactory(String ontologyLocation, Class<X> factoryClass, boolean useInference) throws SecurityException, NoSuchMethodException, OWLOntologyCreationException, InstantiationException, IllegalAccessException, ClassNotFoundException, IllegalArgumentException, InvocationTargetException
   :outertype: TestUtilities

