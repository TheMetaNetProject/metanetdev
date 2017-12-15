.. java:import:: java.util ArrayList

.. java:import:: java.util List

.. java:import:: org.openrdf.model Statement

.. java:import:: org.openrdf.repository RepositoryException

.. java:import:: org.openrdf.rio RDFHandler

.. java:import:: org.openrdf.rio RDFHandlerException

.. java:import:: org.protege.owl.rdf.api OwlTripleStore

.. java:import:: edu.berkeley.icsi.metanet.metaphorQuery SparqlResultSet

GraphQueryHandler
=================

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery.repository
   :noindex:

.. java:type:: public class GraphQueryHandler implements RDFHandler

Constructors
------------
GraphQueryHandler
^^^^^^^^^^^^^^^^^

.. java:constructor:: public GraphQueryHandler(OwlTripleStore triples)
   :outertype: GraphQueryHandler

Methods
-------
endRDF
^^^^^^

.. java:method:: @Override public void endRDF() throws RDFHandlerException
   :outertype: GraphQueryHandler

getQueryResult
^^^^^^^^^^^^^^

.. java:method:: public SparqlResultSet getQueryResult()
   :outertype: GraphQueryHandler

handleComment
^^^^^^^^^^^^^

.. java:method:: @Override public void handleComment(String arg0) throws RDFHandlerException
   :outertype: GraphQueryHandler

handleNamespace
^^^^^^^^^^^^^^^

.. java:method:: @Override public void handleNamespace(String arg0, String arg1) throws RDFHandlerException
   :outertype: GraphQueryHandler

handleStatement
^^^^^^^^^^^^^^^

.. java:method:: @Override public void handleStatement(Statement stmt) throws RDFHandlerException
   :outertype: GraphQueryHandler

startRDF
^^^^^^^^

.. java:method:: @Override public void startRDF() throws RDFHandlerException
   :outertype: GraphQueryHandler

