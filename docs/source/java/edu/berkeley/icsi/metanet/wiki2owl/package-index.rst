edu.berkeley.icsi.metanet.wiki2owl
==================================

This package uses a MediaWiki API to connect to the MetaNet Semantic
MediaWiki and retrieve pages that contain elements of the conceptual
networ.  Those pages are then parsed and converted into an RDF/OWL
format.  The package offers two modes of operation: as a standalone
program that writes out to file, or as a UI integrated plugin to
Protege 4.x.

The following classes implement the main functionality of the conversion
system:

=================================================================  ================================================================  
:java:ref:`edu.berkeley.icsi.metanet.wiki2owl.WikiLoader`          Connects to the wiki and retrieves pages in XML wrapped format
:java:ref:`edu.berkeley.icsi.metanet.wiki2owl.WikiPageHandler`     Parses the XML wrapped format
:java:ref:`edu.berkeley.icsi.metanet.wiki2owl.WikiParser`          Parses the MediaWiki page format
:java:ref:`edu.berkeley.icsi.metanet.wiki2owl.WikiTemplateParser`  Parses template calls within the MediaWiki page format
:java:ref:`edu.berkeley.icsi.metanet.wiki2owl.WikiFieldMap`        Defines translations between Wiki template variable names and OWL properties
=================================================================  ================================================================  

The following pages implement UI elements specific to use a Protege 4.x plugin:

* :java:ref:`edu.berkeley.icsi.metanet.wiki2owl.LoadFromEnglishWiki`
* :java:ref:`edu.berkeley.icsi.metanet.wiki2owl.LoadFromSpanishWiki`
* :java:ref:`edu.berkeley.icsi.metanet.wiki2owl.LoadFromRussianWiki`
* :java:ref:`edu.berkeley.icsi.metanet.wiki2owl.LoadFromPersianWiki`

The following class implements the command line interface to the converter:

* :java:ref:`edu.berkeley.icsi.metanet.wiki2owl.WikiParserCmd`

Package Contents
----------------

.. java:package:: edu.berkeley.icsi.metanet.wiki2owl

.. toctree::
   :maxdepth: 1

   LoadFromEnglishWiki
   LoadFromPersianWiki
   LoadFromRussianWiki
   LoadFromSpanishWiki
   LoadFromTestWiki
   WikiFieldMap
   WikiLoader
   WikiPageHandler
   WikiParser
   WikiParserCmd
   WikiTemplateParser

