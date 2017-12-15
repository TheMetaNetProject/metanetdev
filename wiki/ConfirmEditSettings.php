<?php
/**
 * Settings for the ConfirmEdit extension
 */

# do not subject authenticated users to captcha's
$wgGroupPermissions['*'            ]['skipcaptcha'] = false;
$wgGroupPermissions['autoconfirmed']['skipcaptcha'] = false;
$wgGroupPermissions['user'         ]['skipcaptcha'] = true;
$wgGroupPermissions['bot'          ]['skipcaptcha'] = true; // registered bots
$wgGroupPermissions['sysop'        ]['skipcaptcha'] = true;

# enable captcha's on edit and create (not just on account creation)
$wgCaptchaTriggers['edit']          = true;
$wgCaptchaTriggers['create']        = true;


# use questy captcha: supposedly more effective
require_once "$IP/extensions/ConfirmEdit/QuestyCaptcha.php";

$wgCaptchaQuestions[] = array( 'question' => "Metaphors are not linguistic.  They are ...", 'answer' => "conceptual");
$wgCaptchaQuestions[] = array( 'question' => "A place where you can find many frames.", 'answer' => "framenet" );
$wgCaptchaQuestions[] = array( 'question' => "The C in ECG", 'answer' => array("construction", "cxn") );
$wgCaptchaQuestions[] = array( 'question' => "Another word for frame element.", 'answer' => array( 'role', 'participant' ) );
