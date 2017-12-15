import sys
import re

class Element:
    def __init__(self, name, mapping):
        self.name = name
        self.mapping = mapping

    #Print out contents of an Element object.
    def printElement(self, indent):
        if isinstance(self.mapping, basestring):
            print self.name + ': ' + self.mapping,
        else:
            print self.name + ': '
            mapping.printMediaWikiContainer(indent+1)

    def outputToMediaWiki(self):
        toReturn = ''
        self.name = self.name.replace('|', '{{!}}')
        if isinstance(self.mapping, basestring):
            self.mapping = self.mapping.replace('|', '{{!}}')
            
            self.mapping = self.mapping.rstrip()
            toReturn += '|' + self.name + '=' + self.mapping + '\n'
        elif isinstance(self.mapping, MediaWikiContainer):
            toReturn += '|' + self.name + '=' + self.mapping.outputToMediaWiki()
        else:
            toReturn += '|' + self.name + '=' + '\n'
        return toReturn

class MediaWikiContainer:
    def __init__(self, name):
        name = name.rstrip()
        self.containerName = name
        self.page = []
        self.brackets = False

    def add(self, container):
        self.page.append(container)

    def bracketsHere(self, bracket):
        if bracket:
            self.brackets = True

    def printMediaWikiContainer(self, indent):
        print '--',
        print self.containerName,
        print '--'

        indent += 1

        for i in range(len(self.page)):
            for k in range(indent):
                print ' ',
            if isinstance(self.page[i], Element):
                self.page[i].printElement(indent)
            elif isinstance(self.page[i], MediaWikiContainer):
                self.page[i].printMediaWikiContainer(indent+1)

    def outputToMediaWiki(self):
        toReturn = ''
        if self.brackets:
            toReturn = '{{' + self.containerName + '\n'
        else:
            toReturn = self.containerName + '='
        
        for i in range(len(self.page)):
            if isinstance(self.page[i], Element):
                toReturn += self.page[i].outputToMediaWiki()
            elif isinstance(self.page[i], MediaWikiContainer):
                if self.brackets:
                    toReturn += '|'
                toReturn += self.page[i].outputToMediaWiki()
                if toReturn[-2:] != '}}':
                    toReturn += '\n'
        if self.brackets:
            toReturn += '}}'
        return toReturn

    def getElementValues(self, elementName):
        elementValues = []
        for i in range(len(self.page)):
            if isinstance(self.page[i], Element):
                newElementName = self.page[i].name
                if newElementName == elementName:
                    elementValues.append(self.page[i].mapping)
            elif isinstance(self.page[i], MediaWikiContainer):
                elementValues.extend(self.page[i].getElementValues(elementName))
        return elementValues

    def getLSource(self):
        elementValues = []
        for i in range(len(self.page)):
            if isinstance(self.page[i], Element):
                newElementName = self.page[i].name
                if newElementName == 'Source':
                    elementValues.append(self.page[i].mapping)
            elif isinstance(self.page[i], MediaWikiContainer):
                elementValues.extend(self.page[i].getElementValues('Source'))
        return elementValues[0]

    def getLTarget(self):
        elementValues = []
        for i in range(len(self.page)):
            if isinstance(self.page[i], Element):
                newElementName = self.page[i].name
                if newElementName == 'Target':
                    elementValues.append(self.page[i].mapping)
            elif isinstance(self.page[i], MediaWikiContainer):
                elementValues.extend(self.page[i].getElementValues('Target'))
        return elementValues[0]

    # ------------------------------------------------------------------ #
    #Fixes!
    # ------------------------------------------------------------------ #

    #Check that this metaphor has a metaphor alias corresponding with its title
    def hasAlias(self, containerTitle):
        compareAlias = ''
        if containerTitle[:9] == 'Metaphor:':
            compareAlias = containerTitle[9:]
        else:
            return
        aliases = self.getElementValues("Metaphor.Alias.Name")
        for i in range(len(aliases)):
            if aliases[i] == compareAlias:
                return
        newContainer = MediaWikiContainer("Metaphor.Alias")
        newContainer.bracketsHere(True)
        newElement = Element("Metaphor.Alias.Name", containerTitle)
        newContainer.add(newElement)

        for i in range(len(self.page)):
            entry = self.page[i]
            if isinstance(entry, MediaWikiContainer) and entry.containerName == "Aliases":
                entry.add(newContainer)

    #Uncapitalize role names
    def uncapRoles(self):
        for i in range(len(self.page)):
            entry = self.page[i]
            if isinstance(entry, Element) and entry.name == "Role.Name":
                roleName = entry.mapping
                roleName = roleName[:1].lower() + roleName[1:]
                entry.mapping = roleName
            elif isinstance(entry, MediaWikiContainer):
                entry.uncapRoles()

    def fixSchemaNames(self):
        for i in range(len(self.page)):
            entry = self.page[i]
            if isinstance(entry, Element) and (entry.name == "Source schema" or entry.name == "Target schema" or entry.name == "Related schema.Name"):
                schemaName = entry.mapping
                schemaName = schemaName.replace('_', ' ')
            elif isinstance(entry, MediaWikiContainer):
                entry.fixSchemaNames()

