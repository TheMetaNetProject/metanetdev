.. java:import:: java.util List

SparqlReasoner
==============

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery
   :noindex:

.. java:type:: public interface SparqlReasoner

Methods
-------
dispose
^^^^^^^

.. java:method::  void dispose()
   :outertype: SparqlReasoner

executeQuery
^^^^^^^^^^^^

.. java:method::  List<Object> executeQuery(String query) throws SparqlReasonerException
   :outertype: SparqlReasoner

getSampleQuery
^^^^^^^^^^^^^^

.. java:method::  String getSampleQuery()
   :outertype: SparqlReasoner

precalculate
^^^^^^^^^^^^

.. java:method::  void precalculate() throws SparqlReasonerException
   :outertype: SparqlReasoner

