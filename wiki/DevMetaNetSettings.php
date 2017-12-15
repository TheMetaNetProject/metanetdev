<?php
/**
 * MetaNet Development Site-wide Configuration Settings
 *
 */

# set server url
$wgServer = "__WGSERVER_URL__";

# raise memory limit
$wgMemoryLimit = "512M";

# opcode and object caching
$wgMainCacheType = CACHE_ACCEL;

# output HTML caching
$wgUseFileCache = true; /* default: false */
$wgFileCacheDirectory = "$IP/cache/html";
$wgShowIPinHeader = false;

# localisation caching
$wgCacheDirectory = "$IP/cache/local";

# ICSI logo
$wgLogo 	= "$wgScriptPath/icsi_logo_135b.jpg";

# Query string length limit for ResourceLoader. You should only set this if
# your web server has a query string length limit (then set it to that limit),
# or if you have suhosin.get.max_value_length set in php.ini (then set it to
# that value)
$wgResourceLoaderMaxQueryLength = -1;

# Make external links open in separate tab
$wgExternalLinkTarget = '_blank';

# Default permissions for anonymous users: read, but not edit
# This is because this wiki is accessible only on ICSI subnet anyway
$wgGroupPermissions['*']['createaccount'] = false;
$wgGroupPermissions['*']['edit'] = false;
$wgGroupPermissions['*']['createpage'] = false;
$wgGroupPermissions['*']['writeapi'] = false;
$wgGroupPermissions['*']['patrolmarks']= false;

# Create an analyst group that has edit privileges
$wgGroupPermissions['analyst'] = $wgGroupPermissions['user'];
$wgGroupPermissions['analyst']['edit'] = true;
$wgGroupPermissions['analyst']['move'] = true;
$wgGroupPermissions['analyst']['delete'] = true;
$wgGroupPermissions['analyst']['undelete']= true;
$wgGroupPermissions['analyst']['rollback']= true;
$wgGroupPermissions['analyst']['patrol']= true;
$wgGroupPermissions['analyst']['suppressredirect'] = true;
$wgGroupPermissions['analyst']['deletedtext'] = true;
$wgGroupPermissions['analyst']['deleterevision'] = true;
$wgGroupPermissions['analyst']['deletedhistory'] = true;

# NOTE: default 'user' permissions group will be altered to be
#       read-only for all but the admin wiki.  See section below on
#       customizations for the Admin Wiki.

# Specify who can edit: true means only logged in users may edit pages
$wgWhitelistEdit = true;

# Specify who may create new accounts: 0 means no, 1 means yes. Allow
# analysts to create accounts.
$wgWhitelistAccount = array ( 'user' => 0, 'analyst' => 1,
                              'sysop' => 1, 'developer' => 1 );

# Add more configuration options below.

# Number of items in a category shown per page
$wgCategoryPagingLimit = 500;

# Create custom namespaces
define("NS_EVENT", 500);
define("NS_EVENT_TALK", 501);
$wgExtraNamespaces[NS_EVENT] = "Event";
$wgExtraNamespaces[NS_EVENT_TALK] = "Event_talk";

define("NS_GLOSSARY", 502);
define("NS_GLOSSARY_TALK", 503);
$wgExtraNamespaces[NS_GLOSSARY] = "Glossary";
$wgExtraNamespaces[NS_GLOSSARY_TALK] = "Glossary_talk";

define("NS_METAPHOR", 550);
define("NS_METAPHOR_TALK", 551);
$wgExtraNamespaces[NS_METAPHOR] = "Metaphor";
$wgExtraNamespaces[NS_METAPHOR_TALK] = "Metaphor_talk";

define("NS_FRAME", 552);
define("NS_FRAME_TALK", 553);
$wgExtraNamespaces[NS_FRAME] = "Frame";
$wgExtraNamespaces[NS_FRAME_TALK] = "Frame_talk";

define("NS_METAPHORFAMILY", 554);
define("NS_METAPHORFAMILY_TALK", 555);
$wgExtraNamespaces[NS_METAPHORFAMILY] = "Metaphor_family";
$wgExtraNamespaces[NS_METAPHORFAMILY_TALK] = "Metaphor_family_talk";

define("NS_FRAMEFAMILY", 556);
define("NS_FRAMEFAMILY_TALK", 557);
$wgExtraNamespaces[NS_FRAMEFAMILY] = "Frame_family";
$wgExtraNamespaces[NS_FRAMEFAMILY_TALK] = "Frame_family_talk";

