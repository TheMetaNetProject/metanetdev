.. java:import:: edu.berkeley.icsi.metanet.repository LexicalUnit

.. java:import:: edu.berkeley.icsi.metanet.repository LinguisticMetaphor

.. java:import:: edu.berkeley.icsi.metanet.repository MetaNetFactory

.. java:import:: edu.berkeley.icsi.metanet.repository Schema

.. java:import:: java.awt BorderLayout

.. java:import:: java.awt Color

.. java:import:: java.awt.event ActionEvent

.. java:import:: java.awt.event ActionListener

.. java:import:: java.awt.event AdjustmentEvent

.. java:import:: java.awt.event AdjustmentListener

.. java:import:: java.util ArrayList

.. java:import:: java.util Arrays

.. java:import:: java.util HashMap

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: java.util.concurrent ExecutionException

.. java:import:: java.util.logging Level

.. java:import:: java.util.logging Logger

.. java:import:: javax.swing BoxLayout

.. java:import:: javax.swing JButton

.. java:import:: javax.swing JLabel

.. java:import:: javax.swing JPanel

.. java:import:: javax.swing JScrollPane

.. java:import:: javax.swing JSplitPane

.. java:import:: javax.swing JTable

.. java:import:: javax.swing JTextArea

.. java:import:: javax.swing JTextField

.. java:import:: javax.swing RowFilter

.. java:import:: javax.swing ScrollPaneConstants

.. java:import:: javax.swing SwingWorker

.. java:import:: javax.swing.event DocumentEvent

.. java:import:: javax.swing.event DocumentListener

.. java:import:: javax.swing.table DefaultTableModel

.. java:import:: javax.swing.table TableColumn

.. java:import:: javax.swing.table TableRowSorter

.. java:import:: org.protege.editor.owl.model OWLModelManager

.. java:import:: org.protege.editor.owl.ui.view AbstractOWLViewComponent

.. java:import:: org.protege.owl.codegeneration.inference ReasonerBasedInference

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

Main
====

.. java:package:: edu.berkeley.icsi.metanet.lmtocmlinker
   :noindex:

.. java:type:: public class Main extends AbstractOWLViewComponent

   A tab plugin to Protege for assigning LMs automatically to CMs.

   :author: jhong

Methods
-------
disposeOWLView
^^^^^^^^^^^^^^

.. java:method:: @Override protected void disposeOWLView()
   :outertype: Main

initialiseOWLView
^^^^^^^^^^^^^^^^^

.. java:method:: public void initialiseOWLView() throws Exception
   :outertype: Main

   Initializes the tab

