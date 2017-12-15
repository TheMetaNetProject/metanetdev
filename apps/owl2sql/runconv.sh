#!/bin/sh

##./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db enmr MR_English_2013-03-15P.owl
##/u/metanet/tools/mysql64/bin/mysql --user=fnadmin enmr < specialtables.sql
##/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt enmr > enmr_2013-03-15.sql

./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db esmr MR_Spanish_2013-03-15P.owl
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin esmr < specialtables.sql
/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt esmr > esmr_2013-03-15.sql

./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db famr MR_Persian_2013-03-15P.owl
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin famr < specialtables.sql
/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt famr > famr_2013-03-15.sql

./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db rumr MR_Russian_2013-03-15P.owl
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin rumr < specialtables.sql
/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt rumr > rumr_2013-03-15.sql
