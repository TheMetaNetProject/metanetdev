edu.berkeley.icsi.metanet.owl2sql
=================================

This class is used to populate a MySQL database from a RDF/OWL representation
of the MetaNet conceptual network.  The structure of the resulting database
represents a relational database housing for the RDF triples.  This is to
allow the MetaNet conceptual network to be searched using SQL queries
rather than SPARQL.

Package Contents
----------------

.. java:package:: edu.berkeley.icsi.metanet.owl2sql

.. toctree::
   :maxdepth: 1

   Basics
   CmdLineShell
   Connector
   ConsoleShell
   DatabaseHandler
   FullTableBuilder
   Shell
   SimpleTableBuilder
   SimpleTableBuilder-BlobIDsTuple
   TableBuilder
   Utilities

