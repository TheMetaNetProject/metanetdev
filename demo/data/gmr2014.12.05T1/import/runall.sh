#!/bin/sh
# create the input .txt files and import them directly into the database
#   equivalent to genall.sh followed by importall.sh
# SJD: modified to require $1 in format yyyymmdd
if [[ -z "$1" ]]; then
  echo "requires date parameter:  yyyymmdd"
  exit 1
else
  DSTAMP="$1"
fi

./resetdbs.sh $DSTAMP
/bin/rm -f en-* es-* ru-* fa-*

nohup fastdbimport -v -l en --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4  -d provenance enall.txt > en-log.txt 2>&1 &
nohup fastdbimport -v -l es --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4  -d provenance esall.txt > es-log.txt 2>&1 &
nohup fastdbimport -v -l ru --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4  ruall.txt > ru-log.txt 2>&1 &
nohup fastdbimport -v -l fa --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4  faall.txt > fa-log.txt 2>&1 &
