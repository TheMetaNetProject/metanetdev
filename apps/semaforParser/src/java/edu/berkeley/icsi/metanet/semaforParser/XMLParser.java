package edu.berkeley.icsi.metanet.semaforParser;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.LinkedHashSet;
import java.util.Set;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

/**
 * Parses the XML output of SEMAFOR
 * @author brandon
 *
 */
public class XMLParser {
	private Set<SentenceAnnotation> sentenceAnnotations;
	private BufferedReader lemmaTagsReader, lemmasReader;
	private Document xmlDoc;
	
	/**
	 * Constructs an XML parser 
	 * @param xmlFile
	 * @param targetLemmaFile
	 * @param lemmaTagsFile
	 * @throws ParserConfigurationException
	 * @throws SAXException
	 * @throws IOException
	 */
	public XMLParser(File xmlFile, File targetLemmaFile, File lemmaTagsFile) {
		sentenceAnnotations = new LinkedHashSet<SentenceAnnotation>();
		try {
			lemmaTagsReader = new BufferedReader(new FileReader(lemmaTagsFile));
		} catch (FileNotFoundException e) {
			handleFileNotFoundException("lemma tags file", e);
		}		
		try {
			lemmasReader = new BufferedReader(
					new FileReader(targetLemmaFile));
		} catch (FileNotFoundException e1) {
			handleFileNotFoundException("target lemma file", e1);
		}
		try {
			xmlDoc = DocumentBuilderFactory.newInstance().newDocumentBuilder().
					parse(xmlFile);
		} catch (SAXException e) {
			e.printStackTrace();
			System.exit(1);
		} catch (IOException e) {
			handleIOException("XML file", e);
		} catch (ParserConfigurationException e) {
			e.printStackTrace();
			System.exit(1);
		}
		xmlDoc.getDocumentElement().normalize();
		parse();
	}

	/**
	 * Handles FileNotFoundException
	 * @param string
	 * @param e1
	 */
	private void handleFileNotFoundException(String string,
			FileNotFoundException e1) {
		System.err.println("Error: Could not find " + string);
		e1.printStackTrace();
		System.exit(1);
	}

	/**
	 * Parses the XML file and constructs an equivalent set of 
	 * SentenceAnnotation objects
	 */
	private Set<SentenceAnnotation> parse() {
		Node sentenceNode;
		Element sentenceElement;
		String targetLemma = null;
		String lemmaTags = null;
		String[] lemmaTagsTokens = null;
		SentenceAnnotation sa = null;
		
		// Iterate through the XML document's sentences
		NodeList sentenceNodeList = xmlDoc.getElementsByTagName("sentence");
		for (int i = 0; i < sentenceNodeList.getLength(); i++) {
			// Read in the next target lemma and the next line of annotations
			try {
				lemmaTags = lemmaTagsReader.readLine();
				lemmaTagsTokens = lemmaTags.split("\\s+");
			} catch (IOException e) {
				handleIOException("lemma annotation file", e);
			}
			try {
				targetLemma = lemmasReader.readLine().trim();
			} catch (IOException e) {
				handleIOException("target lemma file", e);
			}
			
			// Get the sentence node
			sentenceNode = sentenceNodeList.item(i);
			if (sentenceNode.getNodeType() != Node.ELEMENT_NODE) {
				continue;
			}
			
			// Get the text for the sentence
			sentenceElement = (Element) sentenceNode;
			sa = parseSentence(sentenceElement, sa, targetLemma, lemmaTagsTokens);
		}
		
		/*
		for (AnnotationSet AS : annotationSets) {
			System.out.println("Frame name: " + AS.getFrameName());
			System.out.println("Target: " + AS.getTarget());
			System.out.println("Sentence: " + AS.getSentence());
			System.out.println();
		}
		*/
		return sentenceAnnotations;
	}
	
