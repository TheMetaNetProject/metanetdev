#!/bin/sh
# SJD: modified to require $1 and $2 in format yyyymmdd
#  backup the database prior to the import
if [[ -z "$1" ]]; then
  echo "requires date parameter:  yyyymmdd from original run"
  exit 1
else 
  DSTAMP="$1"
fi
/bin/rm -f *-import-log.txt

./backupaftergen.sh $DSTAMP

echo "importing en"
fastdbimport -l en --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 -v --import-only -d provenance -n $DSTAMP enall.txt > en-import-log.txt 2>&1
echo "importing es"
fastdbimport -l es --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 -v --import-only -d provenance -n $DSTAMP esall.txt > es-import-log.txt 2>&1
echo "importing ru"
fastdbimport -l ru --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 -v --import-only -n $DSTAMP ruall.txt > ru-import-log.txt 2>&1
echo "importing fa"
fastdbimport -l fa --mdb-name metanetlm_$DSTAMP --mdb-pw not4iarpa! --gdb-name icsi_gmr_$DSTAMP --gdb-pw iarpam4 -v --import-only -n $DSTAMP faall.txt > fa-import-log.txt 2>&1

