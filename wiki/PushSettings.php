<?php
/**
 * Settings for the Push extension
 */

$langWikis =  array('en' => 'English Wiki',
					'es' => 'Spanish Wiki',
					'ru' => 'Russian Wiki',
					'fa' => 'Persian Wiki');

// don't allow pushing to self
$langCode = substr($wgScriptPath,-2);
unset($langWikis[$langCode]);

$scriptPref = substr($wgScriptPath, 0, -2);

foreach ($langWikis as $lang => $wikiname) {
	$egPushTargets[$wikiname] = $wgServer + $scriptPref + $lang;
}
$egPushLoginUser = 'Mnadmin';
$egPushLoginPassword = 'm4sBwy0u!';
$wgGroupPermissions['autoconfirmed']['push'] = false;
$wgGroupPermissions['autoconfirmed']['bulkpush'] = false;
$wgGroupPermissions['autoconfirmed']['filepush'] = false;
