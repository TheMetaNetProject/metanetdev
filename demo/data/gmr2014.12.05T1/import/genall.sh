#!/bin/sh
# generate the input .txt files (csv format), for later import by importall.sh 
# update DSTAMP 
# SJD: modified to require $1 in format yyyymmdd
# added test logic
if [[ -z "$1" ]]; then
  echo "requires date parameter:  yyyymmdd"
  exit 1
else
  DSTAMP="$1"
fi
if [[ "$TEST" == "Y" ]];then
 FILES="test"
else
 FILES="all"
fi


./resetdbs.sh $DSTAMP
/bin/rm -f en-* es-* ru-* fa-*

nohup fastdbimport -v -l en --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 --gen-only -n $DSTAMP -d provenance en${FILES}.txt > en-log.txt 2>&1 &
nohup fastdbimport -v -l es --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 --gen-only -n $DSTAMP -d provenance es${FILES}.txt > es-log.txt 2>&1 &
nohup fastdbimport -v -l ru --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 --gen-only -n $DSTAMP ru${FILES}.txt > ru-log.txt 2>&1 &
nohup fastdbimport -v -l fa --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 --gen-only -n $DSTAMP fa${FILES}.txt > fa-log.txt 2>&1 &
