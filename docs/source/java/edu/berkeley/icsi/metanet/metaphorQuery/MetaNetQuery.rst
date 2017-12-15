.. java:import:: java.util ArrayList

.. java:import:: java.util Collection

.. java:import:: java.util Collections

.. java:import:: java.util HashMap

.. java:import:: java.util List

.. java:import:: java.util Map.Entry

.. java:import:: org.protege.editor.core ProtegeApplication

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.util NamespaceUtil

.. java:import:: edu.berkeley.icsi.metanet.metaphorQuery.repository BasicSparqlReasonerFactory

.. java:import:: edu.berkeley.icsi.metanet.repository MetaNetFactory

.. java:import:: edu.berkeley.icsi.metanet.repository Metaphor

.. java:import:: edu.berkeley.icsi.metanet.repository Schema

MetaNetQuery
============

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery
   :noindex:

.. java:type:: public class MetaNetQuery implements MetaNetInterface

Constructors
------------
MetaNetQuery
^^^^^^^^^^^^

.. java:constructor:: public MetaNetQuery(OWLOntologyManager manager, MetaNetFactory factory)
   :outertype: MetaNetQuery

Methods
-------
getAllMetaphorsRelatedToBy
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: @Override public Collection<? extends Metaphor> getAllMetaphorsRelatedToBy(String metaphorName, String propertyName)
   :outertype: MetaNetQuery

getAllSchemasRelatedToBy
^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: @Override public Collection<? extends Schema> getAllSchemasRelatedToBy(String schemaName, String propertyName)
   :outertype: MetaNetQuery

getMetaphorsRelatedToBy
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public Collection<? extends Metaphor> getMetaphorsRelatedToBy(String metaphorName, String propertyName)
   :outertype: MetaNetQuery

getSchemasRelatedToBy
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: @Override public Collection<? extends Schema> getSchemasRelatedToBy(String schemaName, String propertyName)
   :outertype: MetaNetQuery

runGeneralQuery
^^^^^^^^^^^^^^^

.. java:method:: @Override public List<Object> runGeneralQuery(String query)
   :outertype: MetaNetQuery