def findAndReplacePipes(input, escapedPipes):
    nextPipeIndex = input.find("{{!}}")
    while nextPipeIndex != -1:
        escapedPipes.append(nextPipeIndex)
        input = input.replace("{{!}}", "|", 1)
        nextPipeIndex = input.find("{{!}}")
    return input

#Returns true if the input represents a "template" in MediaWiki markup
def isBracket(str, index):
    return (str[index:index+2] == '{{' or str[index:index+2] == '}}')
                                               
def nextTokenIndexFromIndex(str, index, escapedPipes):
    brackets = False
    if index == -1: index += 1
    elif (isBracket(str, index)):
        index += 2
        brackets = True
    else:
        index += 1
        brackets = False
                                               
    openBracket = str.find('{{', index)
    pipe = str.find('|', index)
    while pipe in escapedPipes:
        pipe = str.find('|', pipe+1)
    equals = str.find('=', index)
    closingBracket = str.find('}}', index)
                                               
    if openBracket != -1 and pipe != -1 and equals != -1 and closingBracket != -1:
        return min(min(min(openBracket, pipe),equals),closingBracket)
                                               
    elif openBracket != -1 and pipe != -1 and equals != -1:
        return min(min(openBracket, pipe),equals)
    elif (openBracket != -1 and pipe != -1 and closingBracket != -1):
        return min(min(openBracket, pipe),closingBracket)
    elif (openBracket != -1 and closingBracket != -1 and equals != -1):
        return min(min(openBracket,equals),closingBracket)
    elif (closingBracket != -1 and pipe != -1 and equals != -1):
        return min(min(pipe,equals),closingBracket)

    elif (openBracket != -1 and pipe != -1):
        return min(openBracket, pipe)
    elif (openBracket != -1 and equals != -1):
        return min(openBracket, equals)
    elif (openBracket != -1 and closingBracket != -1):
        return min(openBracket, closingBracket)
    elif (pipe != -1 and equals != -1):
        return min(pipe, equals)
    elif (pipe != -1 and closingBracket != -1):
        return min(pipe, closingBracket)
    elif (equals != -1 and closingBracket != -1):
        return min(equals, closingBracket)

    elif (openBracket != -1):
        return openBracket
    elif (pipe != -1):
        return pipe
    elif (equals != -1):
        return equals
    elif (closingBracket != -1):
        return closingBracket
    else:
        if (brackets):
            return (index-1)
        else:
            return (index-2)
                     
#Return the next token as a String
def nextToken(str, tokenIndex):
    if str[tokenIndex:tokenIndex+2] == '{{' or str[tokenIndex:tokenIndex+2] == '}}':
        return str[tokenIndex:tokenIndex+2]
    else:
        return str[tokenIndex:tokenIndex+1]
                                               
#Return the next Element located between the start and end indexes provided
def getElement(str, start, end):
    if str[start:start+2] == '{{':
       return str[start+2:end]
    else:
       return str[start+1:end]
                                               
