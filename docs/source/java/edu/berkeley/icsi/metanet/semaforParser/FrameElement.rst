.. java:import:: java.io IOException

.. java:import:: com.fasterxml.jackson.core JsonFactory

.. java:import:: com.fasterxml.jackson.core JsonParseException

.. java:import:: com.fasterxml.jackson.core JsonParser

.. java:import:: com.fasterxml.jackson.core JsonToken

FrameElement
============

.. java:package:: edu.berkeley.icsi.metanet.semaforParser
   :noindex:

.. java:type:: public class FrameElement

   A class representing a semantic frame element.

   :author: brandon

Fields
------
feName
^^^^^^

.. java:field:: protected String feName
   :outertype: FrameElement

start
^^^^^

.. java:field:: protected int start
   :outertype: FrameElement

Constructors
------------
FrameElement
^^^^^^^^^^^^

.. java:constructor:: protected FrameElement()
   :outertype: FrameElement

FrameElement
^^^^^^^^^^^^

.. java:constructor:: protected FrameElement(String sentence, int start, int end, String name)
   :outertype: FrameElement

FrameElement
^^^^^^^^^^^^

.. java:constructor:: protected FrameElement(JsonParser jp) throws JsonParseException, IOException
   :outertype: FrameElement

   Constructs a frame element from the given JsonParser object.

   :param jp: - JsonParser must be such that getCurrentToken() returns the start of the object. i.e. nextToken() must have been called at least once already.

Methods
-------
getContent
^^^^^^^^^^

.. java:method:: public String getContent()
   :outertype: FrameElement

   Get the content of the frame element

   :return: the content of the frame element

getIndexes
^^^^^^^^^^

.. java:method:: public int[] getIndexes()
   :outertype: FrameElement

   Get the start and end indexes for the frame element. Can be used to extract the frame element content from the annotation set's sentence.

   :return: a two-element array of the form [start, end]

getName
^^^^^^^

.. java:method:: public String getName()
   :outertype: FrameElement

   Get the name of the frame element

   :return: the name of the frame element

main
^^^^

.. java:method:: public static void main(String args) throws JsonParseException, IOException
   :outertype: FrameElement

toJSON
^^^^^^

.. java:method:: public String toJSON()
   :outertype: FrameElement

toString
^^^^^^^^

.. java:method:: @Override public String toString()
   :outertype: FrameElement

