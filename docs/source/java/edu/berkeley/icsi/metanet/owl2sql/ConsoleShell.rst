.. java:import:: java.io Console

.. java:import:: java.sql Connection

.. java:import:: java.sql SQLException

.. java:import:: java.sql Statement

.. java:import:: org.semanticweb.owlapi.model OWLOntology

ConsoleShell
============

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public class ConsoleShell extends Shell

Fields
------
console
^^^^^^^

.. java:field::  Console console
   :outertype: ConsoleShell

Constructors
------------
ConsoleShell
^^^^^^^^^^^^

.. java:constructor:: protected ConsoleShell()
   :outertype: ConsoleShell

Methods
-------
establishConnection
^^^^^^^^^^^^^^^^^^^

.. java:method:: @Override  Connection establishConnection()
   :outertype: ConsoleShell

getDBName
^^^^^^^^^

.. java:method:: @Override  String getDBName()
   :outertype: ConsoleShell

initTableBuilder
^^^^^^^^^^^^^^^^

.. java:method:: @Override  TableBuilder initTableBuilder(OWLOntology ont, Statement stmt)
   :outertype: ConsoleShell

