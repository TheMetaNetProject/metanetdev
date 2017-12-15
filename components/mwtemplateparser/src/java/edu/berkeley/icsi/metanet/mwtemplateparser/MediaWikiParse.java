package edu.berkeley.icsi.metanet.mwtemplateparser;
import java.util.Scanner;
import java.util.ArrayList;
import java.io.*;
import java.util.HashMap;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * This class is used for parsing a MediaWiki page and storing it in memory as a Java Data Structure.
 * Once it is saved in memory, you can perform edits on it and convert it back into a MediaWiki page.
 * @author Jalal Buckley
 */
public class MediaWikiParse {
    /* ---------------------------------------------------------------------- */
    /* Constructor / Public Methods */
    /* ---------------------------------------------------------------------- */
    
    /**
     * Constructor MediaWikiParse class. Initialize instance variables.
     */
    public MediaWikiParse() {
        tokenIndex = 0;
        endTokenIndex = 0;
        endToken = "";
        startToken = "";
        pages = new HashMap<String, MediaWikiContainer>();
        escapedPipes = new ArrayList<Integer>();
    }
    
    /**
     * Parse the MediaWiki page input and save it to memory. Return its name
     * so the user can take note of it if desired.
     * @param input the MediaWiki page
     * @return the page's name
     */
    public void parseAndSave(String title, String input) {
        input = MediaWikiParse.findAndReplacePipes(input);
        MediaWikiContainer newContainer = makeMediaWikiContainer(input,0);
        pages.put(title, newContainer);
    }
    
    /**
     * Get the MediaWiki page associated with this name
     * @param name the page name
     * @return the MediaWiki page
     */
    public String getPage(String name) {
        MediaWikiContainer aContainer = pages.get(name);
        return aContainer.outputToMediaWiki();
    }
    
    /**
     * Get the MediaWiki page associated with this name as an XML Document
     * @param name the page name
     * @return XML document
     */
    public String getPageAsXML(String name) {
        MediaWikiContainer aContainer = pages.get(name);
        String xmlFile = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
        xmlFile += '\r';
        xmlFile += aContainer.saveToXML(1);
        return xmlFile;
    }
    
    /**
     * Prints the contents of a page. Used for debugging purposes.
     * @param name the page name
     */
    public void printContentsOfPage(String name) {
        pages.get(name).printMediaWikiContainer(0);
    }
    
    /**
     * Remove the MediaWiki page from memory with this name
     * @param name the page name
     */
    public void removePage(String name) {
        pages.remove(name);
    }
    
    /**
     * Get the names of the pages that are saved in memory
     * @return Set of names
     */
    public Set<String> getPageNames() {
        return pages.keySet();
    }
    
    /**
     * Get all of the values associated with the chosen element. (i.e., find all 
     * of the "Example.Text"'s, etc.)
     * @param name
     * @return 
     */
    public ArrayList<String> getTheElementValues(String pageTitle, String name) {
        MediaWikiContainer page = pages.get(pageTitle);
        ArrayList<String> theElements = page.getElementValues(name);
        return theElements;
    }
    
    /**
     * Get the Linguistic Source from a page.
     * @param pageTitle
     * @return 
     */
    public String getLingSource(String pageTitle) throws Exception {
        MediaWikiContainer page = pages.get(pageTitle);
        return page.getLSource();
    }
    
    /**
     * Get the Linguistic Target from a page.
     * @param pageTitle
     * @return 
     */
    public String getLingTarget(String pageTitle) throws Exception {
        MediaWikiContainer page = pages.get(pageTitle);
        return page.getLTarget();
    }
    
    /**
     * 
     * @param pageTitle
     * @return 
     */
    public ArrayList<String> getExampleTexts(String pageTitle) {
        MediaWikiContainer page = pages.get(pageTitle);
        ArrayList<String> theElements = page.getElementValues("Example.Text");
        return theElements;
    }
    
