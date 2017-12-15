package edu.berkeley.icsi.metanet.metalookup;

public class Frame {
	
	private String lexicalUnit;
	private String frameName;
	
	public String getLexicalUnit() { return lexicalUnit; }
	public String getName() { return frameName; }
	
	public void setLexicalUnit(String lu) { 
		lexicalUnit = lu;
	}
	
	public void setName(String name) {
		frameName = name;
	}

	public String toString() {
		return "This is LexUnit: " + lexicalUnit + " in Frame: " + frameName;
	}
	
}
