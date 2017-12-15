<?php
/**
 * BibManager Extension Settings
 */
$wgBibManagerCitationArticleNamespace = NS_CITATION;
$wgBibManagerCitationFormats = array (
'-'             => '%author%: %title%, %year%',
    'article'       => '%author% (%year%): %title%. <em>%journal%</em>, %volume%, %pages%',
    'book'          => '%author% (%year%): %title%. (%edition%). <em>%publisher%</em>, %address%, %pages%',
    'booklet'       => '%title%',
    'conference'    => '%author% (%year%): %title%. %booktitle%',
    'inbook'        => '%author% (%year%): %title%. (%edition%). <em>%publisher%</em>, %address%, %pages%, %editor%, %chapter%',
    'incollection'  => '%author% (%year%): %title%.  %booktitle%',
    'inproceedings' => '%author% (%year%): %title%. <em>%publisher%</em>, %booktitle%',
    'manual'        => '%title%',
    'masterthesis'  => '%author% (%year%): %title%. %school%',
    'misc'          => '%author%: %title%, %year%',
    'phdthesis'     => '%author% (%year%): %title%. %school%',
    'proceedings'   => '%title% (%year%)',
    'techreport'    => '%author% (%year%): %title%. %institution%.',
    'unpublished'   => '%author%: %title%. %note%.'
);
$wgGroupPermissions['*']['bibmanageredit']      = false;
$wgGroupPermissions['poweruser']['bibmanageredit'] = true;
$wgGroupPermissions['poweruser']['bibmanagercreate'] = true;
$wgGroupPermissions['poweruser']['bibmanagerdelete'] = true;
$wgBibManagerUseJS = true;
