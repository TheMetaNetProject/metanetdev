.. java:import:: java.util ArrayList

.. java:import:: java.util List

SparqlResultSet
===============

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery
   :noindex:

.. java:type:: public class SparqlResultSet

Constructors
------------
SparqlResultSet
^^^^^^^^^^^^^^^

.. java:constructor:: public SparqlResultSet(List<String> colunmNames)
   :outertype: SparqlResultSet

Methods
-------
addRow
^^^^^^

.. java:method:: public void addRow(List<Object> row)
   :outertype: SparqlResultSet

getColumnCount
^^^^^^^^^^^^^^

.. java:method:: public int getColumnCount()
   :outertype: SparqlResultSet

getColumnName
^^^^^^^^^^^^^

.. java:method:: public String getColumnName(int col)
   :outertype: SparqlResultSet

getResult
^^^^^^^^^

.. java:method:: public Object getResult(int row, int col)
   :outertype: SparqlResultSet

getRowCount
^^^^^^^^^^^

.. java:method:: public int getRowCount()
   :outertype: SparqlResultSet

