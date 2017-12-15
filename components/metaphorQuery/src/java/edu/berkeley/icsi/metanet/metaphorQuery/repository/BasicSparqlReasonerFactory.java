package edu.berkeley.icsi.metanet.metaphorQuery.repository;



import org.semanticweb.owlapi.model.OWLOntologyManager;

import edu.berkeley.icsi.metanet.metaphorQuery.SparqlInferenceFactory;
import edu.berkeley.icsi.metanet.metaphorQuery.SparqlReasoner;
import edu.berkeley.icsi.metanet.repository.MetaNetFactory;



public class BasicSparqlReasonerFactory implements SparqlInferenceFactory {

	@Override
	public SparqlReasoner createReasoner(OWLOntologyManager manager, MetaNetFactory metaFactory) {
		return (SparqlReasoner) new BasicSparqlReasoner(manager, metaFactory);
	}

}