class MediaWikiParse:
    def __init__(self):
        self.tokenIndex = 0
        self.endTokenIndex = 0
        self.endToken = ''
        self.startToken = ''
        self.pages = {}
        self.escapedPipes = []

    #Parse the MediaWiki page input and save it to memory. Return its name so the user can take note of it if desired.
    def parseAndSave(self, title, input):
        input = findAndReplacePipes(input, self.escapedPipes)
        newContainer = self.makeMediaWikiContainer(input, 0)
        self.resetTokens()
        self.pages[title] = newContainer

    #Get the MediaWiki page associated with this name
    def getPage(self, name):
        aContainer = self.pages[name]
        pageContents = aContainer.outputToMediaWiki()
        return pageContents

    #Prints the contents of a page. Used for debugging purposes.
    def printContentsOfPage(self, name):
        self.pages[name].printMediaWikiContainer(0)
                                               
    #Get names of pages that are saved in memory
    def getPageNames(self):
       return self.pages.keys()

    #Get all of the values associated with the chosen element. (i.e., find all of the "Example.Text"'s, etc.
    def getTheElementValues(self, pageTitle, name):
        page = self.pages[pageTitle]
        theElements = page.getElementValues(name)
        return theElements

    #Get the Linguistic Source from a page
    def getLingSource(self, pageTitle):
        page = self.pages[pageTitle]
        return page.getLSource()

    #Get the Linguistic Target from a page
    def getLingTarget(self, pageTitle):
        page = self.pages[pageTitle]
        return page.getLTarget()

    def getExampleTexts(self, pageTitle):
        page = self.pages[pageTitle]
        theElements = page.getElementValues('Example.Text')
        return theElements

    # ------------------------------------------------------------------ #
    #Fixes!
    # ------------------------------------------------------------------ #
    
    #Check that there is a metaphor alias corresponding to the page's title
    def aliasCheck(self, pageTitle):
        page = self.pages[pageTitle]
        page.hasAlias(pageTitle)
        self.pages[pageTitle] = page

    #Uncapitalize the roles
    def uncapitalizeRoles(self, pageTitle):
        page = self.pages[pageTitle]
        page.uncapRoles()
        self.pages[pageTitle] = page

    #Make sure that words in a Schema name are separated by spaces, not underscores
    def fixSchema(self, pageTitle):
        page = self.pages[pageTitle]
        page.fixSchemaNames()
        self.pages[pageTitle] = page

    # ------------------------------------------------------------------ #
    #Hidden Methods (You shouldn't have to call any of these)
    # ------------------------------------------------------------------ #
    
    #Advance our tokens and token index references, so that they are pointing to the next element in the MediaWiki page
    def advanceTokens(self, str):
        self.tokenIndex = self.endTokenIndex
        self.endTokenIndex = nextTokenIndexFromIndex(str, self.tokenIndex, self.escapedPipes)
        self.endToken = nextToken(str, self.endTokenIndex)
        self.startToken = nextToken(str, self.tokenIndex)

        while self.startToken == '=' and self.endToken == '=':
            self.endTokenIndex = nextTokenIndexFromIndex(str, self.endTokenIndex, self.escapedPipes)
            self.endToken = nextToken(str, self.endTokenIndex)

    def pastTokens(self, str):
        self.endTokenIndex = self.tokenIndex
        self.tokenIndex = lastTokenIndex(str, self.tokenIndex)
        self.startToken = nextToken(str, self.tokenIndex)
        self.endToken = nextToken(str, self.endTokenIndex)

    def resetTokens(self):
        self.tokenIndex = 0
        self.endTokenIndex = 0
        self.startToken = ''
        self.endToken = ''

    # Starting at beginIndex, parse through the MediaWiki text, and store all of its
    # information in an MediaWikiContainer object. Return that object.
    def makeMediaWikiContainer(self, str, beginIndex):
        self.tokenIndex = nextTokenIndexFromIndex(str,beginIndex-1,self.escapedPipes)
        self.endTokenIndex = nextTokenIndexFromIndex(str, self.tokenIndex,self.escapedPipes)
        theName = getElement(str, self.tokenIndex, self.endTokenIndex)
        temp = MediaWikiContainer(theName)
        brackets = False
        temp.bracketsHere(True)
        self.advanceTokens(str)
        
        while (True):
            if self.startToken == '{{' or self.endToken == '|':
                self.advanceTokens(str)
                temp.bracketsHere(True)

            if self.startToken == '}}':
                break

            if self.endToken == '=':
                name = getElement(str, self.tokenIndex, self.endTokenIndex)
                self.advanceTokens(str)
                if self.endToken == '|':
                    temp.add(Element(name, getElement(str,self.tokenIndex,self.endTokenIndex)))
                elif self.endToken == '}}':
                    temp.add(Element(name, getElement(str,self.tokenIndex,self.endTokenIndex)))
                    return temp
                else:
                    nestedTemp = MediaWikiContainer(name)
                    while self.endToken == '{{':
                        newTemp = self.makeMediaWikiContainer(str, self.endTokenIndex)
                        nestedTemp.add(newTemp)
                        self.advanceTokens(str)
                    temp.add(nestedTemp)
                    self.advanceTokens(str)
        self.resetTokens()
        return temp

    """
    def outputToMediaWiki(containers):
        toReturn = ''
        for i in range(len(containers)):
            toReturn += containers[i].outputToMediaWiki()
        return toReturn
        """

