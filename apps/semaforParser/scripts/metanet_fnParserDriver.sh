#!/bin/bash
#    The driver script for SEMAFOR.
#    Written by Dipanjan Das (dipanjan@cs.cmu.edu)
#	 Modified by Brandon Thai (bgthai@icsi.berkeley.edu)
#    with suggestions from Thomas Kleinbauer (thomas.kleinbauer@dfki.de)
#    Copyright (C) 2011
#    Dipanjan Das
#    Language Technologies Institute, Carnegie Mellon University
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

if [ $# != 3 ]; then
   echo "USAGE: `basename "${0}"` <input-file><temp-dir><semafor-semantic-parser-dir>"
   exit 1
fi

source ${3}/release/config

# $3: location of line split file, must be absolute path
INPUT_FILE=`readlink -f "${1}"`

# Sets and clears out temp directory. Should be in same directory as 
# semafor_xml_parser
TEMP_DIR=`readlink -f "${2}"`

if [ ! -d "${TEMP_DIR}" ]; then
	mkdir "${TEMP_DIR}"
else
	rm -f "${TEMP_DIR}/temp.*"
fi

# output of FN parser
OUTPUT_FILE="${TEMP_DIR}/temp.out"

CLEAN_INPUT=${TEMP_DIR}/temp.input
grep -v '^\s*$' ${INPUT_FILE} > ${CLEAN_INPUT}
INPUT_FILE=${CLEAN_INPUT}


CLASSPATH=".:${SEMAFOR_HOME}/lib/semafor-deps.jar"

if [ "${GOLD_TARGET_FILE}" == "null" ]
then
    echo "**********************************************************************"
    echo "Tokenizing file: ${INPUT_FILE}"
    sed -f ${SEMAFOR_HOME}/scripts/tokenizer.sed ${INPUT_FILE} > ${INPUT_FILE}.tokenized
    echo "Finished tokenization."
    echo "**********************************************************************"
    echo
    echo
else
    echo "**********************************************************************"
    echo "Gold target file provided, not tokenizing input file."
    cat ${INPUT_FILE} > ${INPUT_FILE}.tokenized
    echo "**********************************************************************"
    echo 
    echo
fi

echo "**********************************************************************"
echo "Part-of-speech tagging tokenized data...."
rm -f ${INPUT_FILE}.pos.tagged
cd ${SEMAFOR_HOME}/scripts/jmx
./mxpost tagger.project < ${INPUT_FILE}.tokenized > ${INPUT_FILE}.pos.tagged
echo "Finished part-of-speech tagging."
echo "**********************************************************************"
echo
echo

if [ "$MST_MODE" != "server" ]
then
    echo "**********************************************************************"
    echo "Preparing the input for MST Parser..."
    cd ${SEMAFOR_HOME}
    ${JAVA_HOME_BIN}/java \
	-classpath ${CLASSPATH} \
	edu.cmu.cs.lti.ark.fn.data.prep.CoNLLInputPreparation \
	${INPUT_FILE}.pos.tagged ${INPUT_FILE}.conll.input

    echo "Dependency parsing the data..."
    cd ${MST_PARSER_HOME}
    ${JAVA_HOME_BIN}/java -classpath ".:./lib/trove.jar:./lib/mallet-deps.jar:./lib/mallet.jar" \
	-d64 -Xms8g -Xmx8g mst.DependencyParser \
	test separate-lab \
	model-name:${MODEL_DIR}/wsj.model \
	decode-type:proj order:2 \
	test-file:${INPUT_FILE}.conll.input \
	output-file:${INPUT_FILE}.conll.output \
	format:CONLL
    echo "Finished dependency parsing."
    echo "**********************************************************************"
    echo
    echo
fi

if [ "${AUTO_TARGET_ID_MODE}" == "relaxed" ]
then 
    RELAXED_FLAG=yes
else
    RELAXED_FLAG=no
fi


if [ "${USE_GRAPH_FILE}" == "yes" ]
then
    GRAPH_FILE=${MODEL_DIR}/sparsegraph.gz
else
    GRAPH_FILE=null
fi

ALL_LEMMA_TAGS_FILE=${INPUT_FILE}.all.lemma.tags


echo "**********************************************************************"
echo "Performing frame-semantic parsing"
cd ${SEMAFOR_HOME}
${JAVA_HOME_BIN}/java \
    -classpath ${CLASSPATH} \
    -d64 -Xms4g -Xmx4g \
    edu.cmu.cs.lti.ark.fn.parsing.ParserDriver \
    mstmode:${MST_MODE} \
    mstserver:${MST_MACHINE} \
    mstport:${MST_PORT} \
    posfile:${INPUT_FILE}.pos.tagged \
    test-parsefile:${INPUT_FILE}.conll.output \
    stopwords-file:${SEMAFOR_HOME}/stopwords.txt \
    wordnet-configfile:${SEMAFOR_HOME}/file_properties.xml \
    fnidreqdatafile:${MODEL_DIR}/reqData.jobj \
    goldsegfile:${GOLD_TARGET_FILE} \
    userelaxed:${RELAXED_FLAG} \
    testtokenizedfile:${INPUT_FILE}.tokenized \
    idmodelfile:${MODEL_DIR}/idmodel.dat \
    alphabetfile:${MODEL_DIR}/parser.conf \
    framenet-femapfile:${MODEL_DIR}/framenet.frame.element.map \
    eventsfile:${INPUT_FILE}.events.bin \
    spansfile:${INPUT_FILE}.spans \
    model:${MODEL_DIR}/argmodel.dat \
    useGraph:${GRAPH_FILE} \
    frameelementsoutputfile:${INPUT_FILE}.fes \
    alllemmatagsfile:${ALL_LEMMA_TAGS_FILE} \
    requiresmap:${MODEL_DIR}/requires.map \
    excludesmap:${MODEL_DIR}/excludes.map \
    decoding:${DECODING_TYPE}

end=`wc -l ${INPUT_FILE}.tokenized`
end=`expr ${end% *}`
echo "Producing final XML document:"
${JAVA_HOME_BIN}/java -classpath ${CLASSPATH} \
    -d64 -Xms4g -Xmx4g \
    edu.cmu.cs.lti.ark.fn.evaluation.PrepareFullAnnotationXML \
    testFEPredictionsFile:${INPUT_FILE}.fes \
    startIndex:0 \
    endIndex:${end} \
    testParseFile:${ALL_LEMMA_TAGS_FILE} \
    testTokenizedFile:${INPUT_FILE}.tokenized \
    outputFile:${OUTPUT_FILE}


echo "Finished frame-semantic parsing."
echo "**********************************************************************"
echo
echo