define("NS_LINGMETAPHOR", 558);
define("NS_LINGMETAPHOR_TALK", 559);
$wgExtraNamespaces[NS_LINGMETAPHOR] = "Linguistic_metaphor";
$wgExtraNamespaces[NS_LINGMETAPHOR_TALK] = "Linguistic_metaphor_talk";

define("NS_CXSTANALYSIS", 560);
define("NS_CXSTANALYSIS_TALK", 561);
$wgExtraNamespaces[NS_CXSTANALYSIS] = "Construct_analysis";
$wgExtraNamespaces[NS_CXSTANALYSIS_TALK] = "Construct_analysis_talk";

define("NS_CXNMP", 562);
define("NS_CXNMP_TALK", 563);
$wgExtraNamespaces[NS_CXNMP] = "CxnMP";
$wgExtraNamespaces[NS_CXNMP_TALK] = "CxnMP_talk";

define("NS_METARC", 564);
define("NS_METARC_TALK", 565);
$wgExtraNamespaces[NS_METARC] = "MetaRC";
$wgExtraNamespaces[NS_METARC_TALK] = "MetaRC_talk";

define("NS_ICONCEPT", 570);
define("NS_ICONCEPT_TALK", 571);
$wgExtraNamespaces[NS_ICONCEPT] = "IConcept";
$wgExtraNamespaces[NS_ICONCEPT_TALK] = "IConcept_talk";

# Custom name spaces for BibManager Extension
define("NS_CITATION", 800);
define("NS_CITATION_TALK", 801);
$wgExtraNamespaces[NS_CITATION] = "Cit";
$wgExtraNamespaces[NS_CITATION_TALK] = "Cit_talk";

# Search behavior wrt to the namespaces
$wgNamespacesToBeSearchedDefault[NS_EVENT] = true;
$wgNamespacesToBeSearchedDefault[NS_GLOSSARY] = true;
$wgNamespacesToBeSearchedDefault[NS_METAPHOR] = true;
$wgNamespacesToBeSearchedDefault[NS_METAPHORFAMILY] = true;
$wgNamespacesToBeSearchedDefault[NS_FRAME] = true;
$wgNamespacesToBeSearchedDefault[NS_FRAMEFAMILY] = true;
$wgNamespacesToBeSearchedDefault[NS_LINGMETAPHOR] = false;
$wgNamespacesToBeSearchedDefault[NS_CXSTANALYSIS] = true;
$wgNamespacesToBeSearchedDefault[NS_CXNMP] = true;
$wgNamespacesToBeSearchedDefault[NS_METARC] = true;
$wgNamespacesToBeSearchedDefault[NS_ICONCEPT] = true;

# Enable Semantics
# this call has to come before the namespace options below
enableSemantics( parse_url( $wgServer, PHP_URL_HOST ) );

# Allow for semantic annotation of custom namespaces
$smwgNamespacesWithSemanticLinks[NS_EVENT] = true;
$smwgNamespacesWithSemanticLinks[NS_EVENT_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_GLOSSARY] = true;
$smwgNamespacesWithSemanticLinks[NS_GLOSSARY_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_METAPHOR] = true;
$smwgNamespacesWithSemanticLinks[NS_METAPHORFAMILY] = true;
$smwgNamespacesWithSemanticLinks[NS_FRAME] = true;
$smwgNamespacesWithSemanticLinks[NS_FRAMEFAMILY] = true;
$smwgNamespacesWithSemanticLinks[NS_LINGMETAPHOR] = true;
$smwgNamespacesWithSemanticLinks[NS_METAPHOR_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_METAPHORFAMILY_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_FRAME_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_FRAMEFAMILY_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_LINGMETAPHOR_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_CXSTANALYSIS] = true;
$smwgNamespacesWithSemanticLinks[NS_CXSTANALYSIS_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_CXNMP] = true;
$smwgNamespacesWithSemanticLinks[NS_CXNMP_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_METARC] = true;
$smwgNamespacesWithSemanticLinks[NS_METARC_TALK] = false;
$smwgNamespacesWithSemanticLinks[NS_ICONCEPT] = true;
$smwgNamespacesWithSemanticLinks[NS_ICONCEPT_TALK] = false;

# don't show the default edit tab for some users
$wgGroupPermissions['*']['viewedittab'] = false;
$wgGroupPermissions['sysop']['viewedittab'] = true;

