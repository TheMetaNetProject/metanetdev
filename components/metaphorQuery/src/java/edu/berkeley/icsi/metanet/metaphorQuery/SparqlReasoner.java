package edu.berkeley.icsi.metanet.metaphorQuery;

import java.util.List;

public interface SparqlReasoner {

	void precalculate() throws SparqlReasonerException;

	String getSampleQuery();

	List<Object> executeQuery(String query) throws SparqlReasonerException;

	void dispose();
}
