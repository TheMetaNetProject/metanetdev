package edu.berkeley.icsi.metanet.owl2sql;

import java.io.Console;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;

import org.semanticweb.owlapi.model.OWLOntology;

public class ConsoleShell extends Shell {
	Console console;
	
	protected ConsoleShell() {
		console = System.console();
		if (console == null) {
			System.err.println("Error: If server info is not included as " +
					"command-line arguments, tool must be opened in " +
					"interactive console environment.");
			System.exit(1);
		}
	}
	
	@Override
	String getDBName() {
		String dbName;
		while (true) {
			dbName = console.readLine("Choose database name (will overwrite " +
					"any existing database with the same name): ");
			if (Utilities.isValidDBName(dbName)) {
				return dbName;
			} else {
				System.err.println("Error: Invalid database name. Must " +
						"contain only alphanumeric characters, underscores, " +
						"and string symbols ($)");
			}
		}
	}

	@Override
	Connection establishConnection() {
		Connection con;
		while (true) {
			server = console.readLine("Enter MySQL server name: ");
			if (server.length() == 0 || server.contains("/") || 
					server.contains(":")) {
				System.err.println("Error: Invalid server name. No \":\" " +
						"or \"/\". (i.e. \"localhost\")");
				continue;
			}
			while (true) {
				try {
					port = Integer.parseInt(console.readLine("Enter MySQL " +
							"server port number (default 3306): "));
					break;
				} catch (NumberFormatException ex) {
					System.err.println("Error: Port number must be an integer");
				}
			}
			username = console.readLine("Enter username: ");
			pw = String.valueOf(console.readPassword("Enter password: "));
			try {
				con = Connector.getConnection(server, port, username, pw);
				return con;
			} catch (SQLException ex) {
				System.err.println("Error: Unable to establish connection");
			}
		}
	}

	@Override
	TableBuilder initTableBuilder(OWLOntology ont, Statement stmt) {
		boolean simple;
		String resp;
		
		while (true) {
			resp = console.readLine("Build a simplified database? [Y/n]");
			if (resp.equals("Y")) {
				simple = true;
				break;
			} else if (resp.equals("n")) {
				simple = false;
				break;
			} else {
				System.err.println("Error: Invalid choice");
			}
		}
		if (simple) {
			return new SimpleTableBuilder(ont, stmt, verbose);
		} else {
			return new FullTableBuilder(ont, stmt, verbose);
		}
	}

}