# Semantic MediaWiki settings
$sfgAutocompleteOnAllChars = true;
$smwgQDefaultLimit = 1000;
$smwgQMaxInlineLimit = 2000;
$smwgPropertyPagingLimit = 50; #increase paging limit for properties
$smwgQMaxDepth = 6;
$smwgQMaxSize = 1000;
$smwgShowFactbox = SMW_FACTBOX_NONEMPTY;

# Triplestore settings
$smwgDefaultStore = 'SMWSparqlStore';
$smwgSparqlDatabaseConnector = 'sesame';
$smwgSparqlQueryEndpoint = "http://localhost:8080/openrdf-sesame/repositories/$wgDBname";
$smwgSparqlUpdateEndpoint = "http://localhost:8080/openrdf-sesame/repositories/$wgDBname/statements";
$smwgSparqlDataEndpoint = '';

# Allows links to be entered into form fields
# (so definitions can link to others). Default is false.
$smwgLinksInValues = true;

# Change the default user group to be read-only
$wgGroupPermissions['user']['edit']             = false;
$wgGroupPermissions['user']['move']             = false;
$wgGroupPermissions['user']['move-subpages']    = false;
$wgGroupPermissions['user']['move-rootuserpages'] = false;
$wgGroupPermissions['user']['movefile']         = false;
$wgGroupPermissions['user']['createpage']       = false;
$wgGroupPermissions['user']['writeapi']         = false;
$wgGroupPermissions['user']['upload']           = false;
$wgGroupPermissions['user']['reupload']         = false;
$wgGroupPermissions['user']['reupload-shared']  = false;
$wgGroupPermissions['user']['minoredit']        = false;
$wgGroupPermissions['user']['purge']            = false;
$wgGroupPermissions['user']['sendemail']        = false;

# need to give sysops privileges that were taken away from user
$wgGroupPermissions['sysop']['edit']             = true;
$wgGroupPermissions['sysop']['writeapi']         = true;
$wgGroupPermissions['sysop']['createpage']       = true;
$wgGroupPermissions['sysop']['minoredit']        = true;
$wgGroupPermissions['sysop']['purge']            = true;
$wgGroupPermissions['sysop']['sendemail']        = true;

# need to give bot those privileges too
$wgGroupPermissions['bot']['edit']             = true;
$wgGroupPermissions['bot']['move']             = true;
$wgGroupPermissions['bot']['move-subpages']    = true;
$wgGroupPermissions['bot']['move-rootuserpages'] = true;
$wgGroupPermissions['bot']['movefile']         = true;
$wgGroupPermissions['bot']['createpage']       = true;
$wgGroupPermissions['bot']['upload']           = true;
$wgGroupPermissions['bot']['reupload']         = true;
$wgGroupPermissions['bot']['reupload-shared']  = true;
$wgGroupPermissions['bot']['minoredit']        = true;
$wgGroupPermissions['bot']['purge']            = true;
$wgGroupPermissions['bot']['sendemail']        = true;


# Restrict editing of templates and forms to sysops
$wgGroupPermissions['sysop']['edittemplate'] = true;
$wgGroupPermissions['sysop']['editform'] = true;
$wgGroupPermissions['sysop']['editcategory'] = true;
$wgGroupPermissions['sysop']['editproperty'] = true;
$wgGroupPermissions['sysop']['edittype'] = true;
$wgGroupPermissions['sysop']['editconcept'] = true;

$wgNamespaceProtection[NS_TEMPLATE] = array( 'edittemplate' );
$wgNamespaceProtection[SF_NS_FORM] = array( 'editform' );
$wgNamespaceProtection[NS_CATEGORY] = array( 'editcategory' );
$wgNamespaceProtection[SMW_NS_PROPERTY] = array( 'editproperty' );
$wgNamespaceProtection[SMW_NS_TYPE] = array( 'edittype' );
$wgNamespaceProtection[SMW_NS_CONCEPT] = array( 'editconcept' );

$wgShowIPinHeader = false; # For non-logged in users

# set cookie domain
$wgCookieDomain = '__WG_COOKIE_DOMAIN__';

# allow users to write javascript
$wgAllowUserJs = true;

# recent changes maximum age: 10 years
$wgRCMaxAge = 86400 * 365.242 * 10;

# By default, include debug settings (remove once setup complete)
require_once "$IP/EnableDebugSettings.php";

