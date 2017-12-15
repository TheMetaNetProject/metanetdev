package edu.berkeley.icsi.metanet.metaphorQuery.repository;

import java.util.List;
import java.util.Map.Entry;

import org.openrdf.query.Query;
import org.openrdf.query.QueryEvaluationException;
import org.openrdf.query.QueryLanguage;
import org.openrdf.query.TupleQuery;
import org.openrdf.query.TupleQueryResultHandlerException;
import org.openrdf.repository.RepositoryConnection;
import org.openrdf.repository.RepositoryException;
import org.protege.owl.rdf.Utilities;
import org.protege.owl.rdf.api.OwlTripleStore;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.util.NamespaceUtil;

import edu.berkeley.icsi.metanet.metaphorQuery.SparqlReasoner;
import edu.berkeley.icsi.metanet.metaphorQuery.SparqlReasonerException;
import edu.berkeley.icsi.metanet.repository.MetaNetFactory;



public class BasicSparqlReasoner implements SparqlReasoner {
	private OWLOntologyManager manager;
	private OwlTripleStore triples;
	private MetaNetFactory metaFactory;
	
	public BasicSparqlReasoner(OWLOntologyManager manager, MetaNetFactory metaFactory) {
		this.metaFactory = metaFactory;
		this.manager = manager;
	}
	
	@Override
	public String getSampleQuery() {
		StringBuffer sb = new StringBuffer();
		NamespaceUtil nsUtil = new NamespaceUtil();
		for (Entry<String, String> entry : nsUtil.getNamespace2PrefixMap().entrySet()) {
			String ns = entry.getKey();
			String prefix = entry.getValue();
			sb.append("PREFIX ");
			sb.append(prefix);
			sb.append(": <");
			sb.append(ns);
			sb.append(">\n");
		}
		sb.append("PREFIX m: <https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#>\n\n\n");
		sb.append("SELECT ?ss\n\tWHERE { ?s m:hasName 'Governing action'^^xsd:string .\n\t\t?s m:isSubcaseOfSchema*/m:isSubcaseOfSchema ?ss }");
		return sb.toString();
	}

	@Override
	public void precalculate() throws SparqlReasonerException {
		if (triples == null) {
			try {
				triples = Utilities.getOwlTripleStore(manager, true);
			}
			catch (RepositoryException e) {
				throw new SparqlReasonerException(e);
			}
		}
	}
	
	@Override
	public List<Object> executeQuery(String queryString) throws SparqlReasonerException {
		precalculate();
		try {
			RepositoryConnection connection = null;
			try {
				connection = triples.getRepository().getConnection();
				Query query = connection.prepareQuery(QueryLanguage.SPARQL, queryString);
				if (query instanceof TupleQuery) {
					System.out.println("Processing Tuple Query");
					return handleTupleQuery((TupleQuery) query);
				}
//				else if (query instanceof GraphQuery) {
//					System.out.println("Processing Graph Query");
//					return handleGraphQuery((GraphQuery) query);
//				}
//				else if (query instanceof BooleanQuery) {
//					System.out.println("Processing Boolean Query");
//					return handleBooleanQuery((BooleanQuery) query);
//				}
				else {
					throw new IllegalStateException("Can't handle queries of type " + query.getClass());
				}
			}
			finally {
				if (connection != null) {
					connection.close();
				}
			}
		}
		catch (Exception e) {
			throw new SparqlReasonerException(e);
		}
	}
	
	private List<Object> handleTupleQuery(TupleQuery tupleQuery) throws QueryEvaluationException, TupleQueryResultHandlerException {
		TupleQueryHandler handler = new TupleQueryHandler(triples, metaFactory);
		tupleQuery.evaluate(handler);
		return handler.getQueryResult();
	}
	
//	private SparqlResultSet handleGraphQuery(GraphQuery graph) throws QueryEvaluationException, RDFHandlerException {
//		GraphQueryHandler handler = new GraphQueryHandler(triples);
//		graph.evaluate(handler);
//		return handler.getQueryResult();
//	}
//	
//	private SparqlResultSet handleBooleanQuery(BooleanQuery booleanQuery) throws QueryEvaluationException {
//		List<String> columnNames = new ArrayList<String>();
//		columnNames.add("Result");
//		SparqlResultSet result = new SparqlResultSet(columnNames);
//		List<Object> row = new ArrayList<Object>();
//		row.add(booleanQuery.evaluate() ? "True" : "False");
//		result.addRow(row);
//		return result;
//	}

	@Override
	public void dispose() {
		
	}

}
