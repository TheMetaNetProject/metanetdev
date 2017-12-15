package edu.berkeley.icsi.metanet.semaforParser;

import java.io.IOException;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;

/**
 * 
 * A class representing a semantic frame element.
 * @author brandon
 * 
 */
public class FrameElement {
	protected int start, end;
	protected String feName, content;
	
	protected FrameElement() {
	}
	
	protected FrameElement(String sentence, int start, int end, String name) {
		this.start = start;
		this.end = end;
		content = sentence.substring(start, end + 1);
		this.feName = name;
	}
	
	/**
	 * Constructs a frame element from the given JsonParser object.
	 * @param jp - JsonParser must be such that getCurrentToken() returns the
	 * start of the object. i.e. nextToken() must have been called at least once
	 * already.
	 * @throws IOException 
	 * @throws JsonParseException 
	 */
	protected FrameElement(JsonParser jp) 
			throws JsonParseException, IOException {
		String fieldname;
		
		if (jp.getCurrentToken() != JsonToken.START_OBJECT) {
			throw new JsonParseException("Invalid FrameElement JSON object", 
					null);
		}
		
		while (jp.nextToken() != JsonToken.END_OBJECT) {
			fieldname = jp.getCurrentName();
			jp.nextToken();
			
			if (fieldname.equals("start")) {
				start = jp.getValueAsInt();
			} else if (fieldname.equals("end")) {
				end = jp.getValueAsInt();
			} else if (fieldname.equals("content")){
				content = jp.getValueAsString();
			} else if (fieldname.equals("feName")) {
				feName = jp.getValueAsString();
			}
		}
	}
	
	/**
	 * Get the start and end indexes for the frame element. Can be used to
	 * extract the frame element content from the annotation set's sentence.
	 * @return a two-element array of the form [start, end]
	 */
	public int[] getIndexes() {
		int[] out = {start, end};
		return out;
	}
	
	/**
	 * Get the name of the frame element
	 * @return the name of the frame element
	 */
	public String getName() {
		return feName;
	}
	
	/**
	 * Get the content of the frame element
	 * @return the content of the frame element
	 */
	public String getContent() {
		return content;
	}

	public String toJSON() {
		return "{\"feName\":\"" + JSONParser.prepare(feName) + 
				"\", \"start\":" + start + 
				", \"end\":" + end + 
				", \"content\":\"" + JSONParser.prepare(content) + "\"}";
	}
	
	@Override
	public String toString() {
		return "<FrameElement | start: " + start + 
				", end: " + end + 
				", feName: " + feName + 
				", content: " + content + ">";
	}
	
	public static void main(String[] args) throws JsonParseException, IOException {
		FrameElement fe = new FrameElement("My name is \"Sam\", Sam I am, blah blah blah, ok done!", 1, 15, "imaframe");
		String json = fe.toJSON();
		System.out.println(fe);
		System.out.println(json);
		JsonParser jp = new JsonFactory().createJsonParser(json);
		jp.nextToken();
		System.out.println(new FrameElement(jp));
	}
}
