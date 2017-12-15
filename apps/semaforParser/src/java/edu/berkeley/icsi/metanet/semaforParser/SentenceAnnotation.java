package edu.berkeley.icsi.metanet.semaforParser;

import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

/**
 * Java representation of the SEMAFOR annotation of one sentence. Contains
 * multiple linguistic metaphor "annotation sets".
 * @author brandon
 *
 */
public class SentenceAnnotation {
	private String text;
	private int id;
	private Set<LMAnnotation> lmSet = new HashSet<LMAnnotation>();
	
	/**
	 * Constructs a new SentenceAnnotation
	 * @param id - the unique sentence ID as defined by the SEMAFOR output
	 * @param text - the sentence text
	 */
	public SentenceAnnotation(int id, String text) {
		this.text = text;
		this.id = id;
	}
	
	/**
	 * Get the unique sentence ID as defined by the SEMAFOR output
	 * @return the sentence ID
	 */
	public int getID() {
		return id;
	}
	
	/**
	 * Get the sentence text
	 * @return the sentence text
	 */
	public String getText() {
		return text;
	}
	
	/**
	 * Adds a LM annotation to this sentence annotation's set of LM annotations
	 * @param lm - the LMAnnotation to add
	 */
	public void addLM(LMAnnotation lm) {
		if (lm != null) {
			lmSet.add(lm);
		}
	}
	
	/**
	 * Gets the iterator the sentence annotation's set of LM annotations
	 * @return - an LMAnnotation iterator
	 */
	public Iterator<LMAnnotation> getLMIterator() {
		return lmSet.iterator();
	}
	
	/**
	 * Returns the JSON representation of this sentence annotation
	 * @return JSON string
	 */
	public String toJSON() {
		String out = "{\"id\": " + id + ", " + 
				"\"text\": \"" + JSONParser.prepare(text) + "\", " +
				"\"lms\": [";
		
		Iterator<LMAnnotation> lmIter = lmSet.iterator();
		while (lmIter.hasNext()) {
			out += lmIter.next().toJSON();
			if (lmIter.hasNext()) {
				out += ", ";
			}
		}
		
		out += "]}";
		return out;
	}
}
