#!/bin/sh
# SJD: modified to require $1 and $2 in format yyyymmdd
#  backup the database prior to the import
if [[ -z "$1" ]]; then
  echo "requires date parameter:  yyyymmdd from original run"
  exit 1
else 
  DSTAMP="$1"
fi
/bin/rm -f *-import-case-log.txt


echo "importing en case study"
fastdbimport --case-mode -l en -n $DSTAMP --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 -v --import-only -d name encaseall.txt > en-import-case-log.txt 2>&1
