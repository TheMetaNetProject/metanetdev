<?php

# enable debugging
error_reporting( -1 );
ini_set( 'display_errors', 1 );
$wgShowExceptionDetails = true;
$wgDebugToolbar = true;
$wgShowDebug = true;
#$wgDevelopmentWarnings = true;
$wgShowSQLErrors = true;
$wgDebugDumpSql  = true;
$wgShowDBErrorBacktrace = true;
$wgDebugLogFile = "/tscratch/tmp/httpd/logs/debug-{$wgDBname}.log";
