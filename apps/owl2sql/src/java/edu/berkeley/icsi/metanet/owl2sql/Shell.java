package edu.berkeley.icsi.metanet.owl2sql;

import java.io.File;
import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.PosixParser;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;

public abstract class Shell {

    String server, username, pw;
    boolean verbose = false;
    int port;
    TableBuilder tb;

    static void printHelp(Options options) {
        HelpFormatter formatter = new HelpFormatter();
        formatter.printHelp("owl2sql [OPTIONS] FILE", options);
        System.exit(0);
    }

    abstract Connection establishConnection();

    abstract String getDBName();

    /**
     * Initializes a table builder
     */
    abstract TableBuilder initTableBuilder(OWLOntology ont, Statement stmt);

    @SuppressWarnings("unchecked")
    public static void main(String args[]) {
        List<String> argList;
        Shell shell;
        boolean adequatePermissions = false;
        String path, logPath;
        String dbName;
        File owlFile;
        Connection con = null;
        OWLOntology ont = null;
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        Statement stmt = null;
        CommandLineParser parser;
        CommandLine cmd;
        boolean doDrop = false;

        System.out.println("owl2sql v" + Basics.VERSION);

        /*
         * Handle command-line arguments
         */

        Options options = new Options();
        options.addOption("C", false, "prompt server and user login info "
                + "from console");
        options.addOption("E", false, "enable error logging");
        options.addOption("server", true, "MySQL server name");
        options.addOption("port", true, "MySQL server port");
        options.addOption("u", true, "MySQL username");
        options.addOption("p", true, "MySQL password");
        options.addOption("db", true, "MySQL database name");
        options.addOption("help", false, "print help message");
        options.addOption("h", false, "print help message");
        options.addOption("v", false, "print verbose messages");
        options.addOption("drop", false, "drop existing database");
        options.addOption("simple", false, "creates a simplified database");

        parser = new PosixParser();
        cmd = null;
        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            System.err.println("Error: Invalid command-line arguments");
            Shell.printHelp(options);
            System.exit(1);
        }

        if (cmd.hasOption("drop")) {
            doDrop = true;
        }

        if (cmd.hasOption("help") || cmd.hasOption("h")) {
            Shell.printHelp(options);
        }

        argList = cmd.getArgList();
        if (argList.size() == 0) {
            System.err.println("Error: Must provide path of OWL file as "
                    + "argument");
            System.exit(1);
        } else if (argList.size() > 1) {
            System.err.println("Error: Only one argument can be provided");
        }

        path = argList.get(0);
        owlFile = new File(path);
        if (!owlFile.exists()) {
            System.err.println("Error: the file " + path + " does not exist");
            System.exit(1);
        }

        try {
            ont = manager.loadOntologyFromOntologyDocument(owlFile);
            System.out.println("Ontology file loaded");
        } catch (Exception ex) {
            System.err.println("Error: " + path + " is not a valid OWL file");
            ex.printStackTrace();
            System.exit(1);
        }

        if (cmd.hasOption("C")) {
            shell = new ConsoleShell();
        } else {
            shell = new CmdLineShell(cmd);
        }

        con = shell.establishConnection();
        System.out.println("Connection established");
        try {
            stmt = con.createStatement();
        } catch (SQLException e1) {
            System.err.println("Error: Could not create SQL statement");
            System.exit(1);
        }

        shell.tb = shell.initTableBuilder(ont, stmt);

        try {
            adequatePermissions = Connector.adequatePermissions(con);
        } catch (SQLException ex) {
            System.err.println("Error: Unable to check user permissions");
            System.exit(1);
        }

        if (!adequatePermissions) {
            System.err.println("Error: Inadequate user permissions on this "
                    + "MySQL server. Contact the database administrator.");
            System.exit(1);
        } else {
            System.out.println("Permissions checked");
        }

        dbName = shell.getDBName();

        try {
            DatabaseHandler.prepare(stmt, dbName, doDrop);
        } catch (SQLException ex) {
            System.err.println("Error: Could not prepare database");
            ex.printStackTrace();
            System.exit(1);
        }

        if (cmd.hasOption("E")) {
            logPath = System.getProperty("user.dir") + "/error.log";
            try {
                shell.tb.enableErrorLogging(logPath);
            } catch (IOException e) {
                System.err.println("Error: Could not initialize error "
                        + "logging to " + logPath
                        + ". Proceeding without error logging.");
            }
        }

        try {
            shell.tb.build();
        } catch (SQLException ex) {
            System.err.println("\nError: " + ex.getMessage());
            System.err.println("Error occurred while creating the "
                    + "new database. No changes committed.");
            ex.printStackTrace();
            System.exit(1);
        }

        try {
            con.commit();
            System.out.println("Committed changes to jdbc:mysql://" + shell.server
                    + ":" + shell.port + "/" + dbName);
        } catch (SQLException e) {
            System.err.println("Error: Unable to commit changes to database");
        }
    }
}
