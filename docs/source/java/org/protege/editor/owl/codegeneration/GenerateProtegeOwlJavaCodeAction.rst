.. java:import:: java.awt Component

.. java:import:: java.awt Dimension

.. java:import:: java.awt Point

.. java:import:: java.awt.event ActionEvent

.. java:import:: java.io File

.. java:import:: java.io IOException

.. java:import:: javax.swing JFrame

.. java:import:: javax.swing JOptionPane

.. java:import:: org.apache.log4j Logger

.. java:import:: org.protege.editor.core ProtegeApplication

.. java:import:: org.protege.editor.core.prefs Preferences

.. java:import:: org.protege.editor.core.prefs PreferencesManager

.. java:import:: org.protege.editor.owl.model OWLModelManager

.. java:import:: org.protege.editor.owl.ui.action ProtegeOWLAction

.. java:import:: org.protege.owl.codegeneration CodeGenerationOptions

.. java:import:: org.protege.owl.codegeneration DefaultWorker

.. java:import:: org.protege.owl.codegeneration Utilities

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.protege.owl.codegeneration.inference ReasonerBasedInference

.. java:import:: org.protege.owl.codegeneration.inference SimpleInference

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.reasoner OWLReasoner

GenerateProtegeOwlJavaCodeAction
================================

.. java:package:: org.protege.editor.owl.codegeneration
   :noindex:

.. java:type:: public class GenerateProtegeOwlJavaCodeAction extends ProtegeOWLAction implements GenerateCodeCallback

   :author: z.khan

Fields
------
CODE_GENERATION_PREFERENCES
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final String CODE_GENERATION_PREFERENCES
   :outertype: GenerateProtegeOwlJavaCodeAction

FACTORY_PREFS_KEY
^^^^^^^^^^^^^^^^^

.. java:field:: public static final String FACTORY_PREFS_KEY
   :outertype: GenerateProtegeOwlJavaCodeAction

FOLDER_PREFS_KEY
^^^^^^^^^^^^^^^^

.. java:field:: public static final String FOLDER_PREFS_KEY
   :outertype: GenerateProtegeOwlJavaCodeAction

LOGGER
^^^^^^

.. java:field:: public static final Logger LOGGER
   :outertype: GenerateProtegeOwlJavaCodeAction

PACKAGE_PREFS_KEY
^^^^^^^^^^^^^^^^^

.. java:field:: public static final String PACKAGE_PREFS_KEY
   :outertype: GenerateProtegeOwlJavaCodeAction

Methods
-------
actionPerformed
^^^^^^^^^^^^^^^

.. java:method:: public void actionPerformed(ActionEvent e)
   :outertype: GenerateProtegeOwlJavaCodeAction

cancelClicked
^^^^^^^^^^^^^

.. java:method:: public void cancelClicked()
   :outertype: GenerateProtegeOwlJavaCodeAction

center
^^^^^^

.. java:method:: public static void center(Component component)
   :outertype: GenerateProtegeOwlJavaCodeAction

   Sets the generator panel to center

   :param component:

dispose
^^^^^^^

.. java:method:: public void dispose() throws Exception
   :outertype: GenerateProtegeOwlJavaCodeAction

initialise
^^^^^^^^^^

.. java:method:: public void initialise() throws Exception
   :outertype: GenerateProtegeOwlJavaCodeAction

okClicked
^^^^^^^^^

.. java:method:: public void okClicked()
   :outertype: GenerateProtegeOwlJavaCodeAction

