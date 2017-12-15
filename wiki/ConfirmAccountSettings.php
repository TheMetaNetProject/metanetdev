<?php
/**
 * Settings for the ConfirmAccount extension
 */

$wgConfirmAccountContact = 'jhong@icsi.berkeley.edu';
$wgMakeUserPageFromBio = true;
$wgAutoWelcomeNewUsers = false;
$wgConfirmAccountRequestFormItems = array(
		'UserName'        => array( 'enabled' => true ),
		'RealName'        => array( 'enabled' => true ),
		'Biography'       => array( 'enabled' => false, 'minWords' => 25 ),
		'AreasOfInterest' => array( 'enabled' => false ),
		'CV'              => array( 'enabled' => false ),
		'Notes'           => array( 'enabled' => true ),
		'Links'           => array( 'enabled' => true ),
		'TermsOfService'  => array( 'enabled' => true ),
);
