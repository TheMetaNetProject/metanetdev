package edu.berkeley.icsi.metanet.metavisual;

import org.semanticweb.owlapi.model.OWLNamedIndividual;

public class GraphVertexItem {
	final private OWLNamedIndividual ind; // immutable, should not be able to change individual
	private boolean expanded;
	private int childCount;
	private String type = null;
	private String name = null;
	
	public GraphVertexItem(OWLNamedIndividual ind) {
		this.ind = ind;
		this.expanded = false;
		this.childCount = 0;
	}
	
	public GraphVertexItem(OWLNamedIndividual ind, String name, String type) {
		this.ind = ind;
		this.expanded = false;
		this.childCount = 0;
		this.name = name;
		this.type = type;
	}
	
	public String getType() {
		return type;
	}
	
	public OWLNamedIndividual getIndividual() {
		return ind;
	}
	
	public boolean getExpandState() {
		return expanded;
	}
	
	public void setExpandState(boolean state) {
		this.expanded = state;
	}
	
	public int getCount() {
		return this.childCount;
	}
	
	public void increaseCount() {
		this.childCount++;
	}
	
	public String toString() {
		String[] arr = name.split(" ");
		String returnMe = "";
		for (int n = 0; n < arr.length; n++) {
			if ((n % 3) == 0 && n > 0) {
				returnMe = returnMe + arr[n] + "<br/>";
			} else {
				returnMe = returnMe + arr[n] + " ";
			}
		}
		returnMe = returnMe + " (" + this.childCount + ")";
		return returnMe;
	}
	
}
