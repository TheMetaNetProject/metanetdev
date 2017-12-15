package edu.berkeley.icsi.metanet.metaphorQuery;

import org.semanticweb.owlapi.model.OWLOntologyManager;

import edu.berkeley.icsi.metanet.repository.MetaNetFactory;

public interface SparqlInferenceFactory {

	public SparqlReasoner createReasoner(OWLOntologyManager manager, MetaNetFactory metaFactory);

}
