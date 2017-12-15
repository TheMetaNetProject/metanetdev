.. java:import:: edu.berkeley.icsi.metanet.mwtemplateparser MediaWikiParse

.. java:import:: java.io BufferedWriter

.. java:import:: java.io File

.. java:import:: java.io FileWriter

.. java:import:: java.io IOException

.. java:import:: java.util ArrayList

.. java:import:: java.util List

.. java:import:: javax.security.auth.login FailedLoginException

.. java:import:: org.apache.commons.cli CommandLine

.. java:import:: org.apache.commons.cli CommandLineParser

.. java:import:: org.apache.commons.cli HelpFormatter

.. java:import:: org.apache.commons.cli Options

.. java:import:: org.apache.commons.cli ParseException

.. java:import:: org.apache.commons.cli PosixParser

.. java:import:: org.wikipedia Wiki

WikiExtracter
=============

.. java:package:: edu.berkeley.icsi.metanet.semaforParser
   :noindex:

.. java:type:: public class WikiExtracter

   A class that extracts template information from the Metanet MediaWiki and outputs it to text files in such a way that SEMAFOR and the XMLParser can use.

   :author: bgthai

Constructors
------------
WikiExtracter
^^^^^^^^^^^^^

.. java:constructor:: protected WikiExtracter()
   :outertype: WikiExtracter

   Constructs a new WikiExtracter and sets the CLI options

Methods
-------
initConnection
^^^^^^^^^^^^^^

.. java:method:: protected void initConnection()
   :outertype: WikiExtracter

   Initialize connection to the Wiki page using the set login credentials and server info

main
^^^^

.. java:method:: public static void main(String args) throws IOException
   :outertype: WikiExtracter

processAllPages
^^^^^^^^^^^^^^^

.. java:method:: protected void processAllPages() throws IOException
   :outertype: WikiExtracter

   Process all linguistic metaphor pages for the set Wiki connection

processCmdLineArgs
^^^^^^^^^^^^^^^^^^

.. java:method:: protected void processCmdLineArgs(String args)
   :outertype: WikiExtracter

   Processes the command-line arguments for CLI options and for the two file name arguments

   :param args: - the array of command-line arguments given in main()

processWikiPage
^^^^^^^^^^^^^^^

.. java:method:: protected void processWikiPage(String pageTitle) throws IOException
   :outertype: WikiExtracter

   Process the given Wiki page. Extracts the linguistic source, linguistic target, and all example sentences, and writes them out to the sentence and lemma files.

   :param pageTitle: - title of the page to be processed

setWikiBase
^^^^^^^^^^^

.. java:method:: protected void setWikiBase(String base)
   :outertype: WikiExtracter

   Set the Wiki basename for the Wiki connection

setWikiPw
^^^^^^^^^

.. java:method:: protected void setWikiPw(String pw)
   :outertype: WikiExtracter

   Set the user password for the Wiki connection

setWikiServer
^^^^^^^^^^^^^

.. java:method:: protected void setWikiServer(String server)
   :outertype: WikiExtracter

   Set the Wiki server name for the Wiki connection

setWikiUser
^^^^^^^^^^^

.. java:method:: protected void setWikiUser(String username)
   :outertype: WikiExtracter

   Set user login for the Wiki connection

