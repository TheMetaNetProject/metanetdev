.. java:import:: java.io File

.. java:import:: java.io IOException

.. java:import:: java.io InputStreamReader

.. java:import:: java.io Reader

.. java:import:: java.net URL

.. java:import:: java.util EnumMap

CodeGenerationOptions
=====================

.. java:package:: org.protege.owl.codegeneration
   :noindex:

.. java:type:: public class CodeGenerationOptions

   This class stores the data required for owl code generator.

   :author: z.khan

Fields
------
FACTORY_CLASS_NAME
^^^^^^^^^^^^^^^^^^

.. java:field:: public static final String FACTORY_CLASS_NAME
   :outertype: CodeGenerationOptions

FACTORY_CLASS_NAME_DEFAULT
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final String FACTORY_CLASS_NAME_DEFAULT
   :outertype: CodeGenerationOptions

FILE_NAME
^^^^^^^^^

.. java:field:: public static final String FILE_NAME
   :outertype: CodeGenerationOptions

FILE_NAME_DEFAULT
^^^^^^^^^^^^^^^^^

.. java:field:: public static final String FILE_NAME_DEFAULT
   :outertype: CodeGenerationOptions

PACKAGE
^^^^^^^

.. java:field:: public static final String PACKAGE
   :outertype: CodeGenerationOptions

PACKAGE_DEFAULT
^^^^^^^^^^^^^^^

.. java:field:: public static final String PACKAGE_DEFAULT
   :outertype: CodeGenerationOptions

PREFIX_MODE
^^^^^^^^^^^

.. java:field:: public static final String PREFIX_MODE
   :outertype: CodeGenerationOptions

SET_MODE
^^^^^^^^

.. java:field:: public static final String SET_MODE
   :outertype: CodeGenerationOptions

Methods
-------
getFactoryClassName
^^^^^^^^^^^^^^^^^^^

.. java:method:: public String getFactoryClassName()
   :outertype: CodeGenerationOptions

getOutputFolder
^^^^^^^^^^^^^^^

.. java:method:: public File getOutputFolder()
   :outertype: CodeGenerationOptions

getPackage
^^^^^^^^^^

.. java:method:: public String getPackage()
   :outertype: CodeGenerationOptions

setFactoryClassName
^^^^^^^^^^^^^^^^^^^

.. java:method:: public void setFactoryClassName(String value)
   :outertype: CodeGenerationOptions

setOutputFolder
^^^^^^^^^^^^^^^

.. java:method:: public void setOutputFolder(File file)
   :outertype: CodeGenerationOptions

setPackage
^^^^^^^^^^

.. java:method:: public void setPackage(String value)
   :outertype: CodeGenerationOptions

setUseReasoner
^^^^^^^^^^^^^^

.. java:method:: public void setUseReasoner(boolean useReasoner)
   :outertype: CodeGenerationOptions

useReasoner
^^^^^^^^^^^

.. java:method:: public boolean useReasoner()
   :outertype: CodeGenerationOptions