def main():
    # ------------------------------------------------------------------ #
    #Example Functionality shown here
    # ------------------------------------------------------------------ #
    page1Stuff = open('input1.txt', 'r')
    page2Stuff = open('input2.txt', 'r')
    page3Stuff = open('input3.txt', 'r')
    page4Stuff = open('input4.txt', 'r')
    page1Contents = page1Stuff.read()
    page2Contents = page2Stuff.read()
    page3Contents = page3Stuff.read()
    page4Contents = page4Stuff.read()
    
    page1 = 'Metaphor:MORALITY IS STRAIGHTNESS'
    page2 = 'Metaphor:FREEDOM OF ACTION IS THE LACK OF IMPEDIMENTS TO MOVEMENT'
    page3 = 'Linguistic metaphor:Address barrier'
    page4 = 'Schema:Seeing'
    newParser = MediaWikiParse()
    newParser.parseAndSave(page1, page1Contents)
    newParser.parseAndSave(page2, page2Contents)
    newParser.parseAndSave(page3, page3Contents)
    newParser.parseAndSave(page4, page4Contents)
    
    # ------------------------------------------------------------------ #
    # (1) Get Linguistic Source and Linguistic Target
    # ------------------------------------------------------------------ #
    try:
        linguisticSource = newParser.getLingSource(page1)
        linguisticTarget = newParser.getLingTarget(page1)
        print 'Linguistic Source: ' + linguisticSource,
        print 'Linguistic Target: ' + linguisticTarget,
    except:
        sys.exit(0)
    print '\n',
    # ------------------------------------------------------------------ #
    # (2) Get the Example Texts
    # ------------------------------------------------------------------ #
    elements = newParser.getExampleTexts(page3)
    print 'Example Texts: '
    for i in range(len(elements)):
        print elements[i],
    print '\n',
    # ------------------------------------------------------------------ #
    # (3) Getting all of the values associated with a certain element
    #       - For example, find all of the Entailment Inferences
    # ------------------------------------------------------------------ #
    newElements = newParser.getTheElementValues(page2, 'Entailment.Source inference')
    print 'Entailment Inferences: '
    for i in range(len(newElements)):
        print newElements[i],
    print '\n',
    # ------------------------------------------------------------------ #
    # (4) Perform fixes
    # ------------------------------------------------------------------ #
    newParser.aliasCheck(page2)
    newParser.fixSchema(page2)
    newParser.uncapitalizeRoles(page4)
    # ------------------------------------------------------------------ #
    # (5) Print the contents of a page in order to debug
    # ------------------------------------------------------------------ #
    print newParser.getPage(page2)

if __name__ == '__main__':
    main()