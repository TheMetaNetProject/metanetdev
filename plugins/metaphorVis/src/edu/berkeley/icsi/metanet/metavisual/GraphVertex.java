package edu.berkeley.icsi.metanet.metavisual;

import org.semanticweb.owlapi.model.OWLNamedIndividual;

import com.mxgraph.model.mxCell;

public class GraphVertex {
	
	private GraphVertexItem vertex;
	private mxCell cell;
	
	public GraphVertex(Object obj) {
		cell = (mxCell) obj;
		vertex = (GraphVertexItem) cell.getValue();
	}
	
	public GraphVertexItem getOWLVertex() {
		return vertex;
	}
	
	public mxCell getCell() {
		return cell;
	}
	
	public OWLNamedIndividual getIndie() {
		return vertex.getIndividual();
	}
	
}
