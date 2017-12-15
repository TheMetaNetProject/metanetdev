#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import sys
import re
import subprocess
import argparse
import json

'''
Reads in the output of the LM extractor-- either a json file (which
contains the sentences to import) or a list of LMs (for which the
sentences need to be looked up)-- and generates a mediawiki
import file--one page per LM.

The resulting file can then be imported to the wiki using
pywikipediabot.
'''

tagtrans = {
    'poverty': {
    'en':u'Poverty',
    'es':u'Pobreza',
    'ru':u'Бедность',
    'fa':u'فقر'},
    'taxation': {
    'en':u'Taxation',
    'es':u'Tributación',
    'ru':u'Налогообложение',
    'fa':u'مالیات'},
    'wealth': {
    'en':u'Wealth and social class',
    'es':u'La riqueza y la clase social',
    'ru':u'Богатство и социальный класс',
    'fa':u'ثروت و طبقه اجتماعی'},
    'education': {
    'en':u'Access to education',
    'es':u'El acceso a la educación',
    'ru':u'Доступ к образованию',
    'fa':u'دسترسی به آموزش و پرورش'},
    'governance': {
    'en':u'Governance',
    'es':u'Gobernación',
    'ru':u'управление',
    'fa':u'حکومت'},
    'ei': {
    'en': u'Economic inequality',
    'es': u'La desigualdad económica',
    'ru': u'Экономическое неравенство',
    'fa': u'نابرابری اقتصادی'
    }}

