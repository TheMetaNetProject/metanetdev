.. java:import:: java.util Collection

.. java:import:: java.util List

.. java:import:: edu.berkeley.icsi.metanet.repository Metaphor

.. java:import:: edu.berkeley.icsi.metanet.repository Schema

MetaNetInterface
================

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery
   :noindex:

.. java:type:: public interface MetaNetInterface

Methods
-------
getAllMetaphorsRelatedToBy
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<? extends Metaphor> getAllMetaphorsRelatedToBy(String metaphorName, String propertyName)
   :outertype: MetaNetInterface

getAllSchemasRelatedToBy
^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<? extends Schema> getAllSchemasRelatedToBy(String schemaName, String propertyName)
   :outertype: MetaNetInterface

getMetaphorsRelatedToBy
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<? extends Metaphor> getMetaphorsRelatedToBy(String metaphorName, String propertyName)
   :outertype: MetaNetInterface

getSchemasRelatedToBy
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<? extends Schema> getSchemasRelatedToBy(String schemaName, String propertyName)
   :outertype: MetaNetInterface

runGeneralQuery
^^^^^^^^^^^^^^^

.. java:method:: public List<Object> runGeneralQuery(String query)
   :outertype: MetaNetInterface

