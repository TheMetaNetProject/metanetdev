package edu.berkeley.icsi.metanet.metaphorQuery;

import java.util.Collection;
import java.util.List;

import edu.berkeley.icsi.metanet.repository.Metaphor;
import edu.berkeley.icsi.metanet.repository.Schema;

public interface MetaNetInterface {
	
	public List<Object> runGeneralQuery(String query);
	
	public Collection<? extends Schema> getSchemasRelatedToBy(String schemaName, String propertyName);
	
	public Collection<? extends Schema> getAllSchemasRelatedToBy(String schemaName, String propertyName);
	
	public Collection<? extends Metaphor> getMetaphorsRelatedToBy(String metaphorName, String propertyName);
	
	public Collection<? extends Metaphor> getAllMetaphorsRelatedToBy(String metaphorName, String propertyName);

}
