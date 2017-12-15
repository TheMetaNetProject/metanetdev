package edu.berkeley.icsi.metanet.semaforParser;

import edu.berkeley.icsi.metanet.mwtemplateparser.MediaWikiParse;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.security.auth.login.FailedLoginException;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.PosixParser;
import org.wikipedia.Wiki;

/**
 * A class that extracts template information from the Metanet MediaWiki and
 * outputs it to text files in such a way that SEMAFOR and the XMLParser can
 * use.
 * @author bgthai
 */
public class WikiExtracter {
	private static final String DEFAULT_SERVER = "metaphor.icsi.berkeley.edu";
	private static final String DEFAULT_BASE = "test";
	private static final String DEFAULT_USER = "icsi";
	private static final String DEFAULT_PW = "pw";
	
	private BufferedWriter sentencesWriter;
	private BufferedWriter lemmasWriter;
	
	private MediaWikiParse mwParser = new MediaWikiParse();
	private String wikiServer;
	private String wikiUser;
    private String wikiPw;
    private String wikiBase;
    private Wiki wiki;
    
    private CommandLineParser parser = new PosixParser();
	private Options options = new Options();
	
	/**
	 * Constructs a new WikiExtracter and sets the CLI options
	 */
	protected WikiExtracter() {
		options.addOption("s", true, "Wiki server (default: " + 
				DEFAULT_SERVER + ")");
		options.addOption("b", true, "Wiki basename (default: " + 
				DEFAULT_BASE + ")");
		options.addOption("u", true, "Wiki username (default: " +
				DEFAULT_USER + ")");
		options.addOption("p", true, "Wiki password");
		options.addOption("h", false, "Print this help message");
	}
	
	/**
	 * Set the Wiki server name for the Wiki connection
	 */
	protected void setWikiServer(String server) {
		wikiServer = server;
	}
	
    /**
     * Set the Wiki basename for the Wiki connection
     */
    protected void setWikiBase(String base) {
    	wikiBase = "/" + base;
    }
    
    /**
     * Set user login for the Wiki connection
     */
	protected void setWikiUser(String username) {
		wikiUser = username;
	}
	
	/**
	 * Set the user password for the Wiki connection
	 */
	protected void setWikiPw(String pw) {
		wikiPw = pw;
	}
	
	/**
	 * Initialize connection to the Wiki page using the set login credentials
	 * and server info
	 */
	protected void initConnection() {
		wiki = new Wiki(wikiServer, wikiBase);
		wiki.setThrottle(5000);
		if (wikiUser != null) {
			try {
				wiki.login(wikiUser, wikiPw.toCharArray());
			} catch (FailedLoginException e) {
				System.err.println("Error: Failed to login to " + wikiServer + 
						wikiBase + " as " + wikiUser);
				System.exit(1);
			} catch (IOException e) {
				System.err.println("Error: IO error encountered while " +
						"establishing connection to " + wikiServer + wikiBase);
				System.exit(1);
			}
		}
	}

	/**
	 * Process the given Wiki page. Extracts the linguistic source, linguistic
	 * target, and all example sentences, and writes them out to the sentence
	 * and lemma files.
	 * @param pageTitle - title of the page to be processed
	 * @throws IOException thrown if there is an error accessing the Wiki or
	 * writing out to the output files
	 */
	protected void processWikiPage(String pageTitle) throws IOException {
		String lingTarget, lingSource;
		ArrayList<String> sentences;
		String text = wiki.getPageText(pageTitle);
		try {
			mwParser.parseAndSave(pageTitle, text);
			lingTarget = mwParser.getLingTarget(pageTitle);
			lingSource = mwParser.getLingSource(pageTitle);
			sentences = mwParser.getExampleTexts(pageTitle);
			for (String sentence : sentences) {
				sentencesWriter.append(sentence);
				sentencesWriter.append(sentence);
				lemmasWriter.append(lingTarget);
				lemmasWriter.append(lingSource);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * Process all linguistic metaphor pages for the set Wiki connection
	 * @throws IOException 
	 */
	protected void processAllPages() throws IOException {
		if (wiki == null) {
			throw new IllegalStateException("Wiki connection not established");
		}
		for (String pageTitle : wiki.getCategoryMembers("Linguistic metaphor")) {
			processWikiPage(pageTitle);
		}
		sentencesWriter.flush();
		lemmasWriter.flush();
	}
	
	/**
	 * Processes the command-line arguments for CLI options and for the two
	 * file name arguments
	 * @param args - the array of command-line arguments given in main()
	 */
	protected void processCmdLineArgs(String[] args) {
		CommandLine cmd = null;
		
		/*
		 * Parse CLI options
		 */
		try {
			cmd = parser.parse(options, args);
		} catch (ParseException e) {
			System.err.println("Error: Invalid command-line arguments");
			System.exit(1);
		}
		
		if (cmd.hasOption('h')) {
			printCmdLineHelp();
		}
		
		String username = cmd.getOptionValue('u');
		String pw = cmd.getOptionValue('p');
		String basename = cmd.getOptionValue('b');
		String server = cmd.getOptionValue('s');
		
		/*
		 * Set variables associated with the CLI options. If no CLI option was
		 * provided, set the variable to its default value.
		 */
		if (username == null) {
			setWikiUser(DEFAULT_USER);
		} else {
			setWikiUser(username);
		}
		
		if (pw == null) {
			setWikiPw(DEFAULT_PW);
		} else {
			setWikiPw(pw);
		}
		
		if (basename == null) {
			setWikiBase(DEFAULT_BASE);
		} else {
			setWikiBase(basename);
		}
		
		if (server == null) {
			setWikiServer(DEFAULT_SERVER);
		} else {
			setWikiServer(server);
		}
		
		/*
		 * Parse arguments and create file writers for the sentences and the 
		 * target lemmas output files
		 */
		@SuppressWarnings("unchecked")
		List<String> argList = cmd.getArgList();
		if (argList.size() != 2) {
			System.err.println("Error: Must provide exactly two arguments");
			printCmdLineHelp();
		}
		
		try {
			sentencesWriter = new BufferedWriter(new FileWriter(
					new File(argList.get(0))));
		} catch (IOException e) {
			System.err.println("Error: Could not create writer for" +
					" the sentences output file");
			System.exit(1);
		}
		
		try {
			lemmasWriter = new BufferedWriter(new FileWriter(
					new File(argList.get(1))));
		} catch (IOException e) {
			System.err.println("Error: Could not create writer for" +
					" the target lemmas output file");
			System.exit(1);
		}
	}
	
	/**
	 * Print the help message for the CLI and exits the program
	 */
	private void printCmdLineHelp() {
		HelpFormatter formatter = new HelpFormatter();
		formatter.printHelp(
				"WikiExtracter [OPTIONS] <sentences-output-file-path> <lemmas-output-file-path>", 
				options);
		System.exit(0);
	}
	
	public static void main(String[] args) throws IOException {
		WikiExtracter we = new WikiExtracter();
		we.processCmdLineArgs(args);
		we.initConnection();
		we.processAllPages();
	}
}
