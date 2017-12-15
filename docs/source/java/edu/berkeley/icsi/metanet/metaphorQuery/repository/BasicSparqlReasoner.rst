.. java:import:: java.util List

.. java:import:: java.util Map.Entry

.. java:import:: org.openrdf.query Query

.. java:import:: org.openrdf.query QueryEvaluationException

.. java:import:: org.openrdf.query QueryLanguage

.. java:import:: org.openrdf.query TupleQuery

.. java:import:: org.openrdf.query TupleQueryResultHandlerException

.. java:import:: org.openrdf.repository RepositoryConnection

.. java:import:: org.openrdf.repository RepositoryException

.. java:import:: org.protege.owl.rdf Utilities

.. java:import:: org.protege.owl.rdf.api OwlTripleStore

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.util NamespaceUtil

.. java:import:: edu.berkeley.icsi.metanet.metaphorQuery SparqlReasoner

.. java:import:: edu.berkeley.icsi.metanet.metaphorQuery SparqlReasonerException

.. java:import:: edu.berkeley.icsi.metanet.repository MetaNetFactory

BasicSparqlReasoner
===================

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery.repository
   :noindex:

.. java:type:: public class BasicSparqlReasoner implements SparqlReasoner

Constructors
------------
BasicSparqlReasoner
^^^^^^^^^^^^^^^^^^^

.. java:constructor:: public BasicSparqlReasoner(OWLOntologyManager manager, MetaNetFactory metaFactory)
   :outertype: BasicSparqlReasoner

Methods
-------
dispose
^^^^^^^

.. java:method:: @Override public void dispose()
   :outertype: BasicSparqlReasoner

executeQuery
^^^^^^^^^^^^

.. java:method:: @Override public List<Object> executeQuery(String queryString) throws SparqlReasonerException
   :outertype: BasicSparqlReasoner

getSampleQuery
^^^^^^^^^^^^^^

.. java:method:: @Override public String getSampleQuery()
   :outertype: BasicSparqlReasoner

precalculate
^^^^^^^^^^^^

.. java:method:: @Override public void precalculate() throws SparqlReasonerException
   :outertype: BasicSparqlReasoner

