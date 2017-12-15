package edu.berkeley.icsi.metanet.metavisual;

import org.semanticweb.owlapi.model.OWLObjectProperty;

public class GraphEdgeItem {
	private OWLObjectProperty prop;
	
	public GraphEdgeItem(OWLObjectProperty prop) {
		this.prop = prop;
	}
	
	public String toString() {
		return prop.getIRI().getFragment();
	}
}
