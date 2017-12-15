.. java:import:: java.util HashSet

.. java:import:: java.util Iterator

.. java:import:: java.util Set

SentenceAnnotation
==================

.. java:package:: edu.berkeley.icsi.metanet.semaforParser
   :noindex:

.. java:type:: public class SentenceAnnotation

   Java representation of the SEMAFOR annotation of one sentence. Contains multiple linguistic metaphor "annotation sets".

   :author: brandon

Constructors
------------
SentenceAnnotation
^^^^^^^^^^^^^^^^^^

.. java:constructor:: public SentenceAnnotation(int id, String text)
   :outertype: SentenceAnnotation

   Constructs a new SentenceAnnotation

   :param id: - the unique sentence ID as defined by the SEMAFOR output
   :param text: - the sentence text

Methods
-------
addLM
^^^^^

.. java:method:: public void addLM(LMAnnotation lm)
   :outertype: SentenceAnnotation

   Adds a LM annotation to this sentence annotation's set of LM annotations

   :param lm: - the LMAnnotation to add

getID
^^^^^

.. java:method:: public int getID()
   :outertype: SentenceAnnotation

   Get the unique sentence ID as defined by the SEMAFOR output

   :return: the sentence ID

getLMIterator
^^^^^^^^^^^^^

.. java:method:: public Iterator<LMAnnotation> getLMIterator()
   :outertype: SentenceAnnotation

   Gets the iterator the sentence annotation's set of LM annotations

   :return: - an LMAnnotation iterator

getText
^^^^^^^

.. java:method:: public String getText()
   :outertype: SentenceAnnotation

   Get the sentence text

   :return: the sentence text

toJSON
^^^^^^

.. java:method:: public String toJSON()
   :outertype: SentenceAnnotation

   Returns the JSON representation of this sentence annotation

   :return: JSON string