	/**
	 * Handles IOException
	 * @param fileName
	 */
	private void handleIOException(String fileName, IOException e) {
		System.err.println("Error: Could not read in a line from " + fileName);
		System.exit(1);
	}

	/**
	 * Parses the given sentence for frames with the given target lemma,
	 * creates SentenceAnnotation objects for them, and adds them to the working
	 * set. Sequential sentence elements with the same sentence text will be 
	 * combined into a single SentenceAnnotation object.
	 * @param sentenceElement - XML sentence element
	 * @param prevSentenceAnnotation - the previous sentence annotation. Used
	 * to see if the previous sentence is the same.
	 * @param targetLemma - the target lemma (i.e. "bounce.v")
	 * @param lemmaTagsTokens - a String array representing the tokenized lemma 
	 * annotation corresponding to the given sentence
	 * @return the SentenceAnnotation object. This object has already been added
	 * to the annotationSets hashset
	 * @throws IOException
	 */
	private SentenceAnnotation parseSentence(Element sentenceElement, 
			SentenceAnnotation prevSentenceAnnotation, String targetLemma, 
			String[] lemmaTagsTokens) {
		String frameName, feName, targetLemmaStem, targetLemmaPoS;
		Element lmElement, targetLayerElement, feLayerElement, labelElement;
		NodeList lmElements, layerElementList, labelElementList;
		int start, end;
		LMAnnotation lm;
		SentenceAnnotation sa;
		
		String text = sentenceElement.getTextContent().trim();
		int sentenceID;
		
		if (prevSentenceAnnotation == null) {
			sentenceID = 1;
			sa = new SentenceAnnotation(sentenceID, text);
			sentenceAnnotations.add(sa);
		} else if (!text.equals(prevSentenceAnnotation.getText())) {
			sentenceID = prevSentenceAnnotation.getID() + 1;
			sa = new SentenceAnnotation(sentenceID, text);
			sentenceAnnotations.add(sa);
		}else {
			sa = prevSentenceAnnotation;
		}
		
		// Iterate through the sentence's LM annotation sets
		lmElements = sentenceElement.getElementsByTagName("annotationSet");
		for (int j = 0; j < lmElements.getLength(); j++) {
			// Get the annotation set element
			lmElement = (Element) lmElements.item(j);
			
			// Get the frame name
			frameName = lmElement.getAttribute("frameName");
			
			// Extract the two layers
			layerElementList = lmElement.getElementsByTagName("layer");
			targetLayerElement = (Element) layerElementList.item(0);
			feLayerElement = (Element) layerElementList.item(1);
			
			// Extract the target word
			labelElementList = targetLayerElement.getElementsByTagName(
					"label");
			labelElement = (Element) labelElementList.item(0);
			start = Integer.parseInt(labelElement.getAttribute("start"));
			end = Integer.parseInt(labelElement.getAttribute("end"));
			
			/*
			 * Skip this annotation set if word and target lemma don't
			 * match. Otherwise, add this LM to the sentence annotation
			 */
			if (!matchesLemma(text, start, end, targetLemma, 
					lemmaTagsTokens)) {
				continue;
			}
			lm = new LMAnnotation(text, frameName);
			String[] splitTargetLemma = targetLemma.split("\\.");
			targetLemmaStem = splitTargetLemma[0];
			targetLemmaPoS = splitTargetLemma[1];
			lm.setTarget(targetLemmaStem, start, end, targetLemmaPoS);
			
			// Iterate through and extract frame elements
			labelElementList = feLayerElement.getElementsByTagName("label");
			for (int l = 0; l < labelElementList.getLength(); l++) {
				labelElement = (Element) labelElementList.item(l);
				feName = labelElement.getAttribute("name");
				start = Integer.parseInt(labelElement.getAttribute("start"));
				end = Integer.parseInt(labelElement.getAttribute("end"));
				lm.addFrameElement(start, end, feName);
			}
			
			// Finalize and add to the sentence annotation
			lm.setSource();
			sa.addLM(lm);
		}
		return sa;
	}
	
