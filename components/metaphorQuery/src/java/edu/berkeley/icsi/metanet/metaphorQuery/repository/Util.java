package edu.berkeley.icsi.metanet.metaphorQuery.repository;

import org.openrdf.model.BNode;
import org.openrdf.model.Value;
import org.openrdf.repository.RepositoryException;
import org.protege.owl.rdf.api.OwlTripleStore;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLClassExpression;

public class Util {
	private Util() {
		
	}

	public static Object convertValue(OwlTripleStore triples, Value v) throws RepositoryException {
		Object converted = v;
		if (v instanceof BNode) {
			OWLClassExpression ce = triples.parseClassExpression((BNode) v);
			if (ce != null) {
				converted = ce;
			}
		}
		else if (v instanceof org.openrdf.model.URI) {
			converted = IRI.create(((org.openrdf.model.URI) v).stringValue());
		}
		return converted;
	}
	
	public static String formatName(String name) {
		String[] arr = name.split("_");
		StringBuffer str = new StringBuffer();
		for (int i = 1; i < arr.length; i++) {
			str.append(arr[i]);
			str.append(" ");
		}
		return str.substring(0, str.length() - 1);
	}
	
	public static String formatNameDash(String name) {
		String[] arr = name.split("_");
		StringBuffer str = new StringBuffer();
		for (int i = 1; i < arr.length; i++) {
			str.append(arr[i]);
			str.append("_");
		}
		return str.substring(0, str.length() - 1);
	} 
	
	public static String getName(OwlTripleStore triples, Value v) throws RepositoryException {
		String converted = v.stringValue();
		if (v instanceof BNode) {
			OWLClassExpression ce = triples.parseClassExpression((BNode) v);
			if (ce != null) {
				converted = ce.getClass().getName();
			}
		}
		else if (v instanceof org.openrdf.model.URI) {
			converted = IRI.create(((org.openrdf.model.URI) v).stringValue()).getFragment();
		}
		return converted;
	}
	
	
}
