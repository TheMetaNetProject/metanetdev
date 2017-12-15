.. java:import:: java.io BufferedReader

.. java:import:: java.io BufferedWriter

.. java:import:: java.io File

.. java:import:: java.io FileNotFoundException

.. java:import:: java.io FileReader

.. java:import:: java.io FileWriter

.. java:import:: java.io IOException

.. java:import:: java.util LinkedHashSet

.. java:import:: java.util Set

.. java:import:: javax.xml.parsers DocumentBuilderFactory

.. java:import:: javax.xml.parsers ParserConfigurationException

.. java:import:: org.w3c.dom Document

.. java:import:: org.w3c.dom Element

.. java:import:: org.w3c.dom Node

.. java:import:: org.w3c.dom NodeList

.. java:import:: org.xml.sax SAXException

XMLParser
=========

.. java:package:: edu.berkeley.icsi.metanet.semaforParser
   :noindex:

.. java:type:: public class XMLParser

   Parses the XML output of SEMAFOR

   :author: brandon

Constructors
------------
XMLParser
^^^^^^^^^

.. java:constructor:: public XMLParser(File xmlFile, File targetLemmaFile, File lemmaTagsFile)
   :outertype: XMLParser

   Constructs an XML parser

   :param xmlFile:
   :param targetLemmaFile:
   :param lemmaTagsFile:

Methods
-------
main
^^^^

.. java:method:: public static void main(String args) throws IOException
   :outertype: XMLParser

parseToFile
^^^^^^^^^^^

.. java:method:: public void parseToFile(File file) throws IOException
   :outertype: XMLParser

   Writes out all this parser's sentence annotations to a file

   :param file: - the file to write to

toJSON
^^^^^^

.. java:method:: public String toJSON()
   :outertype: XMLParser

   Converts all this parser's sentence annotations to JSON

   :return: JSON representation of this parser's sentence annotations

