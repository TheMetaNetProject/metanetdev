.. java:import:: java.awt Dimension

.. java:import:: java.awt.event MouseAdapter

.. java:import:: java.awt.event MouseEvent

.. java:import:: java.awt.event MouseWheelEvent

.. java:import:: java.awt.event MouseWheelListener

.. java:import:: javax.swing TransferHandler

.. java:import:: com.mxgraph.layout mxCompactTreeLayout

.. java:import:: com.mxgraph.model mxCell

.. java:import:: com.mxgraph.swing mxGraphComponent

.. java:import:: com.mxgraph.util mxRectangle

.. java:import:: com.mxgraph.view mxGraph

GraphComponent
==============

.. java:package:: edu.berkeley.icsi.metanet.metavisual
   :noindex:

.. java:type:: public class GraphComponent extends mxGraphComponent

Constructors
------------
GraphComponent
^^^^^^^^^^^^^^

.. java:constructor:: public GraphComponent(mxGraph graph)
   :outertype: GraphComponent

Methods
-------
addWheelZoom
^^^^^^^^^^^^

.. java:method:: public void addWheelZoom()
   :outertype: GraphComponent

createTransferHandler
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: @Override public TransferHandler createTransferHandler()
   :outertype: GraphComponent

mouseWheelZoom
^^^^^^^^^^^^^^

.. java:method:: protected void mouseWheelZoom(MouseWheelEvent e)
   :outertype: GraphComponent

reApplyLayout
^^^^^^^^^^^^^

.. java:method:: public void reApplyLayout(Object parent, Object root)
   :outertype: GraphComponent

zoomToFit
^^^^^^^^^

.. java:method:: public void zoomToFit()
   :outertype: GraphComponent

