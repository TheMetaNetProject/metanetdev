LMS2 is primarily used within m4detect.  In that framework a json object is read-in and is modified with the extracted metaphors.  

To run the LMS2 system outside the m4detect, use the following command form:

python externalExtr.py inputfile

Reading in a *.json file, LMS2 processes and extract metaphors, sentence by sentence.  For each sentence the system first tries to use the parse trees inside the json.  If there is no parse tree in the input json, the system uses the Persian pipeline to POS tag and parse the sentence.  LMS2 generates a new json file with the following name format: lms2.inputfile and writes the resulting extracted metaphors.

=========================================================================
To run the Persian pipeline to parse a Persian sentence (in raw text form), use the following command form:
python raw2Parse.py < inputSentence > outputParseTree

The script reads in a Persian sentence in raw form from the standard input and output a parse tree into the standard output.  This script is useful for Luca's framework to generate new json files with better POS and parsing accuracy.
All of the parameter settings for the parser and model files are taking place within the script and there is no need for system paraemter setting outside the code.