    /* ---------------------------------------------------------------------- */
    /* Fixes */
    /* ---------------------------------------------------------------------- */
    
    /**
     * Check that there is a metaphor alias corresponding to the page's title
     * @param pageTitle 
     */
    public void aliasCheck(String pageTitle) {
        MediaWikiContainer page = pages.remove(pageTitle);
        page.hasAlias(pageTitle);
        pages.put(pageTitle, page);
    }
    
    /**
     * Uncapitalize the roles
     * @param pageTitle 
     */
    public void uncapitalizeRoles(String pageTitle) {
        MediaWikiContainer page = pages.remove(pageTitle);
        page.uncapRoles();
        pages.put(pageTitle, page);
    }
    
    /**
     * Make sure that words in a Schema name are separated by spaces, not underscores
     * @param pageTitle 
     */
    public void fixSchema(String pageTitle) {
        MediaWikiContainer page = pages.remove(pageTitle);
        page.fixSchemaNames();
        pages.put(pageTitle, page);
    }
    
    /* ---------------------------------------------------------------------- */
    /* Private Methods */
    /* ---------------------------------------------------------------------- */
    
    private static String findAndReplacePipes(String input) {
        int nextPipeIndex = 0;
        nextPipeIndex = input.indexOf("{{!}}");
        while (nextPipeIndex != -1) {
            escapedPipes.add(nextPipeIndex);
            input = input.replaceFirst(Pattern.quote("{{!}}"), "|");
            nextPipeIndex = input.indexOf("{{!}}");
        }
        return input;
    }
    
    /**
     * Returns true if the input represents a "template" in MediaWiki markup
     * @param str MediaWiki Input
     * @param index the location we are parsing
     * @return 
     */
    private static boolean isBracket(String str, int index) {
        return str.substring(index, index+2).equals("{{") || str.substring(index, index+2).equals("}}");
    }

    /**
     * Get the index of the next token
     * @param str MediaWiki page
     * @return index of the next token
     */
    private static int nextTokenIndex(String str) {
        int openBracket = str.indexOf("{{");
        int pipe = str.indexOf("|");
        int equals = str.indexOf("=");
        int closingBracket = str.indexOf("}}");
        return Math.min(Math.min(Math.min(openBracket, pipe),equals),closingBracket);
    }
    
    /**
     * Get the index of the next token, starting at index
     * @param str the MediaWiki page
     * @param index index to start at
     * @return index of the next token
     */
    private static int nextTokenIndex(String str, int index) {
        boolean brackets = false;
        if (index == -1)
            index++;
        else if (brackets = isBracket(str, index))
            index += 2;
        else
            index++;
        
        int openBracket = str.indexOf("{{", index);
        int pipe = str.indexOf("|", index);
        while (escapedPipes.contains(pipe))
            pipe = str.indexOf("|", pipe+1);
        int equals = str.indexOf("=", index);
        int closingBracket = str.indexOf("}}", index);
        
        if (openBracket != -1 && pipe != -1 && equals != -1 && closingBracket != -1)
            return Math.min(Math.min(Math.min(openBracket, pipe),equals),closingBracket);
        
        else if (openBracket != -1 && pipe != -1 && equals != -1)
            return Math.min(Math.min(openBracket, pipe),equals);
        else if (openBracket != -1 && pipe != -1 && closingBracket != -1)
            return Math.min(Math.min(openBracket, pipe),closingBracket);
        else if (openBracket != -1 && closingBracket != -1 && equals != -1)
            return Math.min(Math.min(openBracket,equals),closingBracket);
        else if (closingBracket != -1 && pipe != -1 && equals != -1)
            return Math.min(Math.min(pipe,equals),closingBracket);
        
        else if (openBracket != -1 && pipe != -1)
            return Math.min(openBracket, pipe);
        else if (openBracket != -1 && equals != -1)
            return Math.min(openBracket, equals);
        else if (openBracket != -1 && closingBracket != -1)
            return Math.min(openBracket, closingBracket);
        else if (pipe != -1 && equals != -1)
            return Math.min(pipe, equals);
        else if (pipe != -1 && closingBracket != -1)
            return Math.min(pipe, closingBracket);
        else if (equals != -1 && closingBracket != -1)
            return Math.min(equals, closingBracket);
        
        else if (openBracket != -1)
            return openBracket;
        else if (pipe != -1)
            return pipe;
        else if (equals != -1)
            return equals;
        else if (closingBracket != -1)
            return closingBracket;
        else {
            if (brackets)
                return (index-1);
            else
                return (index-2);
        }
    }
    
