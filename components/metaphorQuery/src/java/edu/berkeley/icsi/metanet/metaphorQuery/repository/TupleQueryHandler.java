package edu.berkeley.icsi.metanet.metaphorQuery.repository;

import java.util.ArrayList;
import java.util.List;

import org.openrdf.model.Value;
import org.openrdf.query.Binding;
import org.openrdf.query.BindingSet;
import org.openrdf.query.TupleQueryResultHandler;
import org.openrdf.query.TupleQueryResultHandlerException;
import org.openrdf.repository.RepositoryException;
import org.protege.owl.rdf.api.OwlTripleStore;

import edu.berkeley.icsi.metanet.metaphorQuery.SparqlResultSet;
import edu.berkeley.icsi.metanet.repository.MetaNetFactory;

public class TupleQueryHandler implements TupleQueryResultHandler {
	private OwlTripleStore triples;
	private SparqlResultSet queryResult;
	private MetaNetFactory metaFactory;
	private ArrayList<Object> results;
	
	public TupleQueryHandler(OwlTripleStore triples, MetaNetFactory metaFactory) {
		results = new ArrayList<Object>();
		this.metaFactory = metaFactory;
		this.triples = triples;
	}
	
	public List<Object> getQueryResult() {
		return results;
	}

	@Override
	public void startQueryResult(List<String> bindingNames) throws TupleQueryResultHandlerException {
		queryResult = new SparqlResultSet(bindingNames);
	}

	@Override
	public void handleSolution(BindingSet bindingSet) throws TupleQueryResultHandlerException {
		try {
//			System.out.println("Column count is " + queryResult.getColumnCount());
			for (int i = 0; i < queryResult.getColumnCount(); i++) {
//				System.out.println("Column NAME is " + queryResult.getColumnName(i));
				String columnName = queryResult.getColumnName(i);
				Binding binding = bindingSet.getBinding(columnName);
				Value v = binding != null ? binding.getValue() : (Value) null;
				results.add(Util.convertValue(triples, v));
//				System.out.println(Util.convertValue(triples, v));
			}
		}
		catch (RepositoryException re) {
			throw new TupleQueryResultHandlerException(re);
		}
	}
	
	@Override
	public void endQueryResult() throws TupleQueryResultHandlerException {

	}

}
