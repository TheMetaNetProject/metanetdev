.. java:import:: java.sql Connection

.. java:import:: java.sql DriverManager

.. java:import:: java.sql ResultSet

.. java:import:: java.sql SQLException

.. java:import:: java.sql Statement

.. java:import:: java.util HashSet

.. java:import:: java.util Properties

Connector
=========

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public class Connector

Methods
-------
adequatePermissions
^^^^^^^^^^^^^^^^^^^

.. java:method:: protected static boolean adequatePermissions(Connection con) throws SQLException
   :outertype: Connector

getConnection
^^^^^^^^^^^^^

.. java:method:: protected static Connection getConnection(String server, int port, String username, String pw) throws SQLException
   :outertype: Connector

   Gets connection to the given MySQL server with the given user credentials.

   :param server: - Name of a MySQL server (i.e. localhost:3306)
   :param username: - Username
   :param pw: - Password

