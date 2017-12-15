package edu.berkeley.icsi.metanet.mwtemplateparser;

import java.util.ArrayList;

/**
 * Instances of this class are used for storing objects found on MediaWiki pages.
 * Each MediaWikiContainer class has a set of objects. Note that we can have nested containers, i.e.:
 * - Metaphor (is of type MediaWikiContainer)
 *     - Aliases (is of type MediaWikiContainer)
 *         (Alias: foo1) (is of type Element)
 *         (Alias: foo2) (is of type Element)
 * @author Jalal Buckley
 */
public class MediaWikiContainer {
    /* The name of the MediaWikiContainer. */
    String containerName = "";
    /* The set of all the objects in a MediaWikiContainer */
    ArrayList<Object> page;
    /* Does this MediaWiki Object correspond to a "template" in the MediaWiki markup? */
    /* Needed in order to convert this back into MediaWiki markup   */
    boolean brackets = false;

    /**
     * Initialize a MediaWikiContainer object.
     * @param name the name of the MediaWikiContainer
     */
    protected MediaWikiContainer (String name) {
        if (name.substring(name.length()-1).equals("\r"))
            name = name.substring(0, name.length()-1);
	this.containerName = name;
        page = new ArrayList<Object>();
    }
    
    protected String getName() {
        return containerName;
    }

    /**
     * Add an MediaWikiContainer object to this MediaWikiContainer's set of objects
     * @param con a MediaWikiContainer object
     */
    protected void add(MediaWikiContainer con) {
	page.add(con);
    }
    
    /**
     * Add an Element object to this MediaWikiContainer's set of objects
     * @param el 
     */
    protected void add(Element el) {
	page.add(el);
    }
    
    /**
     * If this MediaWikiContainer object corresponds to a "template" in the MediaWiki
     * markup, we call this method.
     * @param bracket a boolean saying if this MediaWikiContainer is a "template"
     */
    protected void bracketsHere(boolean bracket) {
        if (bracket)
            brackets = true;
    }
    
    /**
     * Prints a MediaWikiContainer object. Used for debugging.
     * @param indent number of indents
     */
    protected void printMediaWikiContainer(int indent) {
        System.out.print("--");
        System.out.print(this.containerName);
        System.out.println("--");
        
        indent++;
        
        for (int i = 0; i < page.size(); i++) {
            
            for (int k = 0; k < indent; k++) {
            System.out.print("  ");
        }
            if (page.get(i) instanceof Element)
                ((Element)(page.get(i))).print(indent);
            else if (page.get(i) instanceof MediaWikiContainer)
                ((MediaWikiContainer)(page.get(i))).printMediaWikiContainer(indent+1);
        }
    }
    
    /**
     * Converts a MediaWikiContainer object to XML
     * @param indent the number of indents
     * @return the XML representation of the MediaWikiContainer object
     */
    protected String saveToXML(int indent) {
        String toReturn = "<container name=\"" + containerName + "\" brackets=\"" + brackets + "\">";
        toReturn += '\r';
        
        for (int i = 0; i < page.size(); i++) {
            for (int k = 0; k < indent; k++) {
                toReturn += "   ";
            }
            if (page.get(i) instanceof Element) {
                toReturn += ((Element)(page.get(i))).saveToXML(indent);
            }
            else if (page.get(i) instanceof MediaWikiContainer) {
                toReturn += ((MediaWikiContainer)(page.get(i))).saveToXML(indent+1);
                toReturn += '\r';
            }
        }
        
        for (int k = 0; k < indent-1; k++) {
            toReturn += "   ";
        }
        toReturn += "</container>";
        return toReturn;
    }
    
    /**
     * Converts a MediaWikiContainer object to MediaWiki markup format
     * @return a MediaWiki markup representation of 
     */
    protected String outputToMediaWiki() {
        String toReturn = "";
        /* If this MediaWikiContainer object is a MediaWiki template, add brackets */
        if (brackets)
            toReturn = "{{" + containerName + '\r';
        else
            toReturn = containerName + "=";
        
        /* Iterate through all the objects in our set and add them to our string to return */
        for (int i = 0; i < page.size(); i++) {
            if (page.get(i) instanceof Element) {
                toReturn += ((Element)(page.get(i))).outputToMediaWiki();
            }
            else if (page.get(i) instanceof MediaWikiContainer) {
                if (brackets)
                    toReturn += "|";
                toReturn += ((MediaWikiContainer)(page.get(i))).outputToMediaWiki();
                if (!toReturn.substring(toReturn.length()-2).equals("}}"))
                    toReturn += '\r';
            }
        }
        
        if (brackets)
            toReturn += "}}";
        
        return toReturn;
    }
    
    /**
     * Iterate through all the elements on the page, and get all of the values associated
     * with the chosen element. (For example, if you want to get all of the "Example.Text"
     * values, run this method with "Example.Text" as the parameter).
     * @return String ArrayList of values
     */
    protected ArrayList<String> getElementValues(String elementName) {
        ArrayList<String> elementValues = new ArrayList<String>();
        for (int i = 0; i < page.size(); i++) {
            Object entry = page.get(i);
            if (entry instanceof Element) {
                String newElementName = ((Element)entry).getElementName();
                if ( newElementName.equals(elementName) )
                    elementValues.add(((Element)entry).getElementValue());
            } else if (entry instanceof MediaWikiContainer) {
                elementValues.addAll(((MediaWikiContainer)entry).getElementValues(elementName));
            }
        }
        return elementValues;
    }
    
    /**
     * Return this Linguistic Metaphor's Linguistic Source
     * @return 
     */
    protected String getLSource() throws Exception {
    	if (!containerName.trim().equals("Linguistic metaphor")) 
        	throw new Exception("This is not a Linguistic metaphor. Container name is: " + containerName);
       
        ArrayList<String> elementValues = new ArrayList<String>();
        for (int i = 0; i < page.size(); i++) {
            Object entry = page.get(i);
            if (entry instanceof Element) {
                String newElementName = ((Element)entry).getElementName();
                if ( newElementName.equals("Source") )
                    elementValues.add(((Element)entry).getElementValue());
            } else if (entry instanceof MediaWikiContainer) {
                elementValues.addAll(((MediaWikiContainer)entry).getElementValues("Source"));
            }
        }
        
        return elementValues.get(0);
       
    }
    
    /**
     * Return this Linguistic Metaphor's Linguistic Target
     * @return 
     */
    protected String getLTarget() throws Exception {
    	if (!containerName.trim().equals("Linguistic metaphor")) 
        	throw new Exception("This is not a Linguistic metaphor. Container name is: " + containerName);
    	
        ArrayList<String> elementValues = new ArrayList<String>();
        for (int i = 0; i < page.size(); i++) {
            Object entry = page.get(i);
            if (entry instanceof Element) {
                String newElementName = ((Element)entry).getElementName();
                if ( newElementName.equals("Target") )
                    elementValues.add(((Element)entry).getElementValue());
            } else if (entry instanceof MediaWikiContainer) {
                elementValues.addAll(((MediaWikiContainer)entry).getElementValues("Target"));
            }
        }
        return elementValues.get(0);
    }
    
    /* ---------------------------------------------------------------------- */
    /* Fixes! */
    /* ---------------------------------------------------------------------- */
    
    /**
     * Check that this metaphor has a metaphor alias corresponding with its title
     * @return 
     */
    protected void hasAlias(String containerTitle) {
        String compareAlias;
        if (containerTitle.substring(0,9).equals("Metaphor:"))
            compareAlias = containerTitle.substring(9);
        else
            return;
        ArrayList<String> aliases = this.getElementValues("Metaphor.Alias.Name");
        for (int i = 0; i < aliases.size(); i++) {
            if ( aliases.get(i).equals(compareAlias) )
                return;
        }
        
        MediaWikiContainer newContainer = new MediaWikiContainer("Metaphor.Alias");
        newContainer.bracketsHere(true);
        Element newElement = new Element("Metaphor.Alias.Name", containerTitle);
        newContainer.add(newElement);
        
        for (int i = 0; i < page.size(); i++) {
            Object entry = page.get(i);
            if (entry instanceof MediaWikiContainer && ((MediaWikiContainer)entry).containerName.equals("Aliases")) {
                ((MediaWikiContainer)entry).add(newContainer);
            }
        }
    }
    
    /**
     * Uncapitalize role names.
     */
    protected void uncapRoles() {
        for (int i = 0; i < page.size(); i++) {
            Object entry = page.get(i);
            if (entry instanceof Element && ((Element)entry).getElementName().equals("Role.Name")) {
                String roleName = ((Element)entry).getElementValue();
                roleName = roleName.substring(0,1).toLowerCase() + roleName.substring(1);
                ((Element)entry).setElementValue(roleName);
            } else if (entry instanceof MediaWikiContainer) {
                ((MediaWikiContainer)entry).uncapRoles();
            }
        }
    }
    
    /**
     * Fix Schema names so that they are separated by spaces, not underscores
     */
    protected void fixSchemaNames() {
        for (int i = 0; i < page.size(); i++) {
            Object entry = page.get(i);
            if (entry instanceof Element && ( ((Element)entry).getElementName().equals("Source schema") || ((Element)entry).getElementName().equals("Target schema") || ((Element)entry).getElementName().equals("Related schema.Name") )) {
                String schemaName = ((Element)entry).getElementValue();
                schemaName = schemaName.replaceAll("_", " ");
                ((Element)entry).setElementValue(schemaName);
            } else if (entry instanceof MediaWikiContainer) {
                ((MediaWikiContainer)entry).fixSchemaNames();
            }
        }
    }
    
}
