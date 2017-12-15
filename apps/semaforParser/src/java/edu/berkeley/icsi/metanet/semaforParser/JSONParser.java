package edu.berkeley.icsi.metanet.semaforParser;

public class JSONParser {
	
	/**
	 * Prepares the given string to be output as JSON data. Escapes unescaped 
	 * " and ' characters.
	 * @param string - the String to be prepared
	 * @return the prepared form of the input string
	 */
	public static String prepare(String str) {
		char[] chars = new char[2 * str.length()];
		int charInd = 0;
		char strChar;
		boolean escaped = false;
		
		for (int strInd = 0; strInd < str.length(); strInd++) {
			strChar = str.charAt(strInd);
			
			if ((strChar == '\"' || strChar == '\'') && !escaped) {
				chars[charInd] = '\\';
				charInd++;
			} else if (strChar == '\\' && !escaped) {
				escaped = true;
			} else {
				escaped = false;
			}
			
			chars[charInd] = strChar;
			charInd++;
		}
		
		return String.valueOf(chars).trim();
	}

	public static void main(String args[]) {
	}
}
