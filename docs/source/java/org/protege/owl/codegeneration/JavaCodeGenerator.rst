.. java:import:: java.io File

.. java:import:: java.io FileWriter

.. java:import:: java.io IOException

.. java:import:: java.io PrintWriter

.. java:import:: java.util Collection

.. java:import:: java.util EnumMap

.. java:import:: java.util Map

.. java:import:: java.util Map.Entry

.. java:import:: org.apache.log4j Logger

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLEntity

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

JavaCodeGenerator
=================

.. java:package:: org.protege.owl.codegeneration
   :noindex:

.. java:type:: public class JavaCodeGenerator

   A class that can create Java interfaces in the Protege-OWL format

   :author: z.khan

Fields
------
LOGGER
^^^^^^

.. java:field:: public static final Logger LOGGER
   :outertype: JavaCodeGenerator

Constructors
------------
JavaCodeGenerator
^^^^^^^^^^^^^^^^^

.. java:constructor:: public JavaCodeGenerator(Worker worker)
   :outertype: JavaCodeGenerator

   Constructor

   :param owlOntology:
   :param options:

Methods
-------
createAll
^^^^^^^^^

.. java:method:: public void createAll() throws IOException
   :outertype: JavaCodeGenerator

   Initiates the code generation

   :param reasoner:

fillTemplate
^^^^^^^^^^^^

.. java:method:: public static void fillTemplate(PrintWriter writer, String template, Map<SubstitutionVariable, String> substitutions)
   :outertype: JavaCodeGenerator