	/**
	 * Determines whether or not the given subsection of the sentence matches
	 * the target lemma based on the lemma annotation file.
	 * @param sentence
	 * @param start
	 * @param end
	 * @param lemma
	 * @param lemmaTagsTokens - a String array representing the tokenized lemma 
	 * annotation corresponding to the given sentence
	 * @return
	 * @throws IOException
	 */
	private boolean matchesLemma(String sentence, int start, int end, 
			String lemma, String[] lemmaTagsTokens) {
		// Find number of words in the sentence. Includes punctuation.
		int numWords = sentence.split("\\s+").length;
		
		/*
		 * Find the index of the word in the sentence. Accounts for the random 
		 * number in front of the annotation line.
		 */
		int wordIndex = sentence.substring(0, end + 1).split("\\s+").length;
		
		/*
		 * Get part of speech. There seem to be multiple possible annotations
		 * for a sentence, but we'll take the first one.
		 */
		String POS = simplifyPOS(lemmaTagsTokens[wordIndex + numWords]);
		
		// Extract the lemma associated with the target word
		int lemmaAnnBeginIndex = 0;
		for (int i = numWords + 1; i < lemmaTagsTokens.length; i++) {
			if (lemmaTagsTokens[1].toLowerCase().startsWith(lemmaTagsTokens[i])) {
				lemmaAnnBeginIndex = i;
				break;
			}
		}
		String lemmaWord = lemmaTagsTokens[wordIndex + lemmaAnnBeginIndex - 1];
		String fullLemma = lemmaWord + "." + POS;
		
		/*
		String word = sentence.substring(start, end + 1);
		System.out.println("Sentence: " + sentence);
		System.out.println("Word: " + word);
		System.out.println("Index of word: " + wordIndex);
		System.out.println("Words in sentence: " + numWords);
		System.out.println("Extracted lemma word: " + lemmaWord);
		System.out.println("Simplifed POS: " + POS);
		System.out.println("Full lemma: " + lemma);
		System.out.println();
		*/
		
		return fullLemma.equals(lemma);
	}
	
	/**
	 * Simplifies the part of speech given by SEMAFOR to noun, verb, adj, etc.
	 * @param POS
	 * @return If the POS can be simplified, the simplified part of speech.
	 * Otherwise, the input. In both cases, the returned string lowercase.
	 */
	private String simplifyPOS(String POS) {
		POS = POS.toLowerCase();
		if (POS.startsWith("v")) {
			return "v";
		} else if (POS.startsWith("n")) {
			return "n";
		} else {
			return POS;
		}
	}
	
	/**
	 * Converts all this parser's sentence annotations to JSON
	 * @return JSON representation of this parser's sentence annotations
	 */
	public String toJSON() {
		String out = "[";
		for (SentenceAnnotation sa : sentenceAnnotations) {
			out += "\n\t" + sa.toJSON();
		}
		out += "\n]";
		return out;
	}
	
	/**
	 * Writes out all this parser's sentence annotations to a file
	 * @param file - the file to write to
	 * @throws IOException
	 */
	public void parseToFile(File file) throws IOException {
		BufferedWriter bw = new BufferedWriter(new FileWriter(file.getAbsolutePath()));
		for (SentenceAnnotation sa : sentenceAnnotations) {
			bw.append(sa.toJSON());
			bw.newLine();
		}
		
		bw.close();
	}
	
	public static void main(String args[]) throws IOException {
		File xmlFile = new File(args[0]);
		File targetLemmasFile = new File(args[1]);
		File lemmaTagsFile = new File(args[2]);
		File jsonOutputFile = new File(args[3]);
		XMLParser p = new XMLParser(xmlFile, targetLemmasFile, lemmaTagsFile);
		p.parseToFile(jsonOutputFile);
	}
}
