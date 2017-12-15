.. java:import:: java.awt BorderLayout

.. java:import:: java.awt Frame

.. java:import:: java.awt GridLayout

.. java:import:: java.awt.event WindowEvent

.. java:import:: java.awt.event WindowListener

.. java:import:: java.awt.event WindowStateListener

.. java:import:: java.beans PropertyChangeEvent

.. java:import:: java.beans PropertyChangeListener

.. java:import:: java.io IOException

.. java:import:: java.net MalformedURLException

.. java:import:: java.net URISyntaxException

.. java:import:: java.net URL

.. java:import:: java.util Collections

.. java:import:: java.util.logging Level

.. java:import:: java.util.logging Logger

.. java:import:: javax.swing JDialog

.. java:import:: javax.swing JFrame

.. java:import:: javax.swing JLabel

.. java:import:: org.protege.editor.owl.model OWLModelManager

.. java:import:: org.semanticweb.owlapi.io RDFXMLOntologyFormat

.. java:import:: org.semanticweb.owlapi.model AddImport

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyCreationException

.. java:import:: org.semanticweb.owlapi.model OWLOntologyFormat

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.util DefaultPrefixManager

.. java:import:: org.semanticweb.owlapi.util OWLEntityRemover

.. java:import:: javax.swing JOptionPane

.. java:import:: javax.swing JPanel

.. java:import:: javax.swing JPasswordField

.. java:import:: javax.swing JProgressBar

.. java:import:: javax.swing JTextField

.. java:import:: javax.swing SwingUtilities

.. java:import:: javax.swing SwingWorker

.. java:import:: org.protege.editor.owl.model OWLWorkspace

.. java:import:: org.semanticweb.owlapi.util SimpleIRIMapper

WikiLoader
==========

.. java:package:: edu.berkeley.icsi.metanet.wiki2owl
   :noindex:

.. java:type:: public class WikiLoader implements PropertyChangeListener, WindowListener

Fields
------
EN
^^

.. java:field:: public static final String EN
   :outertype: WikiLoader

ES
^^

.. java:field:: public static final String ES
   :outertype: WikiLoader

FA
^^

.. java:field:: public static final String FA
   :outertype: WikiLoader

RU
^^

.. java:field:: public static final String RU
   :outertype: WikiLoader

TEST
^^^^

.. java:field:: public static final String TEST
   :outertype: WikiLoader

Constructors
------------
WikiLoader
^^^^^^^^^^

.. java:constructor:: public WikiLoader(OWLWorkspace w)
   :outertype: WikiLoader

Methods
-------
load
^^^^

.. java:method:: public void load(String lang) throws IOException
   :outertype: WikiLoader

propertyChange
^^^^^^^^^^^^^^

.. java:method:: @Override public void propertyChange(PropertyChangeEvent evt)
   :outertype: WikiLoader

setProgressMessage
^^^^^^^^^^^^^^^^^^

.. java:method:: public void setProgressMessage(String msg)
   :outertype: WikiLoader

windowActivated
^^^^^^^^^^^^^^^

.. java:method:: @Override public void windowActivated(WindowEvent e)
   :outertype: WikiLoader

windowClosed
^^^^^^^^^^^^

.. java:method:: @Override public void windowClosed(WindowEvent e)
   :outertype: WikiLoader

windowClosing
^^^^^^^^^^^^^

.. java:method:: @Override public void windowClosing(WindowEvent e)
   :outertype: WikiLoader

windowDeactivated
^^^^^^^^^^^^^^^^^

.. java:method:: @Override public void windowDeactivated(WindowEvent e)
   :outertype: WikiLoader

windowDeiconified
^^^^^^^^^^^^^^^^^

.. java:method:: @Override public void windowDeiconified(WindowEvent e)
   :outertype: WikiLoader

windowIconified
^^^^^^^^^^^^^^^

.. java:method:: @Override public void windowIconified(WindowEvent e)
   :outertype: WikiLoader

windowOpened
^^^^^^^^^^^^

.. java:method:: @Override public void windowOpened(WindowEvent e)
   :outertype: WikiLoader

