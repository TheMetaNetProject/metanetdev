.. java:import:: java.util ArrayList

MediaWikiContainer
==================

.. java:package:: edu.berkeley.icsi.metanet.mwtemplateparser
   :noindex:

.. java:type:: public class MediaWikiContainer

   Instances of this class are used for storing objects found on MediaWiki pages. Each MediaWikiContainer class has a set of objects. Note that we can have nested containers, i.e.: - Metaphor (is of type MediaWikiContainer) - Aliases (is of type MediaWikiContainer) (Alias: foo1) (is of type Element) (Alias: foo2) (is of type Element)

   :author: Jalal Buckley

Fields
------
brackets
^^^^^^^^

.. java:field::  boolean brackets
   :outertype: MediaWikiContainer

containerName
^^^^^^^^^^^^^

.. java:field::  String containerName
   :outertype: MediaWikiContainer

page
^^^^

.. java:field::  ArrayList<Object> page
   :outertype: MediaWikiContainer

Constructors
------------
MediaWikiContainer
^^^^^^^^^^^^^^^^^^

.. java:constructor:: protected MediaWikiContainer(String name)
   :outertype: MediaWikiContainer

   Initialize a MediaWikiContainer object.

   :param name: the name of the MediaWikiContainer

Methods
-------
add
^^^

.. java:method:: protected void add(MediaWikiContainer con)
   :outertype: MediaWikiContainer

   Add an MediaWikiContainer object to this MediaWikiContainer's set of objects

   :param con: a MediaWikiContainer object

add
^^^

.. java:method:: protected void add(Element el)
   :outertype: MediaWikiContainer

   Add an Element object to this MediaWikiContainer's set of objects

   :param el:

bracketsHere
^^^^^^^^^^^^

.. java:method:: protected void bracketsHere(boolean bracket)
   :outertype: MediaWikiContainer

   If this MediaWikiContainer object corresponds to a "template" in the MediaWiki markup, we call this method.

   :param bracket: a boolean saying if this MediaWikiContainer is a "template"

fixSchemaNames
^^^^^^^^^^^^^^

.. java:method:: protected void fixSchemaNames()
   :outertype: MediaWikiContainer

   Fix Schema names so that they are separated by spaces, not underscores

getElementValues
^^^^^^^^^^^^^^^^

.. java:method:: protected ArrayList<String> getElementValues(String elementName)
   :outertype: MediaWikiContainer

   Iterate through all the elements on the page, and get all of the values associated with the chosen element. (For example, if you want to get all of the "Example.Text" values, run this method with "Example.Text" as the parameter).

   :return: String ArrayList of values

getLSource
^^^^^^^^^^

.. java:method:: protected String getLSource() throws Exception
   :outertype: MediaWikiContainer

   Return this Linguistic Metaphor's Linguistic Source

getLTarget
^^^^^^^^^^

.. java:method:: protected String getLTarget() throws Exception
   :outertype: MediaWikiContainer

   Return this Linguistic Metaphor's Linguistic Target

getName
^^^^^^^

.. java:method:: protected String getName()
   :outertype: MediaWikiContainer

hasAlias
^^^^^^^^

.. java:method:: protected void hasAlias(String containerTitle)
   :outertype: MediaWikiContainer

   Check that this metaphor has a metaphor alias corresponding with its title

outputToMediaWiki
^^^^^^^^^^^^^^^^^

.. java:method:: protected String outputToMediaWiki()
   :outertype: MediaWikiContainer

   Converts a MediaWikiContainer object to MediaWiki markup format

   :return: a MediaWiki markup representation of

printMediaWikiContainer
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: protected void printMediaWikiContainer(int indent)
   :outertype: MediaWikiContainer

   Prints a MediaWikiContainer object. Used for debugging.

   :param indent: number of indents

saveToXML
^^^^^^^^^

.. java:method:: protected String saveToXML(int indent)
   :outertype: MediaWikiContainer

   Converts a MediaWikiContainer object to XML

   :param indent: the number of indents
   :return: the XML representation of the MediaWikiContainer object

uncapRoles
^^^^^^^^^^

.. java:method:: protected void uncapRoles()
   :outertype: MediaWikiContainer

   Uncapitalize role names.

