package edu.berkeley.icsi.metanet.owl2sql;

import java.sql.SQLException;
import java.sql.Statement;

public class DatabaseHandler {

    /**
     * Drops the previous database if necessary and creates a new database
     *
     * @throws SQLException Throws a SQL exception if an error occurs in
     * creating the new database
     */
    protected static void prepare(Statement stmt, String dbName, boolean doDrop)
            throws SQLException {
        if (doDrop == true) {
            try {
                stmt.execute("DROP DATABASE " + dbName);
                System.out.println("Previous database " + dbName + " dropped");
            } catch (SQLException e) {
                System.err.println("Error dropping DB " + dbName);
            }
        }
        try {
            stmt.execute(
                    "CREATE DATABASE " + dbName
                    + " DEFAULT CHARACTER SET " + Basics.DEFAULT_CHAR_SET
                    + " DEFAULT COLLATE " + Basics.DEFAULT_COLLATE);
            stmt.execute("SET NAMES " + Basics.DEFAULT_CHAR_SET);
            System.out.println("Empty database " + dbName + " created");
            stmt.execute("use " + dbName);
        } catch (SQLException e) {
            // do nothing: probably it's because it exists already
            stmt.execute("use " + dbName);
        }
    }
}
