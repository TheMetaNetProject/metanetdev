package edu.berkeley.icsi.metanet.metaphorQuery;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map.Entry;

import org.protege.editor.core.ProtegeApplication;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.util.NamespaceUtil;

import edu.berkeley.icsi.metanet.metaphorQuery.repository.BasicSparqlReasonerFactory;
import edu.berkeley.icsi.metanet.repository.MetaNetFactory;
import edu.berkeley.icsi.metanet.repository.Metaphor;
import edu.berkeley.icsi.metanet.repository.Schema;

public class MetaNetQuery implements MetaNetInterface {
	private SparqlReasoner reasoner;
	private StringBuffer queryHeader;
	private MetaNetFactory factory;
	private OWLOntologyManager manager;
//	private OWLOntology owlModel;
	private HashMap<String, Schema> schemas;
	private HashMap<String, Metaphor> metaphors;
	
	public MetaNetQuery(OWLOntologyManager manager, MetaNetFactory factory) {
		this.manager = manager;
		this.factory = factory;
//		IRI iri = IRI.create("https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl");
//		owlModel = manager.getOntology(iri);
		schemas = new HashMap<String, Schema>();
		metaphors = new HashMap<String, Metaphor>();
		for (Schema sch : factory.getAllSchemaInstances()) {
//			System.out.println(sch.getOwlIndividual().getIRI());
			schemas.put(sch.getOwlIndividual().getIRI().toString(), sch);
		}
		for (Metaphor metaphor : factory.getAllMetaphorInstances()) {
			metaphors.put(metaphor.getOwlIndividual().getIRI().toString(), metaphor);
		}
		initializeQueryHeader();
		initializeReasoner();
	}
	
	private void initializeQueryHeader() {
		queryHeader = new StringBuffer();
		NamespaceUtil nsUtil = new NamespaceUtil();
		for (Entry<String, String> entry : nsUtil.getNamespace2PrefixMap().entrySet()) {
			String ns = entry.getKey();
			String prefix = entry.getValue();
			queryHeader.append("PREFIX ");
			queryHeader.append(prefix);
			queryHeader.append(": <");
			queryHeader.append(ns);
			queryHeader.append(">\n");
		}
		queryHeader.append("PREFIX m: <https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#>\n\n\n");
	}
	
	private void initializeReasoner() {
		try {
			List<SparqlInferenceFactory> plugins = Collections
					.singletonList((SparqlInferenceFactory) new BasicSparqlReasonerFactory());
			reasoner = plugins
					.iterator()
					.next()
					.createReasoner(manager, factory);
			reasoner.precalculate();
		} catch (SparqlReasonerException e) {
			ProtegeApplication.getErrorLog().logError(e);
		}
	}
	
	@Override
	public List<Object> runGeneralQuery(String query) {
		StringBuffer completeQuery = queryHeader;
		completeQuery.append(query);
		List<Object> result = new ArrayList<Object>();
		try {
			result = reasoner.executeQuery(query.toString());
		} catch (SparqlReasonerException ex) {
			ProtegeApplication.getErrorLog().logError(ex);
		}
		
		return result;
	}

	@Override
	public Collection<? extends Schema> getSchemasRelatedToBy(
			String schemaName, String propertyName) {
		StringBuffer query = queryHeader;
		query.append("SELECT ?ss\n\t" +
						"WHERE { ?s m:hasName '"+schemaName+"'^^xsd:string .\n\t\t" +
							"?s m:"+propertyName+" ?ss }");
//		System.out.println(query.toString());
		List<Object> result = new ArrayList<Object>();
		List<Schema> schemas = new ArrayList<Schema>();
		try {
			result = reasoner.executeQuery(query.toString());
			for (Object res : result) {
				schemas.add(this.schemas.get(res.toString()));
				System.out.println(res.toString());
			}
		} catch (SparqlReasonerException ex) {
			ProtegeApplication.getErrorLog().logError(ex);
		}
		return Collections.unmodifiableList(schemas);
	}

	@Override
	public Collection<? extends Schema> getAllSchemasRelatedToBy(
			String schemaName, String propertyName) {
		StringBuffer query = queryHeader;
		query.append("SELECT ?ss\n\t" +
						"WHERE { ?s m:hasName '"+schemaName+"'^^xsd:string .\n\t\t" +
							"?s m:"+propertyName+"*/m:"+propertyName+" ?ss }");
//		System.out.println(query.toString());
		List<Object> result = new ArrayList<Object>();
		List<Schema> schemas = new ArrayList<Schema>();
		try {
			result = reasoner.executeQuery(query.toString());
			for (Object res : result) {
				schemas.add(this.schemas.get(res.toString()));
			}
		} catch (SparqlReasonerException ex) {
			ProtegeApplication.getErrorLog().logError(ex);
		}
		return Collections.unmodifiableList(schemas);
	}

	public Collection<? extends Metaphor> getMetaphorsRelatedToBy(
			String metaphorName, String propertyName) {
		StringBuffer query = queryHeader;
		query.append("SELECT ?ss\n\t" +
						"WHERE { ?s m:hasName '"+metaphorName+"'^^xsd:string .\n\t\t" +
							"?s m:"+propertyName+"*/m:"+propertyName+" ?ss }");
//		System.out.println(query.toString());
		List<Object> result = new ArrayList<Object>();
		List<Metaphor> metaphors = new ArrayList<Metaphor>();
		try {
			result = reasoner.executeQuery(query.toString());
			for (Object res : result) {
				metaphors.add(this.metaphors.get(res.toString()));
			}
		} catch (SparqlReasonerException ex) {
			ProtegeApplication.getErrorLog().logError(ex);
		}
		return Collections.unmodifiableList(metaphors);
	}

	@Override
	public Collection<? extends Metaphor> getAllMetaphorsRelatedToBy(
			String metaphorName, String propertyName) {
		StringBuffer query = queryHeader;
		query.append("SELECT ?ss\n\t" +
						"WHERE { ?s m:hasName '"+metaphorName+"'^^xsd:string .\n\t\t" +
							"?s m:"+propertyName+"*/m:"+propertyName+" ?ss }");
//		System.out.println(query.toString());
		List<Object> result = new ArrayList<Object>();
		List<Metaphor> metaphors = new ArrayList<Metaphor>();
		try {
			result = reasoner.executeQuery(query.toString());
			for (Object res : result) {
				metaphors.add(this.metaphors.get(res.toString()));
			}
		} catch (SparqlReasonerException ex) {
			ProtegeApplication.getErrorLog().logError(ex);
		}
		return Collections.unmodifiableList(metaphors);
	}
	
	

}
