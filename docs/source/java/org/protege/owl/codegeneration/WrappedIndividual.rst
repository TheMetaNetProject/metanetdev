.. java:import:: org.semanticweb.owlapi.model OWLClassExpression

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLOntology

WrappedIndividual
=================

.. java:package:: org.protege.owl.codegeneration
   :noindex:

.. java:type:: public interface WrappedIndividual extends Comparable<WrappedIndividual>

   :author: z.khan

Methods
-------
assertOwlType
^^^^^^^^^^^^^

.. java:method::  void assertOwlType(OWLClassExpression type)
   :outertype: WrappedIndividual

getOwlIndividual
^^^^^^^^^^^^^^^^

.. java:method::  OWLNamedIndividual getOwlIndividual()
   :outertype: WrappedIndividual

getOwlOntology
^^^^^^^^^^^^^^

.. java:method::  OWLOntology getOwlOntology()
   :outertype: WrappedIndividual

