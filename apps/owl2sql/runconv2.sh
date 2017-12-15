#!/bin/sh

./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db enmr -drop MR-EN-2013-04-19.xml
./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db enmr -simple MR-EN-2013-04-19.xml
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin enmr < specialtables.sql
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin enmr < update-tags-en.sql
/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt enmr > enmr_2013-04-19.sql

./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db esmr -drop MR-ES-2013-04-19.xml
./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db esmr -simple MR-ES-2013-04-19.xml
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin esmr < specialtables.sql
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin esmr < update-tags-es.sql
/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt esmr > esmr_2013-04-19.sql

./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db famr -drop MR-FA-2013-04-19.xml
./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db famr -simple MR-FA-2013-04-19.xml
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin famr < specialtables.sql
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin famr < update-tags-fa.sql
/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt famr > famr_2013-04-19.sql

./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db rumr -drop MR-RU-2013-04-19.xml
./owl2sql -server localhost -port 3306 -u mruser -p mrpw1 -db rumr -simple MR-RU-2013-04-19.xml
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin rumr < specialtables.sql
/u/metanet/tools/mysql64/bin/mysql --user=fnadmin rumr < update-tags-ru.sql
/u/metanet/tools/mysql64/bin/mysqldump --user=fnadmin --opt rumr > rumr_2013-04-19.sql
