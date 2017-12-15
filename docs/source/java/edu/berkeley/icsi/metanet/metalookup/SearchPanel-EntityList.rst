.. java:import:: edu.berkeley.icsi.metanet.repository LinguisticMetaphor

.. java:import:: edu.berkeley.icsi.metanet.repository MetaNetFactory

.. java:import:: edu.berkeley.icsi.metanet.repository Metaphor

.. java:import:: java.awt BorderLayout

.. java:import:: java.awt Dimension

.. java:import:: java.awt.event ActionEvent

.. java:import:: java.awt.event ActionListener

.. java:import:: java.util ArrayList

.. java:import:: java.util Collection

.. java:import:: java.util Collections

.. java:import:: java.util Comparator

.. java:import:: java.util HashMap

.. java:import:: java.util List

.. java:import:: javax.swing Box

.. java:import:: javax.swing BoxLayout

.. java:import:: javax.swing DefaultListModel

.. java:import:: javax.swing JButton

.. java:import:: javax.swing JLabel

.. java:import:: javax.swing JPanel

.. java:import:: javax.swing JScrollPane

.. java:import:: javax.swing JTextField

.. java:import:: javax.swing RowFilter

.. java:import:: javax.swing RowFilter.Entry

.. java:import:: javax.swing.event DocumentEvent

.. java:import:: javax.swing.event DocumentListener

.. java:import:: javax.swing.event ListSelectionEvent

.. java:import:: javax.swing.event ListSelectionListener

.. java:import:: javax.swing.text BadLocationException

.. java:import:: javax.swing.text Document

.. java:import:: org.jdesktop.swingx JXList

.. java:import:: org.protege.owl.codegeneration WrappedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

SearchPanel.EntityList
======================

.. java:package:: edu.berkeley.icsi.metanet.metalookup
   :noindex:

.. java:type::  class EntityList extends JScrollPane
   :outertype: SearchPanel

Fields
------
lingList
^^^^^^^^

.. java:field:: protected JXList lingList
   :outertype: SearchPanel.EntityList

lingListModel
^^^^^^^^^^^^^

.. java:field:: protected DefaultListModel lingListModel
   :outertype: SearchPanel.EntityList

pos
^^^

.. java:field:: protected HashMap<Object, Integer> pos
   :outertype: SearchPanel.EntityList

selected
^^^^^^^^

.. java:field:: protected Object selected
   :outertype: SearchPanel.EntityList

Constructors
------------
EntityList
^^^^^^^^^^

.. java:constructor::  EntityList(EntityLibrary library)
   :outertype: SearchPanel.EntityList

EntityList
^^^^^^^^^^

.. java:constructor::  EntityList(OWLOntology owlModel, EntityLibrary library, String entity)
   :outertype: SearchPanel.EntityList

EntityList
^^^^^^^^^^

.. java:constructor::  EntityList(Collection<? extends LinguisticMetaphor> c)
   :outertype: SearchPanel.EntityList

Methods
-------
setListener
^^^^^^^^^^^

.. java:method:: public void setListener()
   :outertype: SearchPanel.EntityList

