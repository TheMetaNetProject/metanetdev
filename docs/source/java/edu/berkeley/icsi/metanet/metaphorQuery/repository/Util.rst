.. java:import:: org.openrdf.model BNode

.. java:import:: org.openrdf.model Value

.. java:import:: org.openrdf.repository RepositoryException

.. java:import:: org.protege.owl.rdf.api OwlTripleStore

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLClassExpression

Util
====

.. java:package:: edu.berkeley.icsi.metanet.metaphorQuery.repository
   :noindex:

.. java:type:: public class Util

Methods
-------
convertValue
^^^^^^^^^^^^

.. java:method:: public static Object convertValue(OwlTripleStore triples, Value v) throws RepositoryException
   :outertype: Util

formatName
^^^^^^^^^^

.. java:method:: public static String formatName(String name)
   :outertype: Util

formatNameDash
^^^^^^^^^^^^^^

.. java:method:: public static String formatNameDash(String name)
   :outertype: Util

getName
^^^^^^^

.. java:method:: public static String getName(OwlTripleStore triples, Value v) throws RepositoryException
   :outertype: Util

