.. java:import:: java.io IOException

.. java:import:: java.sql SQLException

TableBuilder
============

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public interface TableBuilder

   Interface for table builders

   :author: brandon

Methods
-------
build
^^^^^

.. java:method::  void build() throws SQLException
   :outertype: TableBuilder

   Builds the database

enableErrorLogging
^^^^^^^^^^^^^^^^^^

.. java:method::  void enableErrorLogging(String logPath) throws IOException
   :outertype: TableBuilder

