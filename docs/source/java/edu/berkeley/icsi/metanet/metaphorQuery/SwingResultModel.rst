.. java:import:: java.util ArrayList

.. java:import:: javax.swing.table AbstractTableModel

SwingResultModel
================

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery
   :noindex:

.. java:type:: public class SwingResultModel extends AbstractTableModel

Methods
-------
getColumnCount
^^^^^^^^^^^^^^

.. java:method:: @Override public int getColumnCount()
   :outertype: SwingResultModel

getColumnName
^^^^^^^^^^^^^

.. java:method:: @Override public String getColumnName(int column)
   :outertype: SwingResultModel

getRowCount
^^^^^^^^^^^

.. java:method:: @Override public int getRowCount()
   :outertype: SwingResultModel

getValueAt
^^^^^^^^^^

.. java:method:: @Override public Object getValueAt(int rowIndex, int columnIndex)
   :outertype: SwingResultModel

setResults
^^^^^^^^^^

.. java:method:: public void setResults(SparqlResultSet results)
   :outertype: SwingResultModel

