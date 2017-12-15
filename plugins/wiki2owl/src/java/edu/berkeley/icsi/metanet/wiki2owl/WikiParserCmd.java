package edu.berkeley.icsi.metanet.wiki2owl;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.Collections;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.PosixParser;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.io.RDFXMLOntologyFormat;
import org.semanticweb.owlapi.model.AddImport;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLOntologyStorageException;
import org.semanticweb.owlapi.util.DefaultPrefixManager;
import org.semanticweb.owlapi.util.OWLEntityRemover;
import java.io.Console;
import org.semanticweb.owlapi.util.SimpleIRIMapper;

/**
 * Class to house the main method for command line invocation of the WikiParser,
 * which downloads pages from the MetaNet wiki and converts the MediaWiki template
 * calls to RDF/OWL.
 *
 * @author Jisup Hong <jhong@icsi.berkeley.edu>
 */
public class WikiParserCmd {
    
    private static final Logger logger = Logger.getLogger("WikiParserCmd");
    private static final String DEFAULT_WIKI_SERVER = "ambrosia.icsi.berkeley.edu:2080";
    private static final String DEFAULT_WIKI_SCRIPTPATH_PREFIX = "/dev/";
    private static final String ONTOLOGY_URL = "https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl";
    private static final String ONTOLOGY_BASE = "https://metaphor.icsi.berkeley.edu";
    private static final String REPO_FILE = "MetaphorRepository.owl";

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        
        String wikiuser = null;
        String wikipw = null;
        String lang = null;
        String mOntologyUrl = null;
        String server = null;
        String protocol = null;
        String scriptpath = null;
        String wikiroot = null;
        
        WikiParser wikip = new WikiParser();

        /*
         * Set up command line parser and initialize files and wiki
         */
        
        Options options = new Options();
        Option langOpt = new Option("l", "lang", true, "Wiki language code (en, es, fa, ru)");
        langOpt.setRequired(true);
        options.addOption(langOpt);
        Option ontologyUrl = new Option("o","onto", true, "Metaphor ontology URL");
        options.addOption(ontologyUrl);
        options.addOption("u", "user", true, "Wiki username");
        options.addOption("p", "password", true, "Wiki password");
        options.addOption("v", "verbose", false, "Display verbose messages");
        options.addOption("s", "server", true, "Wiki server hostname and port");
        options.addOption("t", "protocol", true, "Protocol to connect to wiki server (default:https)");
        options.addOption("w", "wikipath", true, "Wiki script path relative to server");
        options.addOption("r", "root", true, "Wiki filesystem sync root directory");
        String outputFile = null;
        Level logLevel = Level.SEVERE;
        CommandLineParser cparser = new PosixParser();
        try {
            CommandLine cmd = cparser.parse(options, args);
            lang = cmd.getOptionValue("lang");
            String user = cmd.getOptionValue("user");
            String pw = cmd.getOptionValue("password");
            String onto = cmd.getOptionValue("onto");
            server = cmd.getOptionValue("server");
            protocol = cmd.getOptionValue("protocol");
            scriptpath = cmd.getOptionValue("wikipath");
            wikiroot = cmd.getOptionValue("root");
            
            // if user/password were not given as parameters, read from Console
            if (user == null) {
                Console cons;
                if ((cons = System.console()) != null
                        && (user = cons.readLine("[%s]", "Username:")) != null) {
                    wikiuser = user;
                } else {
                    throw new ParseException("Error: Must specify wiki password.");
                }
            } else {
                wikiuser = user;
            }
            if (pw == null) {
                Console cons;
                char[] passwd;
                if ((cons = System.console()) != null
                        && (passwd = cons.readPassword("[%s]", "Password:")) != null) {
                    wikipw = new String(passwd);
                } else {
                    throw new ParseException("Error: Must specify wiki password.");
                }
            } else {
                wikipw = pw;
            }
            if (onto == null) {
            	mOntologyUrl = ONTOLOGY_URL;
            } else {
            	mOntologyUrl = onto;
            }
            if (protocol == null) {
            	protocol = "https";
            }
            if (WikiParser.LANGLIST.contains(lang)) {
                wikip.setWikiBase(lang);
            } else {
                throw new ParseException("Invalid lang parameter.");
            }
            if (cmd.hasOption("verbose")) {
                logLevel = Level.INFO;
            }
            if (server == null && wikiroot == null) {
            	server = DEFAULT_WIKI_SERVER;
            }
            if (scriptpath == null) {
            	scriptpath = DEFAULT_WIKI_SCRIPTPATH_PREFIX + lang;
            }
            String[] remainingArgs = cmd.getArgs();
            if (remainingArgs.length == 0) {
            	throw new ParseException("Output filename parameter missing.");
            }
            outputFile = remainingArgs[0];
            
        } catch (ParseException ex) {
            logger.log(Level.SEVERE, "Error: "+ex.getMessage());
            // automatically generate the help statement
            HelpFormatter formatter = new HelpFormatter();
            formatter.printHelp( "wiki2owl <outputfile>", options );
            System.exit(1);
        }
        // initialize logging levels
        logger.setLevel(logLevel);
        
        

