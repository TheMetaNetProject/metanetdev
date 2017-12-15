.. java:import:: org.protege.editor.owl.model OWLModelManager

GenerateCodeCallback
====================

.. java:package:: org.protege.editor.owl.codegeneration
   :noindex:

.. java:type:: public interface GenerateCodeCallback

   :author: z.khan

Methods
-------
cancelClicked
^^^^^^^^^^^^^

.. java:method::  void cancelClicked()
   :outertype: GenerateCodeCallback

   Called when user cancels code generation

getOWLModelManager
^^^^^^^^^^^^^^^^^^

.. java:method::  OWLModelManager getOWLModelManager()
   :outertype: GenerateCodeCallback

okClicked
^^^^^^^^^

.. java:method::  void okClicked()
   :outertype: GenerateCodeCallback

   Called when user prompts to generate code

