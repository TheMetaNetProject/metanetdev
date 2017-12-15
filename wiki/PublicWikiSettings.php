<?php
/**
 * Anonymous users (*) can: read pages, create talk pages
 * 	- cannot view special pages, revision history, source, api, or export
 * Logged-in users (user) can: edit, move, delete, access api, revision history, export, etc.
 */

# set permisions so that anonymous users can edit certain talk pages
# give edit permissions and createtalk permissions
$wgGroupPermissions['*']['edit']  = true;
$wgGroupPermissions['*']['createtalk']  = true;

# restrict edit access on all namespaces except the relevant talk ones
# to logged in users
$metaNetTalkNamespaces = array(551,553,555,557,561,563,565);
$allNamespaces = array(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                       500, 501, 502, 503, 550, 551, 552, 553, 554,
                       555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565,
                       570, 571, 800, 801, 102, 103, 108, 109, 106,
                       107, 274, 275, 104, 105);
foreach ($allNamespaces as $nsid) {
    if (in_array($nsid, $metaNetTalkNamespaces)) {
        continue;
    }
    $wgNamespacePermissionLockdown[$nsid]['edit'] = array('user');
    $wgNamespacePermissionLockdown[$nsid]['createtalk'] = array('user');
}

$wgSpecialPageLockdown['Export'] = array('sysop');
$wgSpecialPageLockdown['Recentchanges'] = array('analyst','sysop');
$wgSpecialPageLockdown['BrokenRedirects'] = array('analyst','sysop');
$wgSpecialPageLockdown['Search'] = array('*');    # unblock search
$wgSpecialPageLockdown['Userlogin'] = array('*');    # unblock login
$wgSpecialPageLockdown['Confirmemail'] = array('*'); # unblock email confirmation
# $wgSpecialPageLockdown['RequestAccount'] = array('*');    # unblock request account
$wgSpecialPageLockdown['PasswordReset'] = array('*'); #unblock password reset
$wgActionLockdown['history'] = array('analyst','sysop');
$wgActionLockdown['info'] = array('analyst','sysop');
$wgSpecialPageLockdown[] = array('analyst','sysop'); # NEEDS TO BE THE LAST; locks all Special's not specified earlier

