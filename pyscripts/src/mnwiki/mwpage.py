'''
MetaWiki Page Parser

Quick and dirty parser that handles templates.  Template calls are
turned into instances of the class TemplateCall which has
getter/setter methods for accessing the contents of the template
call.

Note that the parser handles {{!}} and <nowiki>|</nowiki> to handle
escaping of |.  But it's not smarter than just those two specific
strings.

Created on Jul 29, 2013
@author: jhong
'''

import sys, argparse, codecs
import wikipedia as pywikibot

class MediaWikiPage:
    '''
    Captures the content of a mediawiki page (initially given as a string)
    into a manipulable data structure.  Objects can be connected to the
    wiki to retrieve and modify pages.  Or, it can be used disconnected,
    in which case, it reads and outputs wiki-text as strings.
    
    You can retrieve a site using pywikibot.getSite(code)
    '''
    FREE = 'free'
    TEMPLATE = 'template'
    
    def __init__(self, pageTitle, mwSite=None):
        self.title = pageTitle
        self.content = []
        self.templates = []
        self.mwsite = mwSite
        self.page = None
    
    def load(self):
        ''' Loads the content of the page from the wiki (if it exists)
        '''
        if self.mwsite:
            self.page = pywikibot.Page(self.mwsite, self.title)
            if self.page.exists():
                self.parse(self.page.get())
            
    def save(self,comment=None):
        ''' Saves the page content to the wiki
        '''
        if self.page:
            self.page.put(self.towiki(),comment)
        
    def parse(self, pagestring):
        tstream = StringStream(pagestring)
        free_content = []
        while not tstream.eos():
            if self.atTemplateCall(tstream):
                # start of a template
                # save free content
                if free_content:
                    self.content.append((self.FREE,''.join(free_content)))
                    free_content = []
                template = TemplateCall(tstream)
                self.content.append((self.TEMPLATE,template))
                self.templates.append(template)
                continue
            free_content.append(tstream.read(1))

    def getcontent(self):
        ''' Method to retrieve all the content
        '''
        return self.content
    
    def gettemplate(self):
        ''' Method to retrieve the 1st template call on the page
        '''
        if self.templates:
            return self.templates[0]
        else:
            return None
    
    def gettemplates(self):
        ''' Method to retrieve all the top-level template calls
        '''
        return self.templates
    
    def towiki(self):
        ''' Method to regenerate the wiki page
        '''
        buf = []
        for (content_type, item) in self.content:
            if content_type==self.FREE:
                buf.append(item)
            elif content_type==self.TEMPLATE:
                buf.append(item.towiki())
        return ''.join(buf)
    
    def atTemplateCall(self,tstream):
        line = tstream.peek(3)
        if line.startswith('{{') and (line[2] != '{'):
            return True
        return False

    def __str__(self):
        return self.towiki()
    
    def __repr__(self):
        return self.towiki()
    
