package edu.berkeley.icsi.metanet.wiki2owl;

import java.util.logging.Level;
import java.util.logging.Logger;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.PrefixManager;

/**
 * Class for parsing the MediaWiki Export XML format, which is a wrapper for
 * the MediaWiki page format.  Pages of this format are generated from
 * Special:Export.
 * 
 * @author Jisup Hong <jhong@icsi.berkeley.edu>
 */
public class WikiPageHandler extends DefaultHandler {
    
    private static final Logger logger = Logger.getLogger("WikiPageHandler");
        
    String pageTitle;
    String pageId;
    String pageText;
    StringBuffer content = null;
    boolean inpage = false;
    boolean intitle = false;
    boolean inid = false;
    boolean intext = false;
    boolean inrevision = false;
    String lang;
    
    OWLOntology ontology;
    String ontoPrefix = "";
    OWLOntology repository;
    
    PrefixManager pm;

    public void setLogLevel(Level level) {
        logger.setLevel(level);
    }
    
    public void setLanguage(String s) {
        lang = s;
    }
    
    private void parseWikiPage (String title, String id, String text) {        
        logger.log(Level.INFO, "Parsing page: {0}", title);
        WikiTemplateParser wtp = new WikiTemplateParser(title,text,repository,pm,ontology,ontoPrefix);
        wtp.setLogLevel(logger.getLevel());
        wtp.setLanguage(lang);
        wtp.parse();
        logger.log(Level.INFO, "Done parsing page: {0}", title);
    }

    public void setOntology(OWLOntology onto, String pref) {
        ontology = onto;
        ontoPrefix = pref;
    }
    public void setRepository(OWLOntology repo) {
        repository = repo;
        pm = (PrefixManager)repo.getOWLOntologyManager().getOntologyFormat(repo);
    }
    @Override
    public void startElement (String namespaceURI, String localName,
                              String qName, Attributes atts) throws SAXException{
        if (qName.equalsIgnoreCase("page")) {
            inpage = true;
        }
        if (qName.equalsIgnoreCase("title")) {
            content = new StringBuffer();
            intitle = true;
        }
        if (qName.equalsIgnoreCase("id") & !inrevision) {
            content = new StringBuffer();
            inid = true;
        }
        if (qName.equalsIgnoreCase("text")) {
            content = new StringBuffer();
            intext = true;
        }
        if (qName.equalsIgnoreCase("revision")) {
            inrevision = true;
        }
    }

    @Override
    public void endElement (String namespaceURI, String localName,
                            String qName) throws SAXException {
        if (qName.equalsIgnoreCase("page")) {
            // process page data?
            parseWikiPage(pageTitle,pageId,pageText);
            inpage = false;
        }
        if (qName.equalsIgnoreCase("text")) {
            pageText = content.toString();
            intext = false;
            content = null;
        }
        if (qName.equalsIgnoreCase("id") & inid) {
            pageId = content.toString();
            inid = false;
            content = null;
        }
        if (qName.equalsIgnoreCase("title")) {
            pageTitle = content.toString();
            intitle = false;
            content = null;
        }
        if (qName.equalsIgnoreCase("revision")) {
            inrevision = false;
        }
        if (qName.equalsIgnoreCase("error")) {
        	logger.severe("Error element in XML!");
        	throw new SAXException("Wiki API access error");
        }
    }

    @Override
    public void characters (char ch[], int start, int length) throws SAXException {
        if (intitle || intext || inid) {
            content.append(new String(ch, start, length));
        }
    }  
}
