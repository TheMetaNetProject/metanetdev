.. java:import:: java.io FileNotFoundException

.. java:import:: java.io IOException

.. java:import:: java.io InputStream

.. java:import:: java.net URL

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Iterator

.. java:import:: java.util Set

.. java:import:: javax.xml.stream XMLEventReader

.. java:import:: javax.xml.stream XMLInputFactory

.. java:import:: javax.xml.stream XMLStreamException

.. java:import:: javax.xml.stream.events Attribute

.. java:import:: javax.xml.stream.events EndElement

.. java:import:: javax.xml.stream.events StartElement

.. java:import:: javax.xml.stream.events XMLEvent

XMLParser
=========

.. java:package:: edu.berkeley.icsi.metanet.metalookup
   :noindex:

.. java:type:: public class XMLParser

Fields
------
LEXUNIT
^^^^^^^

.. java:field:: static final String LEXUNIT
   :outertype: XMLParser

LU
^^

.. java:field:: static final String LU
   :outertype: XMLParser

NAME
^^^^

.. java:field:: static final String NAME
   :outertype: XMLParser

Methods
-------
parseDocument
^^^^^^^^^^^^^

.. java:method:: public HashMap<String, Set<String>> parseDocument(String luDoc) throws IOException
   :outertype: XMLParser