class TemplateCall:
    '''
    Class that captures the content of a Template call into a data
    structure with getter/setter methods.  It handles {{!}} and
    <nowiki>|</nowiki> as escapes for |, and escapes all | using
    the latter method for write-out.
    
    Also handles sub-templates, where the value of the variable is
    another template call, or a series of template calls.
    '''
    # static members
    END_TEMPLATE = '}}'
    START_TEMPLATE = '{{'
    VAR_ASSIGN = '='
    VAR_SEP = '|'
    NEW_LINE = '\n'
    TEMPLATE_NAME_END_CHARS = ['|','\n','}']
    
    def __init__(self,tstream):
        '''
        Given the stream at the start of which is a template
        call.  Read the template call portion.
        '''
        # initialize non-static members
        self.data = {}
        self.type = "ANON"  # default, for ANON, variable names are numbers
        self.varcounter = 0
        
        # print "Creating new template"
        self.readTemplateName(tstream)
        eot = False
        while not eot:
            if tstream.peek(1) == self.NEW_LINE:
                tstream.skip(1)
            elif tstream.peek(2) == self.END_TEMPLATE:
                tstream.skip(2)
                eot = True
            else:
                self.readTemplateVariable(tstream)
        # print "End of template:",self.name
        # print "Vars in template:",self.getvars()
        
    def __str__(self):
        return self.towiki()
    
    def __repr__(self):
        return self.towiki()

    def towiki(self):
        buf = []
        buf.append(self.START_TEMPLATE)
        buf.append(self.name)
        for var in self.getvars():
            buf.append(self.NEW_LINE)
            buf.append(self.VAR_SEP)
            buf.append(var)
            buf.append(self.VAR_ASSIGN)
            value = self.get(var)
            if isinstance(value,list):
                # currently all subtemplates and only subtempplates
                # are in lists
                for templ in value:
                    buf.append(templ.towiki())
                #buf.append("subtemplate")
            else:
                buf.append(value.replace('|','<nowiki>|</nowiki>'))
        buf.append(self.NEW_LINE)
        buf.append(self.END_TEMPLATE)
        return ''.join(buf)

    def getvars(self):
        # returns a sorted list of the variable names set in the template
        return sorted(self.data.keys())

    def set(self,variable,value):
        # sets a variable: note that value can be any object
        self.data[variable] = value

    def append(self,variable,value):
        # appends value to the variable
        if variable not in self.data:
            self.set(variable,value)
        elif isinstance(self.data[variable],basestring):
            if self.data[variable][-1]==',':
                self.data[variable] += value
            else:
                self.data[variable] += ',' + value
        elif isinstance(self.data[variable],list):
            self.data[variable].append(value)

    def get(self,variable):
        return self.data[variable]
    
    def readTemplateName(self,tstream):
        # discard the '{{'
        tstream.skip(2)
        tname = []
        curr_char = tstream.read(1)
        while curr_char not in self.TEMPLATE_NAME_END_CHARS:
            tname.append(curr_char)
            curr_char = tstream.read(1)
        # if the template name ended with a '|' then put it back
        if curr_char != self.VAR_SEP:
            tstream.back(1)
        self.name = ''.join(tname).strip()
        #print "read Template name:"+self.name
    
    def peekTemplate(self,tstream):
        chars = tstream.peek(3)
        if chars.startswith('{{') and (chars[2] != '{'):
            return True
        return False
    
    def readTemplateVariable(self,tstream):
        # discard the '|'
        tstream.read(1)
        curr_char = tstream.read(1)
        vname = []
        varname = ''
        while curr_char not in ['=','|','}']:
            vname.append(curr_char)
            curr_char = tstream.read(1)
        if (curr_char=='|') or (curr_char=='}'):
            # it's an anonymous variable
            self.varcounter += 1
            varname=str(self.varcounter)
            # in this case, what we just read is a value
            self.set(varname, ''.join(vname))
            tstream.back(1)
            return

        # if get here, then curr_char == '='
        # it's a named variable
        self.type='NAMED'
        varname=''.join(vname).strip()
        #print self.name,":Reading variable", varname
        # check if what comes next is a template
        if self.peekTemplate(tstream):
            # if its a template, then it can be a list of templates
            value = []
            #print "Value of variable is another template!"
            while self.peekTemplate(tstream):
                subtemplate = TemplateCall(tstream)
                value.append(subtemplate)
            self.set(varname, value)
            return
        # value is not a template, here we are reading a value.
        # we need to handle {{!}} and <nowiki>!</nowiki> detection
        # and translation
        char_buf = []
        while not tstream.eos():
            curr_char = tstream.read(1)
            if curr_char=='{':
                if tstream.peek(4)=='{!}}':
                    tstream.back(1)
                    char_buf.append(tstream.read(5))
                    continue
            if curr_char in ['|','}']:
                # check for nowiki case
                if (curr_char == '|') and (tstream.peek(9)=='</nowiki>'):
                    tstream.back(1)
                    char_buf.append(tstream.read(10))
                    continue
                else: 
                    tstream.back(1) # this is because end of template gets processed elsewhere
                    value = ''.join(char_buf).strip()
                    self.set(varname,
                             value.replace('{{!}}','|').replace('<nowiki>|</nowiki>','|'))
                    return
            char_buf.append(curr_char)

class StringStream:
    '''
    Quick and dirty stream-like functionality with strings
    '''
    content = ''
    position = 0
    
    def __init__(self,instring):
        self.content=instring
        self.position=0
        self.length = len(instring)
    
    def read(self,n):
        '''
        return n characters from the string, and advance the
        position accordingly
        '''
        end = self.position+n
        if end > self.length:
            end = self.length
        retval = self.content[self.position:end]
        self.position = end
        return retval
    
    def peek(self,n):
        '''
        return n characters from the string, but don't advance the
        position
        '''
        end = self.position+n
        if end > self.length:
            end = self.length
        return self.content[self.position:end]
    
    def back(self,n):
        '''
        move position backward by n
        '''
        newpos = self.position - n
        if newpos < 0:
            newpos = 0
        self.position = newpos
        
    def skip(self,n):
        ''' move position ahead by n
        '''
        newpos = self.position + n
        if newpos > self.length:
            newpos = self.length
        self.position = newpos

    def eos(self):
        if self.position >= self.length:
            return True
        return False


def main():
    '''
    This method here for testing
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Test",
        epilog="")
    parser.add_argument("infile",
                        help="input file")
    cmdline = parser.parse_args()
    wpage = MediaWikiPage("Test")
    with codecs.open(cmdline.infile,'r',encoding='utf-8') as inputfile:
        page = inputfile.read()
        wpage.parse(page)
        print wpage.towiki()

if __name__ == '__main__':
    sys.exit(main())
    