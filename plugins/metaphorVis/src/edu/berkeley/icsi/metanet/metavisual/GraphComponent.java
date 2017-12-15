package edu.berkeley.icsi.metanet.metavisual;

import java.awt.Dimension;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseWheelEvent;
import java.awt.event.MouseWheelListener;

import javax.swing.TransferHandler;

import com.mxgraph.layout.mxCompactTreeLayout;
import com.mxgraph.model.mxCell;
import com.mxgraph.swing.mxGraphComponent;
import com.mxgraph.util.mxRectangle;
import com.mxgraph.view.mxGraph;

public class GraphComponent extends mxGraphComponent {
	private static final long serialVersionUID = -4744043037735459482L;
	private mxCompactTreeLayout treeLayout;

	public GraphComponent(mxGraph graph) {
		super(graph);
		// Apply initial tree layout to graph
		treeLayout = new mxCompactTreeLayout(graph, false);
		treeLayout.setEdgeRouting(false);
		treeLayout.setUseBoundingBox(false);
		treeLayout.execute(graph.getDefaultParent());
		
		// Add features to component & set properties
		setProperties();
		addWheelZoom();
		zoomToFit();
		addMouseHandler();
	}

	@Override
	public TransferHandler createTransferHandler() {
		return this.getTransferHandler();
	}
	
	public void reApplyLayout(Object parent, Object root) {
		treeLayout.execute(parent, root);
	}
	
	private void addMouseHandler() {
		getGraphControl().addMouseListener(new MouseAdapter() {
			@Override
			public void mousePressed(MouseEvent e) {
				if (e.getButton() == MouseEvent.BUTTON3) {
					Object obj = getCellAt(e.getX(), e.getY());
					if (obj != null) {
						mxCell cell = (mxCell) obj;
						if (cell.isVertex()) {
							//System.out.println("cell=" + graph.getLabel(obj));
							GraphVertexItem ind = (GraphVertexItem) cell.getValue();
							GraphModel graphModel = (GraphModel) graph;
							if (!ind.getExpandState() && ind.getCount() > 0) {
								if (ind.getType().equals("Metaphor")) {
									graphModel.expandMetaphorOutgoing(ind.getIndividual(), obj);
									graphModel.expandMetaphorIncoming(ind.getIndividual(), obj);
									mxRectangle oldRect = graphModel.getView().getState(obj).getBoundingBox();
									reApplyLayout(graph.getDefaultParent(), obj);
									treeLayout.setVertexLocation(obj, oldRect.getCenterX(), oldRect.getCenterY());
								} else if (ind.getType().equals("Schema")) {
									graphModel.expandSchemaOutgoing(obj, false);
									graphModel.expandSchemaIncoming(obj, true);
									reApplyLayout(graph.getDefaultParent(), obj);
								}
							} else if (ind.getExpandState()) {
								if (ind.getType().equals("Metaphor")) {
									graphModel.collapseVertex(obj, true);
								} else if (ind.getType().equals("Schema")) {
									Object[] removeMe = new Object[1];
									for (Object c : graphModel.getChildVertices(obj)) {
										mxCell role = (mxCell) c;
										for (Object e2 : graphModel.getOutgoingEdges(role)) {
											removeMe[0] = e2;
											graphModel.removeCells(removeMe);
										}
									}
									graphModel.collapseSchema(obj, true);
								}
							}
						}
					}
				}
			}
		});
	}
	
	public void zoomToFit() {
        double newScale = 1;

        Dimension graphSize = getGraphControl().getSize();
        Dimension viewPortSize = getViewport().getSize();

        int gw = (int) graphSize.getWidth();
        int gh = (int) graphSize.getHeight();

        if (gw > 0 && gh > 0) {
            int w = (int) viewPortSize.getWidth();
            int h = (int) viewPortSize.getHeight();

            newScale = Math.min((double) w / gw, (double) h / gh);
        }

        zoom(newScale);
	}
	
	public void addWheelZoom() {
		 MouseWheelListener wheelTracker = new MouseWheelListener() {
			 public void mouseWheelMoved(MouseWheelEvent e) {
				 if (e.isControlDown()) {
					 mouseWheelZoom(e);
				 }
			 }
		 };
		 addMouseWheelListener(wheelTracker);
	}
	
	private void setProperties() {
		setPanning(true);
		setConnectable(false);
		zoomOut();
		getGraphHandler().setLivePreview(true);
	}
	
	 protected void mouseWheelZoom(MouseWheelEvent e) {
		 if (e.getWheelRotation() < 0) {
			 zoomIn();
		 } else {
			 zoomOut();
		 }
		 
//		 System.out.println(mxResources.get("scale") + ": "
//		 + (int) (100 * getGraph().getView().getScale())
//		 + "%");
	 }   
}
