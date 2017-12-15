#!/bin/sh
# generate the input .txt files (csv format), for later import by importall.sh 
# case study input 
# update DSTAMP 
# SJD: modified to require $1 in format yyyymmdd
# added test logic
if [[ -z "$1" ]]; then
  echo "requires date parameter:  yyyymmdd"
  exit 1
else
  DSTAMP="$1"
fi
#iif [[ ( "$TEST" == "Y" ) && ( -z "$CASEONLY" ) ]]; then
# FILES="test"
#else
# FILES="all"
#fi

if [[ "$CASEONLY" == "Y" ]];then
./resetdbs.sh $DSTAMP
echo "resetting database for $DSTAMP"
fi

/bin/rm -f en*case-* es*case-* ru*case-* fa*case-*

nohup fastdbimport  --case-mode -v -l en -n $DSTAMP --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 --gen-only -d name encaseall.txt > encase-log.txt 2>&1 &
