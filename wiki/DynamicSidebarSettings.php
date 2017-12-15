<?php
/**
 * Settings for the DynamicSidebar extension
 */

// Enable debugging
//$wgDebugLogGroups["dynamic-sidebar"] = "/tmp/sidebar-debug.txt";
 
// Allow users to create their own custom sidebars under User:<username>/Sidebar
// Default: true
$wgDynamicSidebarUseUserpages = true;
 
// Allow group sidebars under MediaWiki:Sidebar/Group:<group>
// Default: true
$wgDynamicSidebarUseGroups = true;
 
// Allow category based sidebars under MediaWiki:Sidebar/Category:<category>
// Default: true
$wgDynamicSidebarUseCategories = true;
