#!/bin/bash
for pagedump in `/bin/ls pageexport/*.xml`; do
    echo "importing $pagedump"
    php importDump.php $pagedump
done