        /*
         * Read in empty ontology to populate
         */
        String iriStr = getRepositoryIRIString(lang);
        IRI repIRI = IRI.create(iriStr);
        IRI ontoIRI = IRI.create(mOntologyUrl);
        
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        
        SimpleIRIMapper rmapper = new SimpleIRIMapper(repIRI, IRI.generateDocumentIRI());
        manager.addIRIMapper(rmapper);

        // Load the general metaphor ontology
        OWLOntology metaont = null;
        try {
            // Let's hope that the loader handles UTF-8 correctly.
            metaont = manager.loadOntology(ontoIRI);
        } catch (OWLOntologyCreationException ex) {
            logger.log(Level.SEVERE, "Error loading remote ontology", ex);
            System.exit(1);
        }
        
        // Create new ontology
        OWLOntology repo = null;
        try {
            // Let's hope that the loader handles UTF-8 correctly.
            repo = manager.createOntology(repIRI);
        } catch (OWLOntologyCreationException ex) {
            logger.log(Level.SEVERE, "Error loading remote ontology", ex);
            System.exit(1);
        }
        
        // Delete any individuals that are already in there
        /*
        OWLEntityRemover remover = new OWLEntityRemover(manager, Collections.singleton(metanet));
        for (OWLNamedIndividual i : metanet.getIndividualsInSignature()) {
            i.accept(remover);
        }
        manager.applyChanges(remover.getChanges());
        remover.reset();
        */
        
        // Add import of MetaphorOntology
        AddImport ai = new AddImport(repo,
        	manager.getOWLDataFactory().getOWLImportsDeclaration(IRI.create(mOntologyUrl)));
        manager.applyChange(ai);
        manager.getImports(repo);
        
     // Use same format
        RDFXMLOntologyFormat ofm = new RDFXMLOntologyFormat();
        ofm.setPrefix("metanet", ONTOLOGY_URL + "#");
        ofm.setDefaultPrefix(iriStr + "#");
        manager.setOntologyFormat(repo, ofm);
        
        wikip.setWikiServer(server);
        wikip.setWikiProtocol(protocol);
        wikip.setWikiRoot(wikiroot);
        wikip.setWikiBase(scriptpath);
        wikip.setWikiLogin(wikiuser, wikipw);
        wikip.setLogLevel(logLevel);
        wikip.setLanguage(lang);
        wikip.setOntology(metaont, "metanet");
        wikip.setRepository(repo);
        
        /*
         * Do wiki page parsing and population of OWL model
         */
        try {
        	wikip.initializeWiki();
            wikip.importWiki();
        } catch (IOException ex) {
            logger.log(Level.SEVERE, "Error importing wiki", ex);
            System.exit(1);
        }

        /* 
         * Write out Output file
         */
        File ofile = new File(outputFile);

        // save out file (ontology and individuals)
        logger.info("Saving out file ... ");
        try {
            manager.saveOntology(repo, IRI.create(ofile.toURI()));
        } catch (OWLOntologyStorageException ex) {
            logger.log(Level.SEVERE, "Error saving owl output file", ex);
            System.exit(1);
        }
        logger.info("done.");
    }
    
    private static String getRepositoryIRIString(String lang) {
        return ONTOLOGY_BASE + "/" + lang + "/" + REPO_FILE;
    }
}
