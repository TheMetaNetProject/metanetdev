.. java:import:: java.awt BorderLayout

.. java:import:: java.awt Dimension

.. java:import:: java.awt FlowLayout

.. java:import:: java.util ArrayList

.. java:import:: java.util HashMap

.. java:import:: java.util Set

.. java:import:: javax.swing.event ListSelectionEvent

.. java:import:: javax.swing.event ListSelectionListener

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

OptionsPanel
============

.. java:package:: edu.berkeley.icsi.metanet.metavisual
   :noindex:

.. java:type:: public class OptionsPanel extends JPanel

Fields
------
individualTabs
^^^^^^^^^^^^^^

.. java:field:: protected JTabbedPane individualTabs
   :outertype: OptionsPanel

Constructors
------------
OptionsPanel
^^^^^^^^^^^^

.. java:constructor:: public OptionsPanel(OWLOntology owlModel, EntityLibrary library)
   :outertype: OptionsPanel

Methods
-------
getMetaphorRelations
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Object getMetaphorRelations()
   :outertype: OptionsPanel

getSchemaRelations
^^^^^^^^^^^^^^^^^^

.. java:method:: public Object getSchemaRelations()
   :outertype: OptionsPanel

getSelectedIndividual
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public OWLNamedIndividual getSelectedIndividual()
   :outertype: OptionsPanel

