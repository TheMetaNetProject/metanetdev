.. java:import:: edu.berkeley.icsi.metanet.repository LexicalUnit

.. java:import:: edu.berkeley.icsi.metanet.repository LinguisticMetaphor

.. java:import:: edu.berkeley.icsi.metanet.repository MetaNetFactory

.. java:import:: edu.berkeley.icsi.metanet.repository Metaphor

.. java:import:: edu.berkeley.icsi.metanet.repository Schema

.. java:import:: java.util ArrayList

.. java:import:: java.util Arrays

.. java:import:: java.util Collection

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util List

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: javax.swing JTextArea

.. java:import:: org.apache.commons.lang3 StringUtils

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

MetaphorFinder
==============

.. java:package:: edu.berkeley.icsi.metanet.lmtocmlinker
   :noindex:

.. java:type:: public class MetaphorFinder

   :author: jhong

Constructors
------------
MetaphorFinder
^^^^^^^^^^^^^^

.. java:constructor::  MetaphorFinder(OWLOntology model, MetaNetFactory mfact, Map<String, Set<String>> frames, JTextArea console)
   :outertype: MetaphorFinder

Methods
-------
doLexicalUnitPreprocessing
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Map<String, Set<LexicalUnit>> doLexicalUnitPreprocessing()
   :outertype: MetaphorFinder

doSchemaPreprocessing
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Map<String, Set<Schema>> doSchemaPreprocessing()
   :outertype: MetaphorFinder

findCMsforLM
^^^^^^^^^^^^

.. java:method:: public Object findCMsforLM(LinguisticMetaphor lm)
   :outertype: MetaphorFinder

runSearch
^^^^^^^^^

.. java:method:: public Object runSearch(Collection<SearchPanelListItem> items)
   :outertype: MetaphorFinder

setFrame2Schema
^^^^^^^^^^^^^^^

.. java:method:: public void setFrame2Schema(Map<String, Set<Schema>> fs)
   :outertype: MetaphorFinder

setLemma2Lu
^^^^^^^^^^^

.. java:method:: public void setLemma2Lu(Map<String, Set<LexicalUnit>> ll)
   :outertype: MetaphorFinder