    /**
     * Get the index of the last token, starting at 0 and ending at index
     * @param str the MediaWiki page
     * @param index index to end the search at
     * @return index of the last token
     */
    private static int lastTokenIndex(String str, int index) {
        index--;
        int openBracket = str.lastIndexOf("{{", index);
        int pipe = str.lastIndexOf("|", index);
        int equals = str.lastIndexOf("=", index);
        int closingBracket = str.lastIndexOf("}}", index);
        
        if (openBracket != -1 && pipe != -1 && equals != -1 && closingBracket != -1)
            return Math.min(Math.min(Math.min(openBracket, pipe),equals),closingBracket);
        
        else if (openBracket != -1 && pipe != -1 && equals != -1)
            return Math.min(Math.min(openBracket, pipe),equals);
        else if (openBracket != -1 && pipe != -1 && closingBracket != -1)
            return Math.min(Math.min(openBracket, pipe),closingBracket);
        else if (openBracket != -1 && closingBracket != -1 && equals != -1)
            return Math.min(Math.min(openBracket,equals),closingBracket);
        else if (closingBracket != -1 && pipe != -1 && equals != -1)
            return Math.min(Math.min(pipe,equals),closingBracket);
        
        else if (openBracket != -1 && pipe != -1)
            return Math.min(openBracket, pipe);
        else if (openBracket != -1 && equals != -1)
            return Math.min(openBracket, equals);
        else if (openBracket != -1 && closingBracket != -1)
            return Math.min(openBracket, closingBracket);
        else if (pipe != -1 && equals != -1)
            return Math.min(pipe, equals);
        else if (pipe != -1 && closingBracket != -1)
            return Math.min(pipe, closingBracket);
        else if (equals != -1 && closingBracket != -1)
            return Math.min(equals, closingBracket);
        
        else if (openBracket != -1)
            return openBracket;
        else if (pipe != -1)
            return pipe;
        else if (equals != -1)
            return equals;
        else if (closingBracket != -1)
            return closingBracket;
        else 
            return index;
    }
    
    /**
     * return the next token as a String
     * @param str the MediaWiki page
     * @param tokenIndex the index of the token
     * @return the token
     */
    private static String nextToken(String str, int tokenIndex) {
        if ( str.substring(tokenIndex,tokenIndex+2).equals("{{") || str.substring(tokenIndex,tokenIndex+2).equals("}}") )
            return str.substring(tokenIndex,tokenIndex+2);
        else
            return str.substring(tokenIndex, tokenIndex+1);
    }
    
    /**
     * Return the next Element located between the start and end indexes provided
     * @param str the MediaWiki page
     * @param start start index
     * @param end end index
     * @return element
     */
    private static String getElement(String str, int start, int end) {
        if (str.substring(start,start+2).equals("{{"))
            return str.substring(start+2,end);
        else
            return str.substring(start+1,end);
    }
    
