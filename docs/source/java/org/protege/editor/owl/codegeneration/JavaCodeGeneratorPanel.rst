.. java:import:: java.awt BorderLayout

.. java:import:: java.awt Component

.. java:import:: java.awt Dimension

.. java:import:: java.awt FlowLayout

.. java:import:: java.awt.event ActionEvent

.. java:import:: java.awt.event MouseAdapter

.. java:import:: java.awt.event MouseEvent

.. java:import:: java.io File

.. java:import:: java.net URL

.. java:import:: javax.swing AbstractAction

.. java:import:: javax.swing BorderFactory

.. java:import:: javax.swing Box

.. java:import:: javax.swing BoxLayout

.. java:import:: javax.swing ImageIcon

.. java:import:: javax.swing JButton

.. java:import:: javax.swing JCheckBox

.. java:import:: javax.swing JComponent

.. java:import:: javax.swing JFileChooser

.. java:import:: javax.swing JLabel

.. java:import:: javax.swing JOptionPane

.. java:import:: javax.swing JPanel

.. java:import:: javax.swing JTextField

.. java:import:: javax.swing.border Border

.. java:import:: org.protege.editor.owl.model.inference NoOpReasoner

.. java:import:: org.protege.owl.codegeneration CodeGenerationOptions

.. java:import:: org.protege.owl.codegeneration Constants

JavaCodeGeneratorPanel
======================

.. java:package:: org.protege.editor.owl.codegeneration
   :noindex:

.. java:type:: public class JavaCodeGeneratorPanel extends JPanel

   This class creates a panel, which contains options for code generations.

   :author: z.khan

Constructors
------------
JavaCodeGeneratorPanel
^^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public JavaCodeGeneratorPanel(CodeGenerationOptions options, GenerateCodeCallback generateCodeWithOptions)
   :outertype: JavaCodeGeneratorPanel

   Constructor

   :param options: the EditableJavaCodeGeneratorOptions object in which to save the option values.
   :param generateCodeWithOptions:

Methods
-------
ok
^^

.. java:method:: public void ok()
   :outertype: JavaCodeGeneratorPanel

