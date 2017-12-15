Element
=======

.. java:package:: edu.berkeley.icsi.metanet.mwtemplateparser
   :noindex:

.. java:type:: public class Element

   The Element class provides a one to one mapping from a String to a String or from a String to an instance of MediaWikiContainer. For example: ("Alias": "fooAlias") is a mapping between a String ("Alias") and a String ("fooAlias") ("Aliases": setOfAliases) is a mapping between a String ("Aliases") and a MediaWikiContainer object (setOfAliases)

   :author: Jalal Buckley

Fields
------
elementName
^^^^^^^^^^^

.. java:field::  String elementName
   :outertype: Element

elementValue
^^^^^^^^^^^^

.. java:field::  String elementValue
   :outertype: Element

setOfObjects
^^^^^^^^^^^^

.. java:field::  MediaWikiContainer setOfObjects
   :outertype: Element

Constructors
------------
Element
^^^^^^^

.. java:constructor:: protected Element(String name, String val)
   :outertype: Element

   Create an Element object that is a mapping from a String to a String

   :param name: The Element's name
   :param eVal: The Element's value

Element
^^^^^^^

.. java:constructor:: protected Element(String name, MediaWikiContainer con)
   :outertype: Element

   Create an Element object that is a mapping from a String to a MediaWikiContainer object

   :param name: The Element's name
   :param con: The Element's MediaWikiContainer

Methods
-------
getElementName
^^^^^^^^^^^^^^

.. java:method:: protected String getElementName()
   :outertype: Element

   Get an Element object's elementName

   :param elementName:
   :return: elementName

getElementValue
^^^^^^^^^^^^^^^

.. java:method:: protected String getElementValue()
   :outertype: Element

   Get an Element object's elementValue

   :param elementName:
   :return: elementValue

outputToMediaWiki
^^^^^^^^^^^^^^^^^

.. java:method:: protected String outputToMediaWiki()
   :outertype: Element

   Converts an Element object to MediaWiki markup

   :return: MediaWiki markup

print
^^^^^

.. java:method:: protected void print(int indent)
   :outertype: Element

   Prints out the contents of an Element object. Used for debugging purposes.

   :param indent: the number of indents

saveToXML
^^^^^^^^^

.. java:method:: protected String saveToXML(int indent)
   :outertype: Element

   Converts an Element object to XML.

   :param indent: the number of indents
   :return: XML text

setElementValue
^^^^^^^^^^^^^^^

.. java:method:: protected void setElementValue(String value)
   :outertype: Element

   Set element value

   :param value:

