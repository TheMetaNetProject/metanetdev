package edu.berkeley.icsi.metanet.wiki2owl;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.security.auth.login.FailedLoginException;
import javax.swing.JLabel;
import javax.swing.JProgressBar;
import javax.swing.SwingWorker;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.PrefixManager;
import org.wikipedia.Wiki;
import org.xml.sax.SAXException;

import edu.berkeley.icsi.metanet.wikifileapi.WikiFileApi;

/**
 * Class for retrieving XML page exports from the Metanet Semantic
 * MediaWiki and populating an ontology with instances of metaphors
 * and frames.  This can be instantiated either as a plugin for
 * Protege 4.x or run from the command line through WikiParserCmd.
 * 
 * @author Jisup Hong <jhong@icsi.berkeley.edu>
 */
public class WikiParser extends SwingWorker<Void,Void> {

    public static final Set<String> LANGLIST = new HashSet<String>();
    public static final List<String> CATEGORIES = new ArrayList<String>();
    public static final List<String> NAMESPACES = new ArrayList<String>();

    private static final Logger logger = Logger.getLogger("WikiParser");
    private static final int BATCH_SIZE = 50;
    
    static {
        LANGLIST.add("en");
        LANGLIST.add("es");
        LANGLIST.add("fa");
        LANGLIST.add("ru");
        LANGLIST.add("test");

        CATEGORIES.addAll(Arrays.asList("Frame family","Metaphor family",
        		"Frame", "Metaphor", "IARPASourceConcept",
        		"IARPATargetConcept", "MetaRC", "CxnMP"));
        NAMESPACES.addAll(Arrays.asList("Frame_family","Metaphor_family",
        		"Frame", "Metaphor", "IConcept",
        		"MetaRC", "CxnMP"));
    }

    private String wikiUser;
    private String wikiPw;
    private String wikiServer = null;
    private String wikiProtocol = "https";
    private String wikiBase = null;
    private String wikiFileRoot = null;
    
    private Wiki wiki = null;
    private WikiFileApi wikif = null;
    
    private OWLOntology ontology;
    private OWLOntology repository;
    private PrefixManager pm;
    private String ontoPrefix;
    private String progressMessage;
    
    private String lang;
    
    public void setWikiServer(String s) {
        wikiServer = s;
    }
    
    public void setWikiProtocol(String p) {
    	wikiProtocol = p;
    }
    
    public void setWikiRoot(String r) {
    	wikiFileRoot = r;
    }

    public void setLanguage(String s) {
        lang = s;
    }
    
    public void setWikiBase(String l) {
        wikiBase = l;
    }

    public void setLogLevel(Level level) {
        logger.setLevel(level);
    }
    
    public void setOntology(OWLOntology onto, String prefix) {
        ontology = onto;
        ontoPrefix = prefix;
    }
    public void setRepository(OWLOntology repo) {
        repository = repo;
        pm = (PrefixManager)repository.getOWLOntologyManager().getOntologyFormat(repository);
    }
    
    public void initializeWiki() throws IOException {
    	if (wikiServer != null) {
	        try {
	            wiki = new Wiki(wikiServer, wikiBase, wikiProtocol); // create a new wiki connection
	            wiki.setLogLevel(logger.getLevel());
	            wiki.setThrottle(5000); // set the edit throttle to 0.2 Hz
	            wiki.login(wikiUser, wikiPw.toCharArray());
	        } catch (FailedLoginException fe) {
	            throw new IOException(fe.getMessage());
	        }
    	}
    	if (wikiFileRoot != null) {
    		wikif = new WikiFileApi(wikiFileRoot);
    	}
    }
    
    private void closeWiki() {
        wiki.logout();
    }
    
    /**
     * Import wiki pages using one of the two methods: HTTP connection
     * to wiki itself, or by reading files from the filesystem.  Prefer
     * the latter.
     * 
     * @throws IOException
     */
    public void importWiki() throws IOException {
    	if (wikiFileRoot != null) {
    		logger.info("Importing from file root "+wikiFileRoot);
    		importWikiViaFile();
    		return;
    	}
    	if (wikiServer != null) {
    		logger.info("Importing from server "+wikiServer);
    		importWikiViaHTTP();
    		return;
    	}
    }

