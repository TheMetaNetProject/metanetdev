.. java:import:: java.util.logging Level

.. java:import:: java.util.logging Logger

.. java:import:: org.xml.sax Attributes

.. java:import:: org.xml.sax SAXException

.. java:import:: org.xml.sax.helpers DefaultHandler

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model PrefixManager

WikiPageHandler
===============

.. java:package:: edu.berkeley.icsi.metanet.wiki2owl
   :noindex:

.. java:type:: public class WikiPageHandler extends DefaultHandler

   Class for parsing the mediawiki export XML format. For exports from Special:Export

   :author: jhong

Fields
------
content
^^^^^^^

.. java:field::  StringBuffer content
   :outertype: WikiPageHandler

inid
^^^^

.. java:field::  boolean inid
   :outertype: WikiPageHandler

inpage
^^^^^^

.. java:field::  boolean inpage
   :outertype: WikiPageHandler

inrevision
^^^^^^^^^^

.. java:field::  boolean inrevision
   :outertype: WikiPageHandler

intext
^^^^^^

.. java:field::  boolean intext
   :outertype: WikiPageHandler

intitle
^^^^^^^

.. java:field::  boolean intitle
   :outertype: WikiPageHandler

lang
^^^^

.. java:field::  String lang
   :outertype: WikiPageHandler

ontoPrefix
^^^^^^^^^^

.. java:field::  String ontoPrefix
   :outertype: WikiPageHandler

ontology
^^^^^^^^

.. java:field::  OWLOntology ontology
   :outertype: WikiPageHandler

pageId
^^^^^^

.. java:field::  String pageId
   :outertype: WikiPageHandler

pageText
^^^^^^^^

.. java:field::  String pageText
   :outertype: WikiPageHandler

pageTitle
^^^^^^^^^

.. java:field::  String pageTitle
   :outertype: WikiPageHandler

pm
^^

.. java:field::  PrefixManager pm
   :outertype: WikiPageHandler

repository
^^^^^^^^^^

.. java:field::  OWLOntology repository
   :outertype: WikiPageHandler

Methods
-------
characters
^^^^^^^^^^

.. java:method:: @Override public void characters(char[] ch, int start, int length) throws SAXException
   :outertype: WikiPageHandler

endElement
^^^^^^^^^^

.. java:method:: @Override public void endElement(String namespaceURI, String localName, String qName) throws SAXException
   :outertype: WikiPageHandler

setLanguage
^^^^^^^^^^^

.. java:method:: public void setLanguage(String s)
   :outertype: WikiPageHandler

setLogLevel
^^^^^^^^^^^

.. java:method:: public void setLogLevel(Level level)
   :outertype: WikiPageHandler

setOntology
^^^^^^^^^^^

.. java:method:: public void setOntology(OWLOntology onto, String pref)
   :outertype: WikiPageHandler

setRepository
^^^^^^^^^^^^^

.. java:method:: public void setRepository(OWLOntology repo)
   :outertype: WikiPageHandler

startElement
^^^^^^^^^^^^

.. java:method:: @Override public void startElement(String namespaceURI, String localName, String qName, Attributes atts) throws SAXException
   :outertype: WikiPageHandler