    /**
     * Advance our tokens and token index references, so that they are pointing to
     * the next element in the MediaWiki page.
     * @param str MediaWiki page
     */
    private void advanceTokens(String str) {
        tokenIndex = endTokenIndex;
        endTokenIndex = nextTokenIndex(str, tokenIndex);
        endToken = nextToken(str, endTokenIndex);
        startToken = nextToken(str, tokenIndex);
        
        while (startToken.equals("=") && endToken.equals("=")) {
            endTokenIndex = nextTokenIndex(str,endTokenIndex);
            endToken = nextToken(str, endTokenIndex);
        }
    }
    
    /**
     * Move our tokens and token index references, so that they are pointing to the
     * previous element in the MediaWiki page.
     * @param str the MediaWiki page
     */
    private void pastTokens(String str) {
        endTokenIndex = tokenIndex;
        tokenIndex = lastTokenIndex(str, tokenIndex);
        startToken = nextToken(str, tokenIndex);
        endToken = nextToken(str, endTokenIndex);
    }
    
    /**
     * Set all of the tokens and token indexes to their initial values.
     */
    private void resetTokens() {
        tokenIndex = 0;
        endTokenIndex = 0;
        startToken = "";
        endToken = "";
    }

    /**
     * Starting at beginIndex, parse through the MediaWiki text, and store all of 
     * its information in an MediaWikiContainer object. Return that object.
     * @param str the MediaWiki page
     * @param beginIndex starting index
     * @return MediaWikiContainer object
     */
    private MediaWikiContainer makeMediaWikiContainer(String str, int beginIndex) {
        tokenIndex = nextTokenIndex(str, beginIndex-1);
        endTokenIndex = nextTokenIndex(str, tokenIndex);
        MediaWikiContainer temp = new MediaWikiContainer(getElement(str, tokenIndex,endTokenIndex));
        boolean brackets = false;
        temp.bracketsHere(true);
        advanceTokens(str);
        
        while (true) {
            if (startToken.equals("{{") || endToken.equals("|")) {
                advanceTokens(str);
                temp.bracketsHere(true);
            }
            
            if (startToken.equals("}}"))
                break;
            
            if (endToken.equals("=")) {
                String name = getElement(str,tokenIndex,endTokenIndex);
                advanceTokens(str);
                if (endToken.equals("|"))
                    temp.add(new Element(name, getElement(str,tokenIndex,endTokenIndex)));
                else if (endToken.equals("}}")) {
                    temp.add(new Element(name, getElement(str,tokenIndex,endTokenIndex)));
                    return temp;
                }
                else {
                    MediaWikiContainer nestedTemp = new MediaWikiContainer(name);
                    while (endToken.equals("{{")) {
                        MediaWikiContainer newTemp = makeMediaWikiContainer(str, endTokenIndex);
                        nestedTemp.add(newTemp);
                        advanceTokens(str);
                    }
                    temp.add(nestedTemp);
                advanceTokens(str);
                }   
            }
        }
        
        resetTokens();
        return temp;
    }
    
    /**
     * Output a set of MediaWikiContainers in MediaWiki markup
     * @param containers a set of MediaWikiContainers
     * @return a MediaWiki page
     */
    private static String outputToMediaWiki(ArrayList<MediaWikiContainer> containers) {
        String toReturn = "";
        for (int i = 0; i < containers.size(); i ++) {
            toReturn += containers.get(i).outputToMediaWiki();
        }
        return toReturn;
    }
    
    /* ---------------------------------------------------------------------- */
    /* Instance Variables */
    /* ---------------------------------------------------------------------- */
    
    /* Tokens are special characters ("|", "=", "{{", "}}") we look for when traversing a page. */
    /* In general, when traversing the MediaWiki page, the next thing we will be */
    /* adding to our data structure will be the text located in between tokenIndex and endTokenIndex */
    private int tokenIndex; //Index of the startToken
    private int endTokenIndex; //Index of the endToken
    private String endToken;
    private String startToken;
    
    /* All of the MediaWiki pages we have read into memory */
    HashMap<String, MediaWikiContainer> pages;
    
    private static ArrayList<Integer> escapedPipes;
}
