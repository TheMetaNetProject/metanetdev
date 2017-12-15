.. java:import:: java.io ByteArrayInputStream

.. java:import:: java.io IOException

.. java:import:: java.io InputStream

.. java:import:: java.util ArrayList

.. java:import:: java.util Arrays

.. java:import:: java.util HashSet

.. java:import:: java.util List

.. java:import:: java.util Set

.. java:import:: java.util.logging Level

.. java:import:: java.util.logging Logger

.. java:import:: javax.security.auth.login FailedLoginException

.. java:import:: javax.swing JLabel

.. java:import:: javax.swing JProgressBar

.. java:import:: javax.swing SwingWorker

.. java:import:: javax.xml.parsers ParserConfigurationException

.. java:import:: javax.xml.parsers SAXParser

.. java:import:: javax.xml.parsers SAXParserFactory

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model PrefixManager

.. java:import:: org.wikipedia Wiki

.. java:import:: org.xml.sax SAXException

WikiParser
==========

.. java:package:: edu.berkeley.icsi.metanet.wiki2owl
   :noindex:

.. java:type:: public class WikiParser extends SwingWorker<Void, Void>

   Class for retrieving XML page exports from the metanet semantic mediawiki and populating an ontology with instances.

   :author: jhong

Fields
------
CATEGORIES
^^^^^^^^^^

.. java:field:: public static final List<String> CATEGORIES
   :outertype: WikiParser

LANGLIST
^^^^^^^^

.. java:field:: public static final Set<String> LANGLIST
   :outertype: WikiParser

Constructors
------------
WikiParser
^^^^^^^^^^

.. java:constructor:: public WikiParser()
   :outertype: WikiParser

Methods
-------
doInBackground
^^^^^^^^^^^^^^

.. java:method:: @Override protected Void doInBackground() throws Exception
   :outertype: WikiParser

getProgressMessage
^^^^^^^^^^^^^^^^^^

.. java:method:: public String getProgressMessage()
   :outertype: WikiParser

importWiki
^^^^^^^^^^

.. java:method:: public void importWiki() throws IOException
   :outertype: WikiParser

initializeWiki
^^^^^^^^^^^^^^

.. java:method:: public void initializeWiki() throws IOException
   :outertype: WikiParser

setLanguage
^^^^^^^^^^^

.. java:method:: public void setLanguage(String s)
   :outertype: WikiParser

setLogLevel
^^^^^^^^^^^

.. java:method:: public void setLogLevel(Level level)
   :outertype: WikiParser

setOntology
^^^^^^^^^^^

.. java:method:: public void setOntology(OWLOntology onto, String prefix)
   :outertype: WikiParser

setRepository
^^^^^^^^^^^^^

.. java:method:: public void setRepository(OWLOntology repo)
   :outertype: WikiParser

setWikiBase
^^^^^^^^^^^

.. java:method:: public void setWikiBase(String l)
   :outertype: WikiParser

setWikiLogin
^^^^^^^^^^^^

.. java:method:: public void setWikiLogin(String wikiuser, String wikipw)
   :outertype: WikiParser

setWikiServer
^^^^^^^^^^^^^

.. java:method:: public void setWikiServer(String s)
   :outertype: WikiParser

