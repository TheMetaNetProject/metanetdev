package edu.berkeley.icsi.metanet.metavisual;

import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;

public class OptionsListItem {

	private String displayName;
	private OWLNamedIndividual individual;
	private OWLObjectProperty property;
	
	public OptionsListItem(String displayName, OWLObjectProperty property) {
		this.displayName = displayName;
		this.property = property;
		individual = null;
	}
	
	public OptionsListItem(String displayName, OWLNamedIndividual individual) {
		this.displayName = displayName;
		this.individual = individual;
		property = null;
	}
	
	public OWLNamedIndividual individual() {
		return individual;
	}
	
	public OWLObjectProperty property() {
		return property;
	}
	
	public String toString() {
		return displayName;
	}
	
}
