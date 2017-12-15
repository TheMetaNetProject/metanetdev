.. java:import:: java.io File

.. java:import:: java.io IOException

.. java:import:: org.apache.commons.cli BasicParser

.. java:import:: org.apache.commons.cli CommandLine

.. java:import:: org.apache.commons.cli HelpFormatter

.. java:import:: org.apache.commons.cli Options

.. java:import:: org.apache.commons.cli ParseException

.. java:import:: org.apache.log4j Logger

.. java:import:: org.protege.owl.codegeneration CodeGenerationOptions

.. java:import:: org.protege.owl.codegeneration DefaultWorker

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.protege.owl.codegeneration.inference ReasonerBasedInference

.. java:import:: org.protege.owl.codegeneration.inference SimpleInference

.. java:import:: org.protege.owl.codegeneration.names IriNames

.. java:import:: org.protege.owl.codegeneration.test GenerateTestCode

.. java:import:: org.semanticweb.owlapi.apibinding OWLManager

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyCreationException

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasoner

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasonerFactory

GenerateSimpleJavaCode
======================

.. java:package:: org.protege.owl.codegeneration.main
   :noindex:

.. java:type:: public class GenerateSimpleJavaCode

Fields
------
DELETE_OPT
^^^^^^^^^^

.. java:field:: public static final String DELETE_OPT
   :outertype: GenerateSimpleJavaCode

FACTORY_OPT
^^^^^^^^^^^

.. java:field:: public static final String FACTORY_OPT
   :outertype: GenerateSimpleJavaCode

LOGGER
^^^^^^

.. java:field:: public static Logger LOGGER
   :outertype: GenerateSimpleJavaCode

OUTPUT_OPT
^^^^^^^^^^

.. java:field:: public static final String OUTPUT_OPT
   :outertype: GenerateSimpleJavaCode

PACKAGE_OPT
^^^^^^^^^^^

.. java:field:: public static final String PACKAGE_OPT
   :outertype: GenerateSimpleJavaCode

REASONER_OPT
^^^^^^^^^^^^

.. java:field:: public static final String REASONER_OPT
   :outertype: GenerateSimpleJavaCode

Methods
-------
main
^^^^

.. java:method:: public static void main(String args) throws Exception
   :outertype: GenerateSimpleJavaCode

