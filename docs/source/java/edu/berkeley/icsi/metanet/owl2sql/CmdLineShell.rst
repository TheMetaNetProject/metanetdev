.. java:import:: java.sql Connection

.. java:import:: java.sql SQLException

.. java:import:: java.sql Statement

.. java:import:: org.apache.commons.cli CommandLine

.. java:import:: org.semanticweb.owlapi.model OWLOntology

CmdLineShell
============

.. java:package:: edu.berkeley.icsi.metanet.owl2sql
   :noindex:

.. java:type:: public class CmdLineShell extends Shell

Fields
------
cmd
^^^

.. java:field::  CommandLine cmd
   :outertype: CmdLineShell

dbName
^^^^^^

.. java:field::  String dbName
   :outertype: CmdLineShell

Constructors
------------
CmdLineShell
^^^^^^^^^^^^

.. java:constructor:: public CmdLineShell(CommandLine cmd)
   :outertype: CmdLineShell

Methods
-------
establishConnection
^^^^^^^^^^^^^^^^^^^

.. java:method:: @Override  Connection establishConnection()
   :outertype: CmdLineShell

getDBName
^^^^^^^^^

.. java:method:: @Override  String getDBName()
   :outertype: CmdLineShell

initTableBuilder
^^^^^^^^^^^^^^^^

.. java:method:: @Override  TableBuilder initTableBuilder(OWLOntology ont, Statement stmt)
   :outertype: CmdLineShell

