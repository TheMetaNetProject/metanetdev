.. java:import:: java.util List

.. java:import:: java.util Set

.. java:import:: java.util TreeSet

.. java:import:: org.protege.owl.codegeneration CodeGenerationFactory

.. java:import:: org.protege.owl.codegeneration WrappedIndividual

.. java:import:: org.protege.owl.codegeneration.impl WrappedIndividualImpl

.. java:import:: org.protege.owl.codegeneration.inference CodeGenerationInference

.. java:import:: org.semanticweb.owlapi.model AddAxiom

.. java:import:: org.semanticweb.owlapi.model OWLAxiom

.. java:import:: org.semanticweb.owlapi.model OWLAxiomChange

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLEntity

.. java:import:: org.semanticweb.owlapi.model OWLException

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntologyChange

.. java:import:: org.semanticweb.owlapi.model OWLOntologyChangeListener

.. java:import:: org.semanticweb.owlapi.model OWLPropertyAssertionAxiom

CodeGenerationListener
======================

.. java:package:: org.protege.owl.codegeneration.listener
   :noindex:

.. java:type:: public abstract class CodeGenerationListener<X extends WrappedIndividual> implements OWLOntologyChangeListener

Constructors
------------
CodeGenerationListener
^^^^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public CodeGenerationListener(CodeGenerationFactory factory, Class<? extends X> javaInterface)
   :outertype: CodeGenerationListener

Methods
-------
individualCreated
^^^^^^^^^^^^^^^^^

.. java:method:: public abstract void individualCreated(X individual)
   :outertype: CodeGenerationListener

individualModified
^^^^^^^^^^^^^^^^^^

.. java:method:: public abstract void individualModified(X individual)
   :outertype: CodeGenerationListener

ontologiesChanged
^^^^^^^^^^^^^^^^^

.. java:method:: @Override public void ontologiesChanged(List<? extends OWLOntologyChange> changes) throws OWLException
   :outertype: CodeGenerationListener

