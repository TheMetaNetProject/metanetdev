#!/usr/bin/env sh
# This is the slurm run file for the SEMAFOR XML parser. If something isn't
# working, check the 'sfdir' variable below to see if it's pointing to 
# the semafor directory

sfdir=/u/framenet/aicorpus/semafor/semafor-semantic-parser
thisdir="$(dirname $(readlink -f ${0}))"
scriptdir=${thisdir}
basedir="$(dirname ${thisdir})"
tempdir="${basedir}/temp"
builddir="${basedir}/build"

if [ $# -lt 2 ]; then
    echo "Usage: "${0}" <input-file> <target-lemmas-file> [output-file]"
    exit 1
fi

inputFile="$(readlink -f ${1})"
targetLemmasFile="$(readlink -f ${2})"

if [ ! -f ${inputFile} ]; then
    echo "${0}: Couldn't find input file: ${1}"
    exit 1
fi

if [ ! -f ${targetLemmasFile} ]; then
	echo "${0}: Couldn't find target lemmas file: ${targetLemmasFile}"
	exit 1
fi

if [ $# -eq 3 ]; then
	touch ${3}
	outputFile="$(readlink -f ${3})"
	rm ${outputFile}
	touch ${outputFile}
else
	outputFile="${basedir}/$(basename ${inputFile}).json"
	touch ${outputFile}
	rm ${outputFile}
	touch ${outputFile}
fi

inputLines=$(wc -l ${inputFile} | cut -d ' ' -f 1)
targetLemmasLines=$(wc -l ${targetLemmasFile} | cut -d ' ' -f 1)

if [ ${inputLines} -ne ${targetLemmasLines} ]; then
	echo "${0}: input-file and target-lemmas-file must have the same number of lines"
	echo "${inputFile} has ${inputLines} lines"
	echo "${targetLemmasFile} has ${targetLemmasLines} lines"
	exit 1
fi

#srun -qK -I --mem-per-cpu 12000 -p ai ${sfdir}/release/fnParserDriver.sh "$@"
srun -qK -I -p ai --mem-per-cpu 20000 ${scriptdir}/metanet_fnParserDriver.sh ${1} ${tempdir} ${sfdir}

lemmaTagsFile="${tempdir}/temp.input.all.lemma.tags"
xmlFile="${tempdir}/temp.out"

if [ ! -f ${xmlFile} ]; then
	echo "${0}: Couldn't find the SEMAFOR XML output file: ${xmlFile}"
	exit 1
fi

if [ ! -f ${lemmaTagsFile} ]; then
	echo "${0}: Couldn't find the lemma tags temporary file: ${lemmaTagsFile}"
	exit 1
fi

cd ${builddir}
java edu.berkeley.icsi.metanet.semaforParser.XMLParser "${xmlFile}" "${targetLemmasFile}" "${lemmaTagsFile}" "${outputFile}"