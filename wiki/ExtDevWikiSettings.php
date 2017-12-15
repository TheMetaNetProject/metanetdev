<?php
/**
 * Additional permissions settings for External copy of development
 * Wiki. This wiki is readonly, except for sysops and above.
 * Anonymous users (*): can read and create/edit talk pages
 * Logged in users (user): can edit
 * There's no need for an analyst distinction, but we'll keep the category
 * around.
 */
# logged in users can edit certain talk pages
$wgGroupPermissions['user']['edit']  = true;
$wgGroupPermissions['user']['createtalk']  = true;

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
    $wgNamespacePermissionLockdown[$nsid]['edit'] = array('sysop');
    $wgNamespacePermissionLockdown[$nsid]['createtalk'] = array('sysop');
}


# restrictions set using the Lockdown extension
$wgSpecialPageLockdown['Export'] = array('user');
$wgSpecialPageLockdown['Recentchanges'] = array('user','analyst','sysop');
$wgSpecialPageLockdown['BrokenRedirects'] = array('user','analyst','sysop');
$wgSpecialPageLockdown['Userlogin'] = array('*');    # unblock login
$wgSpecialPageLockdown['UserLogout'] = array('*');    # unblock logout
$wgSpecialPageLockdown['Confirmemail'] = array('*'); # unblock email confirmation
# $wgSpecialPageLockdown['RequestAccount'] = array('*');    # unblock request account
$wgSpecialPageLockdown['PasswordReset'] = array('*'); #unblock password reset
$wgSpecialPageLockdown['ChangePassword'] = array('*'); #unblock password change
$wgSpecialPageLockdown['CreateAccount'] = array('analyst','sysop');
$wgActionLockdown['history'] = array('user','analyst','sysop');
$wgActionLockdown['info'] = array('user','analyst','sysop');
$wgActionLockdown['create2'] = array('analyst','sysop');
$wgSpecialPageLockdown[] = array('user','analyst','sysop'); # NEEDS TO BE THE LAST; locks all Special's not specified earlier

