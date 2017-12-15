.. java:import:: java.io File

.. java:import:: java.io IOException

.. java:import:: org.apache.log4j Logger

.. java:import:: org.protege.owl.codegeneration CodeGenerationOptions

.. java:import:: org.protege.owl.codegeneration DefaultWorker

.. java:import:: org.protege.owl.codegeneration Utilities

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.protege.owl.codegeneration.inference ReasonerBasedInference

.. java:import:: org.protege.owl.codegeneration.inference SimpleInference

.. java:import:: org.protege.owl.codegeneration.names IriNames

.. java:import:: org.semanticweb.owlapi.apibinding OWLManager

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyCreationException

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasoner

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasonerFactory

.. java:import:: org.semanticweb.owlapi.util AutoIRIMapper

.. java:import:: org.semanticweb.owlapi.util SimpleIRIMapper

GenerateTestCode
================

.. java:package:: org.protege.owl.codegeneration.test
   :noindex:

.. java:type:: public class GenerateTestCode

   Ordinarily I wouldn't corrupt the main source tree with testing code. But this seems like a reasonable exception at this time. This bootstraps the maven test build process. It should be the only test file that appears in the main tree.

   :author: tredmond

Fields
------
FEB_PATH
^^^^^^^^

.. java:field:: public static final String FEB_PATH
   :outertype: GenerateTestCode

FEB_TBOX_ONTOLOGY
^^^^^^^^^^^^^^^^^

.. java:field:: public static final String FEB_TBOX_ONTOLOGY
   :outertype: GenerateTestCode

LOGGER
^^^^^^

.. java:field:: public static Logger LOGGER
   :outertype: GenerateTestCode

ONTOLOGY_ROOT
^^^^^^^^^^^^^

.. java:field:: public static final File ONTOLOGY_ROOT
   :outertype: GenerateTestCode

Methods
-------
addIRIMappers
^^^^^^^^^^^^^

.. java:method:: public static void addIRIMappers(OWLOntologyManager manager)
   :outertype: GenerateTestCode

main
^^^^

.. java:method:: public static void main(String args) throws Exception
   :outertype: GenerateTestCode

   :param args:

