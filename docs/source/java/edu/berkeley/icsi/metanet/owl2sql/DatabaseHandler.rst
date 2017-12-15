.. java:import:: java.sql SQLException

.. java:import:: java.sql Statement

DatabaseHandler
===============

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public class DatabaseHandler

Methods
-------
prepare
^^^^^^^

.. java:method:: protected static void prepare(Statement stmt, String dbName, boolean doDrop) throws SQLException
   :outertype: DatabaseHandler

   Drops the previous database if necessary and creates a new database

