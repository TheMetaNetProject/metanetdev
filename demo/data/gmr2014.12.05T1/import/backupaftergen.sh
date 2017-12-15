#!/bin/sh

# ======================================================================
# Backup icsi_gmr database after genall.sh, prior to importall.sh
#   (cm_source and cm_target tables populated)
# ======================================================================

umask 0002

export PATH=/u/metanet/tools/mysql64/bin:$PATH

DSTAMP="$1"

GMRDBNAME="icsi_gmr_$DSTAMP"
GMRDBNAMEBAK="aftergen_$GMRDBNAME"

# create/re-create the database
echo "DROP DATABASE IF EXISTS $GMRDBNAMEBAK; CREATE DATABASE $GMRDBNAMEBAK CHARACTER SET utf8 COLLATE utf8_general_ci;" | mysql -u mnadmin

# make a copy of the database
mysqldump -u mnadmin $GMRDBNAME | mysql -u mnadmin $GMRDBNAMEBAK
