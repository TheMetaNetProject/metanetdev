package edu.berkeley.icsi.metanet.owl2sql;

import java.io.IOException;
import java.sql.SQLException;

/**
 * Interface for table builders
 * @author brandon
 *
 */
public interface TableBuilder {
	/**
	 * Builds the database
	 * @throws SQLException 
	 */
	void build() throws SQLException;
	
	void enableErrorLogging(String logPath) throws IOException;
}
