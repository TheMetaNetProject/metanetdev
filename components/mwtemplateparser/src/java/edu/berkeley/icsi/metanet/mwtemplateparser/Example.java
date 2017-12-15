package edu.berkeley.icsi.metanet.mwtemplateparser;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * An Example class used to show the functionality of the MediaWikiParse class.
 * @author Jalal Buckley
 */
public class Example {
    /**
     * This class demonstrates functionality of the MediaWikiContainer class
     */
    public static void main(String args[]) {
        /* Load in two different pages from text files. */
        String page1Contents = fileGenerator("input1.txt");
        String page2Contents = fileGenerator("input2.txt");
        String page3Contents = fileGenerator("input3.txt");
        String page4Contents = fileGenerator("input4.txt");
        /* Give these files titles */
        String page1 = "Metaphor:MORALITY IS STRAIGHTNESS";
        String page2 = "Metaphor:FREEDOM OF ACTION IS THE LACK OF IMPEDIMENTS TO MOVEMENT";
        String page3 = "Linguistic metaphor:Address barrier";
        String page4 = "Schema:Seeing";
        
        /* Create a new MediaWikiParse object */
        MediaWikiParse newParser = new MediaWikiParse();
        /* Read page1Contents, page2Contents, and page3Contents into memory */
        newParser.parseAndSave(page1, page1Contents);
        newParser.parseAndSave(page2, page2Contents);
        newParser.parseAndSave(page3, page3Contents);
        newParser.parseAndSave(page4, page4Contents);
           
        /* ------------------------------------------------------------------ */
        /* (1) Get Linguistic Source and Linguistic Target */
        /* ------------------------------------------------------------------ */
        /* We have to run this using a try and catch because there may not be
         * a linguistic source or linguistic target on the page.
         */
        try {
            String linguisticSource = newParser.getLingSource(page3);
            String linguisticTarget = newParser.getLingTarget(page3);
            
            System.out.println("Linguistic Source: " + linguisticSource);
            System.out.println("Linguistic Target: " + linguisticTarget);
        } catch (Exception ex) {
            Logger.getLogger(Example.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        /* ------------------------------------------------------------------ */
        /* (2) Get the Example Texts */
        /* ------------------------------------------------------------------ */
        ArrayList<String> elements = newParser.getExampleTexts(page3);
        System.out.println("Example Texts: ");
        for (int i = 0; i < elements.size(); i++) {
            System.out.print("  ");
            System.out.println(elements.get(i));
        }
        
        /* ------------------------------------------------------------------ */
        /* (3) Getting all the values associated with a certain element */
        /*   - For example, find all of the Entailment Inferences       */
        /* ------------------------------------------------------------------ */
        ArrayList<String> newElements = newParser.getTheElementValues(page2, "Entailment.Source inference");
        System.out.println("Entailment Inferences: ");
        for (int i = 0; i < newElements.size(); i++) {
            System.out.print("  ");
            System.out.println(newElements.get(i));
        }
        
        System.out.println();
        System.out.println();
        
        /* ------------------------------------------------------------------ */
        /* (4) Perform fixes */
        /* ------------------------------------------------------------------ */
        /* Find more detail about each fix under the MediaWikiParse class.
         */
        newParser.aliasCheck(page2);
        newParser.fixSchema(page2);
        newParser.uncapitalizeRoles(page4);
        
        /* ------------------------------------------------------------------ */
        /* (5) Print the contents of a page in order to debug */
        /* ------------------------------------------------------------------ */
        newParser.printContentsOfPage(page1);
    }
    
        /**
     * Method for reading text from a file. Taken from Stack Overflow.
     * @param fileName
     * @return text from file
     */
    public static String fileGenerator(String fileName) {   
        String toReturn = "";
        try {
            String currentDirectory = System.getProperty("user.dir");
            System.out.println(currentDirectory);
            String inputFileName = currentDirectory+"/src/java/edu/berkeley/icsi/metanet/mwtemplateparser/"+fileName;
            File inputFile = new File(inputFileName);
            System.out.println(inputFile.getAbsolutePath());
            FileReader inputFileReader = new FileReader(inputFile);
            Scanner input = new Scanner(inputFileReader);
            while(input.hasNext()) {
                toReturn += input.nextLine(); 
                toReturn += '\r';
            }
        }  catch (Exception e) { 
            e.printStackTrace();
        }
        return toReturn;
    }
}
