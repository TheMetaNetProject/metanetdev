.. java:import:: java.util Scanner

.. java:import:: java.util ArrayList

.. java:import:: java.util HashMap

.. java:import:: java.util Set

.. java:import:: java.util.regex Pattern

MediaWikiParse
==============

.. java:package:: edu.berkeley.icsi.metanet.mwtemplateparser
   :noindex:

.. java:type:: public class MediaWikiParse

   This class is used for parsing a MediaWiki page and storing it in memory as a Java Data Structure. Once it is saved in memory, you can perform edits on it and convert it back into a MediaWiki page.

   :author: Jalal Buckley

Fields
------
pages
^^^^^

.. java:field::  HashMap<String, MediaWikiContainer> pages
   :outertype: MediaWikiParse

Constructors
------------
MediaWikiParse
^^^^^^^^^^^^^^

.. java:constructor:: public MediaWikiParse()
   :outertype: MediaWikiParse

   Constructor MediaWikiParse class. Initialize instance variables.

Methods
-------
aliasCheck
^^^^^^^^^^

.. java:method:: public void aliasCheck(String pageTitle)
   :outertype: MediaWikiParse

   Check that there is a metaphor alias corresponding to the page's title

   :param pageTitle:

fixSchema
^^^^^^^^^

.. java:method:: public void fixSchema(String pageTitle)
   :outertype: MediaWikiParse

   Make sure that words in a Schema name are separated by spaces, not underscores

   :param pageTitle:

getExampleTexts
^^^^^^^^^^^^^^^

.. java:method:: public ArrayList<String> getExampleTexts(String pageTitle)
   :outertype: MediaWikiParse

   :param pageTitle:

getLingSource
^^^^^^^^^^^^^

.. java:method:: public String getLingSource(String pageTitle) throws Exception
   :outertype: MediaWikiParse

   Get the Linguistic Source from a page.

   :param pageTitle:

getLingTarget
^^^^^^^^^^^^^

.. java:method:: public String getLingTarget(String pageTitle) throws Exception
   :outertype: MediaWikiParse

   Get the Linguistic Target from a page.

   :param pageTitle:

getPage
^^^^^^^

.. java:method:: public String getPage(String name)
   :outertype: MediaWikiParse

   Get the MediaWiki page associated with this name

   :param name: the page name
   :return: the MediaWiki page

getPageAsXML
^^^^^^^^^^^^

.. java:method:: public String getPageAsXML(String name)
   :outertype: MediaWikiParse

   Get the MediaWiki page associated with this name as an XML Document

   :param name: the page name
   :return: XML document

getPageNames
^^^^^^^^^^^^

.. java:method:: public Set<String> getPageNames()
   :outertype: MediaWikiParse

   Get the names of the pages that are saved in memory

   :return: Set of names

getTheElementValues
^^^^^^^^^^^^^^^^^^^

.. java:method:: public ArrayList<String> getTheElementValues(String pageTitle, String name)
   :outertype: MediaWikiParse

   Get all of the values associated with the chosen element. (i.e., find all of the "Example.Text"'s, etc.)

   :param name:

parseAndSave
^^^^^^^^^^^^

.. java:method:: public void parseAndSave(String title, String input)
   :outertype: MediaWikiParse

   Parse the MediaWiki page input and save it to memory. Return its name so the user can take note of it if desired.

   :param input: the MediaWiki page
   :return: the page's name

printContentsOfPage
^^^^^^^^^^^^^^^^^^^

.. java:method:: public void printContentsOfPage(String name)
   :outertype: MediaWikiParse

   Prints the contents of a page. Used for debugging purposes.

   :param name: the page name

removePage
^^^^^^^^^^

.. java:method:: public void removePage(String name)
   :outertype: MediaWikiParse

   Remove the MediaWiki page from memory with this name

   :param name: the page name

uncapitalizeRoles
^^^^^^^^^^^^^^^^^

.. java:method:: public void uncapitalizeRoles(String pageTitle)
   :outertype: MediaWikiParse

   Uncapitalize the roles

   :param pageTitle:

