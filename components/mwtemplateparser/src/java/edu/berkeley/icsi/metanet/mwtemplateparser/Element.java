package edu.berkeley.icsi.metanet.mwtemplateparser;

/**
 * The Element class provides a one to one mapping from a 
 * String to a String or from a String to an instance of MediaWikiContainer.
 * 
 * For example:
 * ("Alias": "fooAlias") is a mapping between a String ("Alias") and a String ("fooAlias")
 * ("Aliases": setOfAliases) is a mapping between a String ("Aliases") and a MediaWikiContainer object (setOfAliases)
 * @author Jalal Buckley
 */
public class Element {
    /* the Element's Name */
    String elementName = "";
    /* the Element's Value */
    String elementValue = "";
    /* the Element's MediaWikiContainer object */
    MediaWikiContainer setOfObjects;
    
    /**
     * Create an Element object that is a mapping from a String to a String
     * @param name The Element's name
     * @param eVal The Element's value
     */
    protected Element (String name, String val) {
        this.elementName = name;
	this.elementValue = val;
    }
    
    /**
     * Create an Element object that is a mapping from a String to a MediaWikiContainer object
     * @param name The Element's name
     * @param con The Element's MediaWikiContainer 
     */
    protected Element (String name, MediaWikiContainer con) {
        this.elementName = name;
	this.setOfObjects = con;
    }
    
    /**
     * Get an Element object's elementValue
     * @param elementName
     * @return elementValue
     */
    protected String getElementValue() {
        return elementValue;
    }
    
    /**
     * Get an Element object's elementName
     * @param elementName
     * @return elementName
     */
    protected String getElementName() {
        return elementName;
    }
    
    /**
     * Set element value
     * @param value 
     */
    protected void setElementValue(String value) {
        elementValue = value;
    }
    
    /**
     * Prints out the contents of an Element object. Used for debugging purposes.
     * @param indent the number of indents
     */
    protected void print(int indent) {
        if (!elementValue.equals(""))
            System.out.println(elementName + ": " + elementValue);
        else if (setOfObjects != null) {
            System.out.println(elementName + ": ");
            setOfObjects.printMediaWikiContainer(indent+1);
        }
    } 
    
    /**
     * Converts an Element object to XML.
     * @param indent the number of indents
     * @return XML text
     */
    protected String saveToXML(int indent) {
        String toReturn = "";
        if (!elementValue.equals("")) {
            if (elementValue.substring(elementValue.length()-1).equals("\r"))
                elementValue = elementValue.substring(0,elementValue.length()-1);
            toReturn += "<element name=\"" + elementName + "\">" + elementValue + "</element>";
            toReturn += '\r';
        }
        else if (setOfObjects != null) {
            toReturn += "<template name=\"" + elementName + "\">" + setOfObjects.saveToXML(indent+1);
            toReturn += "</template>";
            //toReturn += '\r';
        }
        return toReturn;
    }
    
    /**
     * Converts an Element object to MediaWiki markup
     * @return MediaWiki markup
     */
    protected String outputToMediaWiki() {
        String toReturn = "";
        if (!elementValue.equals("")) {
            elementValue.replaceAll("|", "{{!}}");
            
            if (elementValue.substring(elementValue.length()-1).equals("\r"))
                elementValue = elementValue.substring(0,elementValue.length()-1);
            toReturn += "|" + elementName + "=" + elementValue;
            toReturn += '\r';
        }
        else if (setOfObjects != null) {
            toReturn += "|" + elementName + "=" + setOfObjects.outputToMediaWiki();
        }
        else {
            toReturn += "|" + elementName + "=" + '\r';
        }
        return toReturn;
    }
}
