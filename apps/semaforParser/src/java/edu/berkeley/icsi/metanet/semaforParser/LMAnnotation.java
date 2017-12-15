package edu.berkeley.icsi.metanet.semaforParser;

import java.util.ArrayList;

/**
 * 
 * Java representation of SEMAFOR annotation set for a linguistic metaphor.
 * @author brandon
 *
 */
public class LMAnnotation {
	private String sentence, targetName, frameName, sourceName, seed;
	private int targetStart, targetEnd, sourceStart, sourceEnd;
	private ArrayList<FrameElement> frameElements = new ArrayList<FrameElement>();
	
	/**
	 * Constructs a new annotation set
	 * @param sentence - the sentence
	 * @param targetLemma - the target
	 * @param frameName - the frame name
	 */
	protected LMAnnotation(String sentence, String frameName) {
		this.sentence = sentence;
		this.frameName = frameName;
	}

	/**
	 * Adds a new frame element to the annotation set
	 * @param start - start index of the frame element
	 * @param end end - index of the frame element
	 * @param feName - the frame element name
	 */
	protected void addFrameElement(int start, int end, String feName) {
		frameElements.add(new FrameElement(sentence, start, end, feName));
	}
	
	/**
	 * Get the sentence associated with this annotation set
	 * @return the sentence
	 */
	public String getSentence() {
		return sentence;
	}
	
	/**
	 * Get the name of the linguistic target of this linguistic metaphor
	 * @return the target
	 */
	public String getTarget() {
		return targetName;
	}
	
	/**
	 * Get the frame name of the this annotation set
	 * @return the frame name
	 */
	public String getFrameName() {
		return frameName;
	}
	
	/**
	 * Get the frame elements of this annotation set
	 * @return a Set of frame elements
	 */
	public ArrayList<FrameElement> getFrameElements() {
		return frameElements;
	}
	
	/**
	 * Gets the name of the annotated linguistic metaphor, defined as the source
	 * and target stems concatenated with the same order as in the source 
	 * sentence
	 * @return the name of the linguistic metaphor
	 */
	public String getName() {
		if (sourceStart < targetStart) {
			return sourceName + " " + targetName;
		} else {
			return targetName + " " + sourceName;
		}
	}
	
	/**
	 * Sets information for the linguistic source of the linguistic metaphor. 
	 * Since SEMAFOR does not explicitly define the source of a LM,
	 * this method infers that the first frame element is the linguistic source.
	 * If this LMAnnotation has no frame elements, sets fields with default
	 * values (null for String fields and 0 for int fields)
	 */
	public void setSource() {
		if (frameElements.size() == 0) {
			return;
		}
		FrameElement firstFE = frameElements.get(0);
		sourceName = firstFE.content;
		sourceStart = firstFE.start;
		sourceEnd = firstFE.end;
	}
	
	/**
	 * Sets information about the linguistic target of this LM
	 * @param name - stem of the linguistic target
	 * @param start - start index of the target in the source sentence
	 * @param end - end index of the target the source sentence
	 * @param pos - part of speech of the linguistic target 
	 * (usually a verb i.e. "v")
	 */
	public void setTarget(String name, int start, int end, String pos) {
		targetName = name;
		targetStart = start;
		targetEnd = end;
	}
	
	/**
	 * Sets the LM seed of this seed
	 * @param seed - the name of the LM seed
	 */
	public void setSeed(String seed) {
		this.seed = seed;
	}
	
	/**
	 * Renders this AnnotationSet into a JSON object
	 * @return the JSON string representation of this AnnotationSet
	 */
	public String toJSON() {
		String name = getName();
		String sourceLemma = sourceName + "." + "n";
		String targetLemma = targetName + "." + "v";
		
		String json = "{\"name\": \"" + name + "\", " + 
				"\"target\": {\"lemma\": \"" + targetLemma + "\", \"start\": " + 
				targetStart + ", \"end\": " + targetEnd + 
				"}, \"source\": {\"lemma\": \"" + sourceLemma + 
				"\", \"start\": " + sourceStart + ", \"end\": " + sourceEnd +
				"}";
		
		if (seed != null) {
			json += ", \"seed\": \"" + seed + "\"";
		}
		
		json += "}";
		
		return json;
	}
	
	public static void main(String args[]) {
		System.out.println(new LMAnnotation("This is a sample sentence", "Framename").toJSON());
	}
	
}
