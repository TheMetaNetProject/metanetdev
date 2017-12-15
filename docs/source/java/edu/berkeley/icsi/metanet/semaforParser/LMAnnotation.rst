.. java:import:: java.util ArrayList

LMAnnotation
============

.. java:package:: edu.berkeley.icsi.metanet.semaforParser
   :noindex:

.. java:type:: public class LMAnnotation

   Java representation of SEMAFOR annotation set for a linguistic metaphor.

   :author: brandon

Constructors
------------
LMAnnotation
^^^^^^^^^^^^

.. java:constructor:: protected LMAnnotation(String sentence, String frameName)
   :outertype: LMAnnotation

   Constructs a new annotation set

   :param sentence: - the sentence
   :param targetLemma: - the target
   :param frameName: - the frame name

Methods
-------
addFrameElement
^^^^^^^^^^^^^^^

.. java:method:: protected void addFrameElement(int start, int end, String feName)
   :outertype: LMAnnotation

   Adds a new frame element to the annotation set

   :param start: - start index of the frame element
   :param end: end - index of the frame element
   :param feName: - the frame element name

getFrameElements
^^^^^^^^^^^^^^^^

.. java:method:: public ArrayList<FrameElement> getFrameElements()
   :outertype: LMAnnotation

   Get the frame elements of this annotation set

   :return: a Set of frame elements

getFrameName
^^^^^^^^^^^^

.. java:method:: public String getFrameName()
   :outertype: LMAnnotation

   Get the frame name of the this annotation set

   :return: the frame name

getName
^^^^^^^

.. java:method:: public String getName()
   :outertype: LMAnnotation

   Gets the name of the annotated linguistic metaphor, defined as the source and target stems concatenated with the same order as in the source sentence

   :return: the name of the linguistic metaphor

getSentence
^^^^^^^^^^^

.. java:method:: public String getSentence()
   :outertype: LMAnnotation

   Get the sentence associated with this annotation set

   :return: the sentence

getTarget
^^^^^^^^^

.. java:method:: public String getTarget()
   :outertype: LMAnnotation

   Get the name of the linguistic target of this linguistic metaphor

   :return: the target

main
^^^^

.. java:method:: public static void main(String args)
   :outertype: LMAnnotation

setSeed
^^^^^^^

.. java:method:: public void setSeed(String seed)
   :outertype: LMAnnotation

   Sets the LM seed of this seed

   :param seed: - the name of the LM seed

setSource
^^^^^^^^^

.. java:method:: public void setSource()
   :outertype: LMAnnotation

   Sets information for the linguistic source of the linguistic metaphor. Since SEMAFOR does not explicitly define the source of a LM, this method infers that the first frame element is the linguistic source. If this LMAnnotation has no frame elements, sets fields with default values (null for String fields and 0 for int fields)

setTarget
^^^^^^^^^

.. java:method:: public void setTarget(String name, int start, int end, String pos)
   :outertype: LMAnnotation

   Sets information about the linguistic target of this LM

   :param name: - stem of the linguistic target
   :param start: - start index of the target in the source sentence
   :param end: - end index of the target the source sentence
   :param pos: - part of speech of the linguistic target (usually a verb i.e. "v")

toJSON
^^^^^^

.. java:method:: public String toJSON()
   :outertype: LMAnnotation

   Renders this AnnotationSet into a JSON object

   :return: the JSON string representation of this AnnotationSet

