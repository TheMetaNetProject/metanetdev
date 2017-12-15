#!/bin/bash
# drop and recreate the metanetlm and gmr databases
# 9/11/14: changed from reset_gmr_sjd.sh to reset_gmr.sh
#          added FILE grant to enable LOAD DATA INFILE (without LOCAL)

export PATH=/u/metanet/tools/mysql64/bin:$PATH
if [[ -z $1 ]]
then
dstamp=`date +%Y%m%d`
else
dstamp="$1"
fi

metanetdbfile=/u/metanet/repository/mysql/metanetlm.sql

mndb="metanetlm_$dstamp"
echo "resetting database $mndb ..."
echo "DROP DATABASE IF EXISTS $mndb; CREATE DATABASE $mndb CHARACTER SET utf8 COLLATE utf8_bin;" | mysql -u mnadmin
cat $metanetdbfile | mysql -u mnadmin $mndb
echo "GRANT ALL ON $mndb.* TO 'mdbuser'@'localhost';" | mysql -u mnadmin mysql
echo "GRANT FILE ON *.* TO 'mdbuser'@'localhost';" | mysql -u mnadmin mysql
echo "GRANT SELECT ON $mndb.* TO 'readonly_user'@'localhost';" | mysql -u mnadmin mysql

cd /u/metanet/repository/gmrdumps
./reset_gmr.sh "icsi_gmr_$dstamp"

#icsigmrfile=/u/metanet/repository/gmrdumps/icsi_gmr_31_dump.sql
#altergmrfile=/u/metanet/repository/gmrdumps/alter_gmr_31.sql

#gmrdb="icsi_gmr_$dstamp"
#echo "reseting database $gmrdb ..."
#echo "DROP DATABASE IF EXISTS $gmrdb; CREATE DATABASE $gmrdb CHARACTER SET utf8 COLLATE utf8_general_ci;" | mysql -u mnadmin
#cat $icsigmrfile | mysql -u mnadmin $gmrdb
#cat $altergmrfile | mysql -u mnadmin $gmrdb
#echo "GRANT ALL ON $gmrdb.* TO 'gmruser'@'localhost';" | mysql -u mnadmin mysql