    /*
     * Import wiki pages into the ontology
     * 
     * Retrieves pages from the wiki based on the categories listed in
     * CATEGORIES, parses, them and populates the ontology.
     * 
     * @throws  IOException
     */
    public void importWikiViaHTTP() throws IOException {

        // assume connection to wiki has already been initialized

		List<String> pages = new ArrayList<String>();
        setProgressMessage("Retrieving list of pages to import...");
        logger.info("Retrieving list of pages to import ...");
        setProgress(0);
        int interval = (int)(100 / CATEGORIES.size());
        int prog = 0;
        for (String cat : CATEGORIES) {
            if (isCancelled()) {
                throw new IOException("Import canceled.");
            }
            pages.addAll(Arrays.asList(wiki.getCategoryMembers(cat)));
            prog += interval;
            setProgress(prog);
        }
        int numpages = pages.size();
        setProgressMessage("Lists retrieved.");
        logger.info("Lists of pages retrieved.");
        setProgress(100);
        
        
        // limit is 500 for bots/sysops for extraction
        // do in batches of 500, use this to display progress
        
        int startIndex = 0;
        int endIndex = BATCH_SIZE;
        List<String> subPages = null;
        String pagesXML;
        setProgressMessage("Importing wiki pages...");
        logger.info("Importing wiki pages...");
        setProgress(1);
        while (pages.size() > endIndex) {
            if (isCancelled()) {
                throw new IOException("Import canceled.");
            }
            // read sublist and process
            subPages = (List<String>)pages.subList(startIndex, endIndex);
            pagesXML = wiki.export(subPages);
            doImport(pagesXML, repository);
            setProgress(Math.min((int)((endIndex*100)/numpages),100));
            logger.severe("Progress: "+ getProgress() + " startIndex: "+startIndex +" endIndex: "+endIndex);
            // update indices
            startIndex = endIndex;
            endIndex += BATCH_SIZE;
        }
        // import the remaining pages
        endIndex = pages.size();
        if (endIndex > startIndex) {
        	subPages = (List<String>)pages.subList(startIndex,endIndex);
        	pagesXML = wiki.export(subPages);
        	doImport(pagesXML, repository);
        }
        logger.severe("Progress: "+ getProgress() + " startIndex: "+startIndex +" endIndex: "+endIndex);
        setProgressMessage("Import complete");
        logger.info("Import complete");
        setProgress(100);
    }

    /*
     * Import wiki pages into the ontology via the File Api
     * 
     * Retrieves pages from the wiki based on the namespaces listed in
     * NAMESPACES, parses them and populates the ontology.
     * 
     * @throws  IOException
     */
    public void importWikiViaFile() throws IOException {


		List<String> pages = new ArrayList<String>();
        setProgressMessage("Retrieving list of pages to import...");
        logger.info("Retrieving list of pages to import ...");
        setProgress(0);
        int interval = (int)(100 / NAMESPACES.size());
        int prog = 0;
		for (String ns : NAMESPACES) {
			pages.addAll(wikif.getNamespaceMembers(ns));
            prog += interval;
            setProgress(prog);
		}    	
        int numpages = pages.size();
        setProgressMessage("Lists retrieved.");
        logger.info("Lists of pages retrieved.");
        setProgress(100);
        
        
        // limit is 500 for bots/sysops for extraction
        // do in batches of 500, use this to display progress
        
        setProgressMessage("Importing wiki pages...");
        logger.info("Importing wiki pages...");
        setProgress(1);
        int pnum = 0;
        for (String title : pages) {
        	pnum += 1;
        	String text = wikif.getPageText(title);
        	logger.log(Level.INFO, "Parsing page: {0}", title);
            WikiTemplateParser wtp = new WikiTemplateParser(title,text,repository,pm,ontology,ontoPrefix);
            wtp.setLogLevel(logger.getLevel());
            wtp.setLanguage(lang);
            wtp.parse();
            logger.log(Level.INFO, "Done parsing page: {0}", title);
            setProgress(Math.min((int)((pnum*100)/numpages),100));
        }        
        setProgressMessage("Import complete");
        logger.info("Import complete");
        setProgress(100);
    }
    
    private void doImport(String xmlContent, OWLOntology repo) throws IOException {
        
        SAXParserFactory factory = SAXParserFactory.newInstance();

        try {
            SAXParser sp = factory.newSAXParser();

            // set up the wikipage handler
            WikiPageHandler wh = new WikiPageHandler();
            wh.setLogLevel(logger.getLevel());
            wh.setOntology(ontology, ontoPrefix);
            wh.setLanguage(lang);
            wh.setRepository(repo);

            InputStream in = new ByteArrayInputStream(xmlContent.getBytes("UTF-8"));

            // parse and populate
            sp.parse(in, wh);
        } catch (ParserConfigurationException ex) {
            logger.log(Level.SEVERE, "Error configurting XML parser", ex);
            throw new IOException("Error configuring XML parser.");
        } catch (SAXException ex) {
            logger.log(Level.SEVERE, "Error parsing XML.", ex);
            logger.severe("******** XML content ********\n"+xmlContent);
            throw new IOException("Error parsing XML.");
        }
    }
    
    public void setWikiLogin(String wikiuser, String wikipw) {
        wikiUser = wikiuser;
        wikiPw = wikipw;
    }
    
    private void setProgressMessage(String m) {
        progressMessage = m;
    }
    
    public String getProgressMessage() {
        return progressMessage;
    }
    
    public WikiParser() {
    }

    @Override
    protected Void doInBackground() throws Exception {
        importWiki();
        return null;
    }
}
