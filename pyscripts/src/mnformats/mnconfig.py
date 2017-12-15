#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: mnconfig
   :platform: Unix
   :synopsis: MetaNet Configuration File Library

Utility class for reading configuration information from a file.  The ConfigParser supports
interpolation, so variables set in the same section or in the default section can be
reused in the same section via %(varname).  Note that the configurations cascade--so the
modestring-marked section takes precedence to the unmarked section which takes
precedence over the DEFAULT section.  The config file structure is as follows:

[applicationame{.modestring}]

# applications are m4detect, m4mapping, fastdbimport, etc.

systemcomponent.configvariable{.lang}:value

# system components are cms, sbs, lms, etc.  When a lang extension is specified
# on a variable, it overrides that variable's value for each respective language.

[DEFAULT]

# put system-wide defalt settings here

.. moduleauthor:: Jisup Hong <jhong@icsi.berkeley.edu>

"""
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
import pprint, os, sys, logging, argparse, time

class MetaNetConfigParser:
    """
    Parses configuration files that have the following section syntax.
    
    [appname.appmode] e.g. [m4detect.gmr.case], where appname=m4detect,
    and appmode=gmr.case.
    
    This class reads all the configuration variables and stores them
    internally, so that instances of the class can be serialized.
    Configuration variables have the following syntax
    
    componentnamespace.variable.languageoverride:value
    
    componentnamespace. is optional
    and so is the .languageoverride.
    configuration variable names may otherwise not contain .'s
    
    """
    NOCOMP = '__NOCOMPNS__'
    
    def __init__(self, configfname, appname, appmode=None):
        logger = logging.getLogger(__name__)
        self.appname = appname
        self.appmode = appmode
        self.validLangs = set(['en','es','fa','ru'])
        # Note: sectionList will contain first the appname
        # and then the appname qualified with the appmode if
        # an appmode parameter is passed in
        self.sectionList = [appname]
        if appmode:
            self.sectionList.append(appname + '.' + appmode)
        cparser = SafeConfigParser()
        cparser.read(configfname)
        compoptions = {}
        for section in self.sectionList:
            optHash = {}
            try:
                optList = cparser.options(section)
            except NoSectionError:
                logger.warning('Section %s not defined in config file %s', section, configfname)
                continue
            for opt in optList:
                ovect = opt.split(u'.')
                if len(ovect)==1:
                    # no lang override, no namespace
                    compns = self.NOCOMP
                    varname = opt
                elif len(ovect)==2:
                    if ovect[1] in self.validLangs:
                        compns = self.NOCOMP
                        varname = opt
                    else:
                        compns = ovect[0]
                        varname = ovect[1]
                elif len(ovect)==3:
                    if ovect[2] not in self.validLangs:
                        logger.error('Skipping config variable with invalid lang extension: %s',opt)
                        continue
                    compns = ovect[0]
                    varname = ovect[1] + '.' + ovect[2]
                else:
                    logger.error('Skipping config variable with bad syntax: %s',opt)
                    continue
                if compns not in compoptions:
                    compoptions[compns] = {}
                compoptions[compns][varname] = cparser.get(section,opt)
        self.confcache = compoptions


    def addValidLanguage(self,lang):
        """
        Takes a 2-letter language code and adds it to the list of possible
        language override extensions
        """
        self.validLangs.add(lang.lower())

    def getComponentOptions(self, component):
        """ Get options .
        """
        if component in self.confcache:
            return self.confcache[component]
        else:
            return {}

    def getListFromComp(self, component, cvar, lang=None, required=False,
                         default=[], override=None):
        if override:
            return override
        clist = default
        cvalue = self.getValueFromComp(component, cvar, lang, required)
        if cvalue:
            clist = [elem.strip() for elem in cvalue.split(u',')]
        return clist

    def getFlagFromComp(self, component, cvar, lang=None, required=False,
                        default=False):
        cvalue = self.getValueFromComp(component, cvar, lang, required)
        if cvalue:
            if cvalue.lower() in ['no', 'false', 'f', 'n', '0']:
                return False
            return True
        return default

    def getValueFromComp(self, component, cvar, lang=None, required=False,
                         default=None, override=None):
        if override:
            return override
        options = self.getComponentOptions(component)
        if lang:
            lcvar = cvar + '.' + lang
            if lcvar in options:
                return options[lcvar]
        if cvar in options:
            return options[cvar]
        else:
            if required:
                raise NoOptionError(cvar,component)
        return default
    
    def getValue(self, cvar, lang=None, required=False,
                 default=None, override=None):
        return self.getValueFromComp(self.NOCOMP, cvar, lang, required, default, override)

    def getInt(self, cvar, lang=None, required=False,
               default=None, override=None):
        val = self.getValue(cvar,lang,required,default,override)
        try:
            return int(val)
        except:
            return default

    def getFloat(self, cvar, lang=None, required=False,
               default=None, override=None):
        val = self.getValue(cvar,lang,required,default,override)
        try:
            return float(val)
        except:
            return default

    def getList(self, cvar, lang=None, required=False,
                default=[], override=None):
        return self.getListFromComp(self.NOCOMP, cvar, lang, required, default, override)

    def getFlag(self, cvar, lang=None, required=False):
        return self.getFlagFromComp(self.NOCOMP, cvar, lang, required)

    def getIntFromComp(self, component, cvar, lang=None, required=False,
                       default=None, override=None):
        val = self.getValueFromComp(component,cvar,lang,required,default,override)
        try:
            return int(val)
        except:
            return default

    def getFloatFromComp(self, component, cvar, lang=None, required=False,
                       default=None, override=None):
        val = self.getValueFromComp(component,cvar,lang,required,default,override)
        try:
            return float(val)
        except:
            return default

def main():
    """ for testing
    """
    FORMAT = '%(asctime)-15s - %(message)s'
    DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
    logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="MetaNet config file parser")
    parser.add_argument('--file', '-f', help='Config file',
                        default='/u/metanet/etc/mnsystem.conf')
    parser.add_argument('--app','-a', help='Application', default="m4detect")
    parser.add_argument('--mode','-m', help="Application mode",default=None)
    parser.add_argument('--comp','-c',help="Component",default=None)
    parser.add_argument('--lang','-l', help='Language', default=None)
    parser.add_argument('vars', default=[], nargs='*', help='configuration variables')
    cmdline = parser.parse_args()

    mncparser = MetaNetConfigParser(cmdline.file, cmdline.app, cmdline.mode)
    if cmdline.vars:
        if cmdline.comp:
            for cvar in cmdline.vars:
                print mncparser.getValueFromComp(cmdline.comp, cvar, cmdline.lang)
        else:
            for cvar in cmdline.vars:
                print mncparser.getValue(cvar, cmdline.lang)
    else:
        if cmdline.comp:
            opts = mncparser.getComponentOptions(cmdline.comp)
            print pprint.pformat(opts)
        else:
            print >> sys.stderr, "Must specify --comp or a variable"
        

if __name__ == "__main__":
    status = main()
    sys.exit(status)
    
