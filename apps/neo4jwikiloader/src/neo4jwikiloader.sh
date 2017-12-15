#!/bin/sh
# ===================================================================
#
# Script for running neo4jwikiloader
#
# This script must run on the server that hosts neo4j
#
# ===================================================================

MN_DIST_DIR=@@@DISTDIR@@@
MAIN_CLASS=edu.berkeley.icsi.metanet.neo4j.MetaNetWikiLoader
NEO4J_HOME=${NEO4J_HOME:-"/xa/metanet/services/neo4j"}

CLASSPATH=$MN_DIST_DIR/lib/neo4jwikiloader.jar:$MN_DIST_DIR/lib/commons-cli-1.2.jar:$NEO4J_HOME/lib/*
export CLASSPATH

java $MAIN_CLASS $@
