.. java:import:: java.util ArrayList

.. java:import:: java.util HashMap

.. java:import:: java.util HashSet

.. java:import:: java.util Map

.. java:import:: java.util Set

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLIndividual

.. java:import:: org.semanticweb.owlapi.model OWLLiteral

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: com.mxgraph.model mxCell

.. java:import:: com.mxgraph.model mxGeometry

.. java:import:: com.mxgraph.util mxRectangle

.. java:import:: com.mxgraph.view mxCellState

.. java:import:: com.mxgraph.view mxGraph

.. java:import:: com.mxgraph.view mxStylesheet

GraphModel
==========

.. java:package:: edu.berkeley.icsi.metanet.metavisual
   :noindex:

.. java:type:: public class GraphModel extends mxGraph

Fields
------
metaphorRelations
^^^^^^^^^^^^^^^^^

.. java:field:: protected Set<OWLObjectProperty> metaphorRelations
   :outertype: GraphModel

schemaBindingEdges
^^^^^^^^^^^^^^^^^^

.. java:field:: protected Set<Object> schemaBindingEdges
   :outertype: GraphModel

schemaBindingVertices
^^^^^^^^^^^^^^^^^^^^^

.. java:field:: protected Set<Object> schemaBindingVertices
   :outertype: GraphModel

schemaRelations
^^^^^^^^^^^^^^^

.. java:field:: protected Set<OWLObjectProperty> schemaRelations
   :outertype: GraphModel

schemaToRoles
^^^^^^^^^^^^^

.. java:field:: protected HashMap<Object, Object> schemaToRoles
   :outertype: GraphModel

Constructors
------------
GraphModel
^^^^^^^^^^

.. java:constructor:: public GraphModel()
   :outertype: GraphModel

GraphModel
^^^^^^^^^^

.. java:constructor:: public GraphModel(OWLOntology owlModel, EntityLibrary library, OWLNamedIndividual individual, Object metaphorRelations, Object schemaRelations, boolean expandAll, boolean schema)
   :outertype: GraphModel

Methods
-------
collapseSchema
^^^^^^^^^^^^^^

.. java:method:: public void collapseSchema(Object origin, boolean isRoot)
   :outertype: GraphModel

collapseVertex
^^^^^^^^^^^^^^

.. java:method:: public void collapseVertex(Object origin, boolean isRoot)
   :outertype: GraphModel

edgeInserterWithInverse
^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void edgeInserterWithInverse(Object subject, Object object, OWLObjectProperty property, Set<OWLObjectProperty> relations)
   :outertype: GraphModel

expandMetaphorIncoming
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void expandMetaphorIncoming(OWLNamedIndividual currentMetaphor, Object source)
   :outertype: GraphModel

expandMetaphorOutgoing
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void expandMetaphorOutgoing(OWLNamedIndividual currentMetaphor, Object subject)
   :outertype: GraphModel

expandSchemaIncoming
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void expandSchemaIncoming(Object source, boolean secondPass)
   :outertype: GraphModel

expandSchemaOutgoing
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void expandSchemaOutgoing(Object source, boolean secondPass)
   :outertype: GraphModel

isCellSelectable
^^^^^^^^^^^^^^^^

.. java:method:: @Override public boolean isCellSelectable(Object cell)
   :outertype: GraphModel

moveEdgeToBack
^^^^^^^^^^^^^^

.. java:method:: public void moveEdgeToBack(Object edge)
   :outertype: GraphModel

moveEdgeToFront
^^^^^^^^^^^^^^^

.. java:method:: public void moveEdgeToFront(Object edge)
   :outertype: GraphModel

redrawVertexBox
^^^^^^^^^^^^^^^

.. java:method:: public void redrawVertexBox(Object obj)
   :outertype: GraphModel

   HELPER FUNCTIONS AND SOME OVERRIDES FOR AESTHETICS *

roleBindings
^^^^^^^^^^^^

.. java:method:: public void roleBindings(Object sourceRoles, Object targetRoles, OWLNamedIndividual sourceSchema)
   :outertype: GraphModel

