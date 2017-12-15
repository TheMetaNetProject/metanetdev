.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Map

.. java:import:: java.util Set

WikiFieldMap
============

.. java:package:: edu.berkeley.icsi.metanet.wiki2owl
   :noindex:

.. java:type:: public class WikiFieldMap

   Contains mappings from metanet semantic mediawiki property names to OWL property names, as well as some other facilities for translation from wiki to owl.

   :author: jhong

Methods
-------
getInstanceName
^^^^^^^^^^^^^^^

.. java:method:: public static String getInstanceName(String className)
   :outertype: WikiFieldMap

hasName
^^^^^^^

.. java:method:: public static boolean hasName(String className)
   :outertype: WikiFieldMap

isAnnotationProp
^^^^^^^^^^^^^^^^

.. java:method:: public static boolean isAnnotationProp(String prop)
   :outertype: WikiFieldMap

trans
^^^^^

.. java:method:: public static String trans(String pageType, String fieldName)
   :outertype: WikiFieldMap

transmetarel
^^^^^^^^^^^^

.. java:method:: public static String transmetarel(String relName)
   :outertype: WikiFieldMap

transschemarel
^^^^^^^^^^^^^^

.. java:method:: public static String transschemarel(String relName)
   :outertype: WikiFieldMap

