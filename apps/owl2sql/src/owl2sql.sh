#!/bin/sh
# ===================================================================
#
# Script for running owl2sql
#
# ===================================================================

MN_DIST_DIR=@@@DISTDIR@@@
MAIN_CLASS=edu.berkeley.icsi.metanet.owl2sql.Shell

CLASSPATH=$MN_DIST_DIR/lib/owl2sql.jar:$MN_DIST_DIR/lib/commons-cli-1.2.jar:$MN_DIST_DIR/lib/org.semanticweb.owl.owlapi.jar:$MN_DIST_DIR/lib/mysql-connector-java-5.1.22-bin.jar
export CLASSPATH

java -DentityExpansionLimit=1000000000 $MAIN_CLASS $@
