package edu.berkeley.icsi.metanet.neo4j;

import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.Label;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.PosixParser;

import java.io.*;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.Path;


public class MetaNetWikiLoader {
	private static final Logger logger = Logger.getLogger("MetaNetWikiLoader");
	public static void main (String [] args) throws IOException{
		/*
         * Takes 3 arguments: a language abbreviation, the path to the database and the input file
         */
		String lang = args[0];
		String dbpathstr = args[1];
		String inputFile = args[2];

		Level logLevel = Level.SEVERE;
        logger.setLevel(logLevel);
                
		// access the neo4j database
		GraphDatabaseService graphDb = new GraphDatabaseFactory().newEmbeddedDatabase(dbpathstr);
		registerShutdownHook( graphDb );
		try {
			
			Transaction tx = graphDb.beginTx();
			
			HashMap<String,Node> wikiNodes = new HashMap<String,Node>();
			
			// open the file of nodes and edges
			File wikiInfoFile = new File(inputFile);
			BufferedReader reader = new BufferedReader(new FileReader(wikiInfoFile));
			String text;
		    while ((text = reader.readLine()) != null) {
		    	String [] textEntries = text.split("#");
		    	
		    	// build lu nodes
		        if (textEntries[0].equals("lu_node")) {
		        	Node newNode = graphDb.createNode();
		        	newNode.setProperty("name", textEntries[1]);
		        	newNode.setProperty("lemma", textEntries[2]);
		        	newNode.setProperty("lang", lang);
		        	newNode.addLabel(NodeLabels.LexicalUnit);
		        	wikiNodes.put(textEntries[1],newNode);
		        }
		        
		        // build schema nodes
		        if (textEntries[0].equals("frame_node")) {
		        	Node newNode = graphDb.createNode();
		        	newNode.setProperty("name", textEntries[1]);
		        	newNode.setProperty("label", textEntries[2]);
		        	newNode.setProperty("lang", lang);
		        	newNode.addLabel(NodeLabels.Frame);
		        	wikiNodes.put(textEntries[1],newNode);
		        }
		        
		        // build metaphor nodes
		        if (textEntries[0].equals("metaphor_node")) {
		        	Node newNode = graphDb.createNode();
		        	newNode.setProperty("name", textEntries[1]);
		        	newNode.setProperty("label", textEntries[2]);
		        	newNode.setProperty("lang", lang);
		        	newNode.addLabel(NodeLabels.Metaphor);
		        	wikiNodes.put(textEntries[1],newNode);
		        }
		        
		        // add edges
		        if (textEntries[0].equals("edge")) {
		        	Relationship newRelationship;
		        	Node outNode = wikiNodes.get(textEntries[4]);
		        	Node inNode = wikiNodes.get(textEntries[3]);
		        	String edgeLabel = textEntries[5];
		        	RelationshipType rt ;
		        	if (edgeLabel.equals("hasLexicalUnit")) {
		        		rt = RelTypes.hasLU;
		        	} else if (edgeLabel.equals("hasTargetFrame")){
		        		rt = RelTypes.hasTargetFrame;
		        	} else if (edgeLabel.equals("hasSourceFrame")){
		        		rt = RelTypes.hasSourceFrame;
		        	} else if (edgeLabel.equals("isSubcaseOfFrame")) {
		        		rt = RelTypes.isSubcaseOfFrame;
		        	} else if (edgeLabel.equals("isEntailedByMetaphor")) {
		        		rt = RelTypes.isEntailedByMetaphor;
		        	} else if (edgeLabel.equals("makesUseOfMetaphor")) {
		        		rt = RelTypes.makesUseOfMetaphor;
		        	} else if (edgeLabel.equals("makesUseOfFrame")) {
		        		rt = RelTypes.makesUseOfFrame;
		        	}
		        	else {
		        		rt = RelTypes.wikiEdge;
		        	}
		        	newRelationship = outNode.createRelationshipTo(inNode,rt);
		        	newRelationship.setProperty("edgeLabel", textEntries[5]);
		        	newRelationship.setProperty("lang", lang);
		        	logger.info("edge created!");
		        }
		    }
			reader.close();
			//Node firstNode = graphDb.createNode();
			//Node secondNode = graphDb.createNode();
			//firstNode.setProperty( "message", "Hello, " );
			//secondNode.setProperty( "message", "World!" );
			//Relationship relationship = firstNode.createRelationshipTo( secondNode, RelTypes.KNOWS );
			//relationship.setProperty( "message", "brave Neo4j " );
			
		    
			tx.success();
		    tx.finish();
		    tx.close();
			
		} catch (Exception e) {
			logger.severe("Error with transaction!");
		}
		
	}
	
	private static void registerShutdownHook (final GraphDatabaseService graphDb ) {
		Runtime.getRuntime().addShutdownHook(new Thread()
		{
			@Override
			public void run()
			{
				graphDb.shutdown();
				System.out.println("used shut down hook.");				
			}
		} );
	}
	
	private static enum RelTypes implements RelationshipType
	{
		wikiEdge,
		hasLU,
		hasTargetFrame,
		hasSourceFrame,
		isSubcaseOfFrame,
		isEntailedByMetaphor,
		makesUseOfMetaphor,
		makesUseOfFrame
		
	}
	
	private static enum NodeLabels implements Label
	{
		LexicalUnit,
		Frame,
		Metaphor
		
	}

}
