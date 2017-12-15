.. java:import:: java.util ArrayList

.. java:import:: java.util List

.. java:import:: org.openrdf.model Value

.. java:import:: org.openrdf.query Binding

.. java:import:: org.openrdf.query BindingSet

.. java:import:: org.openrdf.query TupleQueryResultHandler

.. java:import:: org.openrdf.query TupleQueryResultHandlerException

.. java:import:: org.openrdf.repository RepositoryException

.. java:import:: org.protege.owl.rdf.api OwlTripleStore

.. java:import:: edu.berkeley.icsi.metanet.metaphorQuery SparqlResultSet

.. java:import:: edu.berkeley.icsi.metanet.repository MetaNetFactory

TupleQueryHandler
=================

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery.repository
   :noindex:

.. java:type:: public class TupleQueryHandler implements TupleQueryResultHandler

Constructors
------------
TupleQueryHandler
^^^^^^^^^^^^^^^^^

.. java:constructor:: public TupleQueryHandler(OwlTripleStore triples, MetaNetFactory metaFactory)
   :outertype: TupleQueryHandler

Methods
-------
endQueryResult
^^^^^^^^^^^^^^

.. java:method:: @Override public void endQueryResult() throws TupleQueryResultHandlerException
   :outertype: TupleQueryHandler

getQueryResult
^^^^^^^^^^^^^^

.. java:method:: public List<Object> getQueryResult()
   :outertype: TupleQueryHandler

handleSolution
^^^^^^^^^^^^^^

.. java:method:: @Override public void handleSolution(BindingSet bindingSet) throws TupleQueryResultHandlerException
   :outertype: TupleQueryHandler

startQueryResult
^^^^^^^^^^^^^^^^

.. java:method:: @Override public void startQueryResult(List<String> bindingNames) throws TupleQueryResultHandlerException
   :outertype: TupleQueryHandler

