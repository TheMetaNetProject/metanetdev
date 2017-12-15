.. java:import:: java.io File

.. java:import:: java.io FileInputStream

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

FrameNetLUIndexParser
=====================

.. java:package:: edu.berkeley.icsi.metanet.lmtocmlinker
   :noindex:

.. java:type:: public class FrameNetLUIndexParser

Fields
------
FRAME
^^^^^

.. java:field:: static final String FRAME
   :outertype: FrameNetLUIndexParser

LEXUNIT
^^^^^^^

.. java:field:: static final String LEXUNIT
   :outertype: FrameNetLUIndexParser

LU
^^

.. java:field:: static final String LU
   :outertype: FrameNetLUIndexParser

localfile
^^^^^^^^^

.. java:field:: static final String localfile
   :outertype: FrameNetLUIndexParser

Methods
-------
getLU2FrameMap
^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, Set<String>> getLU2FrameMap() throws IOException
   :outertype: FrameNetLUIndexParser

   Takes a FrameNet LU Index document URL and generates a HashMap that maps Lemmas to a set of Frames, e.g. "push.v", ["Cause_motion", etc]

   :param URL: string to FrameNet LU Index XML
   :return: HashMap from lemmas to sets of frame names