def main():
    global tagtrans
    botname = 'Metabot'
    default_maxsents = 100
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Convert extracted metaphors into in a format that can be'\
        ' used by pywikipedia to import into the wiki.  This includes '\
        'retrieving sentences.')
    parser.add_argument('-m', '--maxsents',required=False, dest='maxsents',
                        help='Max number of sentences to import per '\
                        'lingistic metaphor.Set to 0 to suppress sentence '\
                        'importation',default=default_maxsents)
    
    parser.add_argument('-p', '--provenance',required=False,dest='provenance',
                        help='When set this value overrides the default '\
                        'provenances, which are names of the default '\
                        'corpora used.')
    parser.add_argument('-t', '--textdocument', required=False, dest='textdoc',
                        help='For use with input documents rather than '\
                        'corpora',default='')
    parser.add_argument('-g', '--tag', required=False, dest='tag',
                        help='String to add to the Tag field of the LM',
                        default='')
    parser.add_argument('-j','--json-mode',dest='jsonmode',
                        help='To force json mode.',action="store_true")
    parser.add_argument('importfiles',nargs=argparse.REMAINDER)
    name_space = parser.parse_args()
    args = vars(name_space)

    maxsents = args['maxsents']
    importfiles = args['importfiles']
    textdoc = args['textdoc']
    forcejsonmode = args['jsonmode']
    
    subjrel = {'en':'ncsubj','es':'subj','ru':'verb-subject'}
    objrel = {'en':'dobj', 'es':'dobj','ru':'verb-object'}
    resultsdir = {'en':'/u/metanet/Parsing/Results/bnc',
                  'es':'/u/metanet/Parsing/Results/GW/es',
                  'ru':'/tscratch/tmp/russian_metaphor_search',
                  'fa':''}
    corpusname = {'en':'BNC','es':'GW','ru':'RU-WAC','fa':'Persian Tree Bank'}
    language = {'en':'English','es':'Spanish', 'ru':'Russian', 'fa':'Persian'}

    for ifile in importfiles:
        print 'creating wiki import for '+ifile+'\n' 
        lang = ''
        jdata = None
        jsonmode = False
        
        if ifile.endswith('.json') or (forcejsonmode==True):
            # open file to read lang
            jdata = json.load(file(ifile),encoding='UTF-8')
            if 'lang' in jdata:
                lang = jdata['lang']
                jsonmode = True
            else:
                sys.exit('Error: JSON file doesn\'t specify lang.')
        else:
            lcfile = os.path.basename(ifile.lower());
            if lcfile.startswith('english') or lcfile.startswith('en') or '.en.' in lcfile:
                lang = 'en'
            elif lcfile.startswith('spanish') or lcfile.startswith('es') or '.es.' in lcfile:
                lang = 'es'
            elif lcfile.startswith('russian') or lcfile.startswith('ru') or '.ru.' in lcfile:
                lang = 'ru'
            elif lcfile.startswith('persian') or lcfile.startswith('fa') or '.fa.' in lcfile:
                lang = 'fa'
            else:
                sys.exit('Error: unrecognized file language type.');

        tags = args['tag']
        if tags in tagtrans:
            if lang in tagtrans[tags]:
                tags = tagtrans[tags][lang]

        resultscwd = resultsdir[lang]
        provenance = corpusname[lang]
        if args['provenance']:
            provenance= args['provenance']
        
        ofilename = ifile + '.wiki';
        data = codecs.open(ifile, encoding='utf-8')
        toFile = codecs.open(ofilename, encoding='utf-8', mode='w')

        lines = list()
        for line in data:
            lines.append(line)
        data.close()

        if jsonmode:
            if "sentences" in jdata==False:
                continue
            if len(jdata["sentences"]) < 1:
                continue
            # create lm to sentence index
            lmlist = {}
            for sindex in range(0, len(jdata['sentences'])):
                sent = jdata['sentences'][sindex]
                if "lms" not in sent:
                    continue
                for lm in sent['lms']:
                    if lm['name'] in lmlist:
                        lmlist[lm['name']]['examples'].append(sindex)
                    else:
                        lmlist[lm['name']] = {'name':lm['name'],
                                              'source':lm['source']['lemma'],
                                              'target':lm['target']['lemma']}
                        if 'seed' in lm:
                            lmlist[lm['name']]['seed'] = lm['seed']
                        if 'rel' in lm['target']:
                            lmlist[lm['name']]['tgrel'] = lm['target']['rel']
                        lmlist[lm['name']]['examples'] = []
                        lmlist[lm['name']]['examples'].append(sindex)
            # loop through lms
            for lmname in lmlist.keys():
                lm = lmlist[lmname]
                # rudimentary annotation
                rel = 'subj'
                if 'tgrel' in lm:
                    if lm['tgrel'].startswith('obj'):
                        rel = 'obj'
                    annotation = lm['source']+'=pred(Source),'+lm['target']+'='+rel+'(Target)'
                else:
                    annotation = ""
        
                fullname = u'Linguistic metaphor:' + lm['name'].capitalize()
                if rel=='obj':
                    fullname = u'Linguistic metaphor:' + flip_order(lm['name']).capitalize()
                
                # if there is a trailing : it is a seed
                isSeed = 0
                type = 'extracted'
                if 'seed' in lm:
                    if (lm['seed']==u'None' or lm['seed']==u'NA'):
                        type = 'other'
                    else:
                        seedname = u'Linguistic metaphor:' + lm['seed'].capitalize()
                        if rel=='obj':
                            seedname = u'Linguistic metaphor:' + flip_order(lm['seed']).capitalize()
                else:
                    type = 'seed'

                # Write Template Data
                comments = ""
        
                toFile.write(u'xxxx\n')
                toFile.write(u'\'\'\''+fullname+'\'\'\'\n')
                toFile.write(u'{{Linguistic metaphor')
                toFile.write(u'\n|Type='+type)
                # refer to seed if it is purely extracted
                if (type == 'extracted'):
                    toFile.write(u'\n|Seed='+seedname)
                toFile.write(u'\n|Source='+lm['source'])
                toFile.write(u'\n|Target='+lm['target'])
                toFile.write(u'\n|Examples=')

                numex = 0;
                if 'examples' in lm:
                    for sentind in lm['examples']:
                        if numex >= maxsents:
                            comments = 'Imported %d examples out of %d.' % (maxsents,len(lm['examples']))
                            break
                        sent = jdata['sentences'][sentind]['text']
                        sentid = jdata['sentences'][sentind]['id']
                        if ":" in sentid:
                            provenance = sentid
                        toFile.write(u'{{Example');
                        toFile.write(u'\n|Example.Text='+sent.strip().replace('|','{{!}}'));
                        toFile.write(u'\n|Example.Annotation='+annotation)
                        toFile.write(u'\n|Example.Provenance='+provenance)
                        toFile.write(u'\n|Example.Language='+language[lang])
                        toFile.write(u'\n}}')
                        numex = numex + 1
                else:
                    sys.stderr.write("Warning:"+fullname+" does not have any examples.\n")
                        
                toFile.write(u'\n|Tags='+tags)
                toFile.write(u'\n|Comments='+comments)
                toFile.write(u'\n|Entered by='+botname)
                toFile.write(u'\n|Status=auto imported')
                toFile.write(u'\n}}\n')
                toFile.write(u'yyyy\n')
            toFile.close()
            continue    
                
        elif lang == 'fa':
            # Persian special case        
            readSentence = False
            readNgrams = True
            ngrams = list()
            sentence = u"";
            for a in range(0, len(lines)):
                # lop off newline at end
                line = lines[a].strip()
                
                if (line[:4] == '===='):
                    # write metaphors out to file
                    for ngram in ngrams:
                        toFile.write(u'xxxx\n')
                        toFile.write(u'\'\'\'Linguistic metaphor:'+
                                     ngram['fullname']+'\'\'\'\n')
                        toFile.write(u'{{Linguistic metaphor')
                        toFile.write(u'\n|Type=extracted')
                        toFile.write(u'\n|Source='+ngram['source'])
                        toFile.write(u'\n|Target='+ngram['target'])
                        toFile.write(u'\n|Examples=')
                        #there's only on example
                        toFile.write(u'{{Example');
                        toFile.write(u'\n|Example.Text='+sentence.strip().replace('|','{{!}}'));
                        toFile.write(u'\n|Example.Provenance='+corpusname[lang])
                        toFile.write(u'\n|Example.Language='+language[lang])
                        toFile.write(u'\n|Example.Annotation='+
                                     ngram['source']+u'=Source,'+
                                     ngram['target']+u'=Target')
                        toFile.write(u'\n}}')        
                        toFile.write(u'\n|Tag='+tags)
                        toFile.write(u'\n|Entered by='+botname)
                        toFile.write(u'\n|Status=auto imported')
                        toFile.write(u'\n}}\n')
                        toFile.write(u'yyyy\n')
                    readNgrams = True
                    readSentence = False
                    sentence = u""
                    ngrams = list()
                    continue

                if (readSentence):
                    sentence += " " + line

                if (line == u""):
                    continue

                if (line[:4] == u'Sent'):
                    readNgrams = False
                    readSentence = True
                    continue

                if (readNgrams):
                    # start reading metaphors
                    prog = re.compile('\w+', re.U)
                    words = prog.findall(line)
                    #if len(words) > 2:
                    #    sys.stderr.write('Skipping ngram with '+
                    #       str(len(words))+' words:'+line+'\n')
                    ngrams.append({'source': words[0],
                                   'target':words[1],
                                   'fullname':line})
            toFile.close()
            continue

        # all other languages besides Persian

        seed = ''
        gramrel = ''
        for a in range(0, len(lines)):
            # skip dashed lines
            if ((lines[a])[:3] == '---'):
                gramrel = objrel[lang]
                continue

            # pull out all word matches
            prog = re.compile('\w+', re.U)
            words = prog.findall(lines[a])
            if ((lines[a])[-3:-1] == '-:'):
                target = words[0]
                source = words[1]
                gramrel = subjrel[lang]
            else:
                target = words[1]
                source = words[0]
            # all our source are v / all our target are n
            verb = source
            noun = target
            target = noun + '.n'
            source = verb + '.v'

            # rudimentary annotation
            annotation = source+'=pred(Source),'+target+'='+gramrel+'(Target)'
        
            # construct name of linguistic metaphor
            name = words[0] + ' ' + words[1]
            fullname = 'Linguistic metaphor:' + name.capitalize()
        
            # if there is a trailing : it is a seed
            isSeed = 0
            type = 'extracted'
            if ((lines[a])[-2:-1] == ':'):
                isSeed = 1
                type = 'seed'
                seed = fullname
            else:
                if (fullname == seed):
                    type = 'seed'
                else:
                    type = 'extracted'

            # Write Template Data
            comments = ""
        
            toFile.write(u'xxxx\n')
            toFile.write(u'\'\'\''+fullname+'\'\'\'\n')
            toFile.write(u'{{Linguistic metaphor')
            toFile.write(u'\n|Type='+type)
            # refer to seed if it is purely extracted
            if (type == 'extracted'):
                toFile.write(u'\n|Seed='+seed)
            toFile.write(u'\n|Source='+source)
            toFile.write(u'\n|Target='+target)
            toFile.write(u'\n|Examples=')
        
            # look up examples using script
            # don't examples for russian--takes too long
            if (maxsents > 0) and (lang != 'ru'):
                sents = "";
                try:
                    if (textdoc != ''):
                        sents = unicode(
                            subprocess.check_output(['GetTextSentences.py',
                                                     textdoc,gramrel,
                                                     verb,noun]),'utf-8')
                    else:
                        sents = unicode(
                            subprocess.check_output(['./findrel', gramrel,
                                                     verb, noun],
                                                    cwd=resultscwd),'utf-8')
                except subprocess.CalledProcessError:
                    sys.stderr.write('Error looking up examples for '+
                                     fullname+'\n');
                if sents is not u"" or None:
                    sentlist = sents.splitlines()
                    if len(sentlist) == 0:
                        sys.stderr.write("Warning:"+fullname+" has 0 examples.\n")
                    else:
                        sys.stderr.write('%s has %d examples.\n' % (fullname,len(sentlist)))
                    numex = 0;
                    for sent in sentlist:
                        if numex >= maxsents:
                            comments = 'Imported %d examples out of %d.' % (maxsents,len(sentlist))
                            break
                        toFile.write(u'{{Example');
                        toFile.write(u'\n|Example.Text='+sent.strip().replace('|','{{!}}'));
                        toFile.write(u'\n|Example.Annotation='+annotation)
                        toFile.write(u'\n|Example.Provenance='+provenance)
                        toFile.write(u'\n|Example.Language='+language[lang])
                        toFile.write(u'\n}}')
                        numex = numex + 1
                else:
                    sys.stderr.write("Warning:"+fullname+" does not have any examples.\n")
                        
            toFile.write(u'\n|Tag='+tags)
            toFile.write(u'\n|Comments='+comments)
            toFile.write(u'\n|Entered by='+botname)
            toFile.write(u'\n|Status=auto imported')
            toFile.write(u'\n}}\n')
            toFile.write(u'yyyy\n')
        toFile.close()
    sys.exit(0)

def flip_order(line):
    words = line.split()
    c = words[1]
    words[1] = words[0]
    words[0] = c
    return u' '.join(words)

if __name__ == '__main__':
    main()
