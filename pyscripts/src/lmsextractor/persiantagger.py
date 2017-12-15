#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: persiantagger
    :platform: Unix
    :synopsis: Perisan HMM POS tagger
    
Part of speech tagger for Persian.  Precomputed distributional statistics such as
bigram probabilities are loaded by default from:

``/u/metanet/extraction/persian``

This path can be altered via a parameter to the constructor method.

"""
import codecs, logging, re, os
import cPickle as pickle

REPDIR = '/u/metanet/extraction/persian'

class PersianPOSTagger:
    """
    A Persian POS tagger which uses the unigram and bigram lexical and tag
    sequence probabilities and finds the best tag sequence using 
    Viterbi decoding
    """
    tag_list = ['V','POSTP','IDEN','PART','ADR','POSNUM','PSUS','PR','N','ADJ','ADV',
                'PREM','PREP','CONJ','PUNC','PRENUM','SUBR']
    
    def __init__(self, repDir=None):
        """
        :param repDir: path to the directory to load precomputed distributional statistics
        :type repDir: str
        """
        global REPDIR
        # for pos tagger
        if repDir:
            self.repDir = repDir
        else:
            self.repDir= REPDIR
        self.cachef = '%s/tagger.cache' % (self.repDir)
        self.fpOne = codecs.open(self.repDir + '/bigramProb.txt','r','utf-8').read()
        self.fpTwo = codecs.open(self.repDir + '/lexProb.txt','r','utf-8').read()
        self.logger = logging.getLogger("PersianPOSTagger")
        self.logger.setLevel(logging.DEBUG)

        self.reList = [(ur'^"', ur'`` '),
                       (ur'([ (\[{<])"', ur'\1 `` '),
                       (ur'\.\.\.', ur' ... '),
                       (ur'[؛,;:@#$%&،»«؟]', ur' & '),
                       (ur'([^.])([.])([\])}>"\']*)[         ]*$', ur'\1 \2\3 '),
                       (ur'[?!]', ur' & '),
                       (ur'[\]\[(){}<>]', ur' & '),
                       (ur'--', ur' -- '),
                       (ur'$', ur' '),
                       (ur'^', ur' '),
                       (ur'"', ur' \'\' '),
                       (ur'  *', ur' '),
                       (ur'^ *', ur''),
                       (ur'/',ur'-')]
        self.cleanRes = []
        for (expr, subst) in self.reList:
            self.cleanRes.append((re.compile(expr, flags=re.U),subst))
        self.bigram_tag_prob = self.fpOne.split()
        self.bigram_tag_prob.remove(self.bigram_tag_prob[0])
        if os.path.exists(self.cachef):
            self.lex_prob_hash = self.load_lex_prob_cache()
        else:
            self.lex_prob_hash = self.preproc_lex_prob()
            
    def preproc_lex_prob(self):
        """
        Preprocesses the lexical probabilities and stoes them in 
        a dictionary
        """
        lex_prob = self.fpTwo.split("*")
        lex_prob.remove(lex_prob[0])
        lex_prob_hash = {}
        try:
            for i in range(0,len(lex_prob),2):
                if lex_prob[i] in lex_prob_hash:
                    continue
                else:
                    lex_prob_hash[lex_prob[i]] = float(lex_prob[i+1])
        except IndexError:
            self.logger.debug('Loop index exceeded %d' % (len(lex_prob)))
        with open(self.cachef,'wb') as cf:
            pickle.dump(lex_prob_hash,cf,2)
            cf.close()
        return lex_prob_hash

    def load_lex_prob_cache(self):
        """
        Loads the lexical probabilities in to a dictionary
        """
        lex_prob_hash = {}
        with open(self.cachef,'rb') as cf:
            lex_prob_hash = pickle.load(cf)
            cf.close()
        return lex_prob_hash

    def run_hmm_tagger(self, text):
        """
        A higher level function which calls the POS tagger on the input text
        and returns a tagged form of the text. Returns a taglist in 'word/TAG' format
        
        * this is to be able to maintain alignment even if we end up having to skip some sentences in the tagger.
        
        """
        import math
    
        tag_list = self.tag_list
        bigram_tag_prob = self.bigram_tag_prob
        lex_prob_hash = self.lex_prob_hash
        
        tag_word = []
        word = text.split()

        # SEPARATING PUNCTUATION FROM THE PREVIOUS WORD
        new_word = []
        cndtn = False
        for w in range(len(word)):
            if len(word[w]) > 1 and (word[w][-1] == u"." or word[w][-1] == u"!" or word[w][-1] == u"؟" or word[w][-1] == u"،" or word[w][-1] == u"؛" or word[w][-1] == u":" or word[w][-1] == u")" or word[w][-1] == u"("):
                cndtn = True
                new_word.append(word[w][:-1])
                new_word.append(word[w][-1])

            else:
                new_word.append(word[w])

        if cndtn == True:
            word = new_word

        # INITIALIZATION
        scoreOne = []
        j = 14
        for i in range (len(tag_list)):
            try:
                s = word[0] + tag_list[i]
                z = math.log10(float(bigram_tag_prob[j])) + math.log10(lex_prob_hash[s])

            except:
                z = math.log10(float(bigram_tag_prob[j])) + math.log10(0.0000000001)

            j += 17
            scoreOne.append(z)
            indx = scoreOne.index(max(scoreOne))

        scoreThree = []
        scoreTwo = []
        backTrace = [0]
        length = len(word)

        # ITERATION
        for j in range(1,len(word)):
            for k in range(len(tag_list)):
                for l in range (len(scoreOne)):
                    init = scoreOne[l] + math.log10(float(bigram_tag_prob[k*17+l]))
                    scoreTwo.append(init)
                try:
                    score = word[j] + tag_list[k]
                    max_score = max(scoreTwo) + math.log10(lex_prob_hash[score])

                except:
                    max_score = max(scoreTwo) + math.log10(0.0000000001)

                scoreTwo = []
                scoreThree.append(max_score)

            backTrace.append(scoreThree.index(max(scoreThree)))
            scoreOne = []
            scoreOne = scoreThree
            scoreThree = []

        # BACKTRACING
        counter = 1
        jump = False

        tag_word.append(word[0]+"/"+tag_list[indx])

        for m in range(1,len(word)):
            if counter > length-1:
                break

            # CONSIDERING COMPLEX VERBS
            if length > 3 and (counter <= len(word)-3 and tag_list[backTrace[counter]] == 'V' and tag_list[backTrace[counter+1]] == 'V' and tag_list[backTrace[counter+2]] == 'V'):
                if word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + "V" in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + "/"+tag_list[backTrace[counter+2]])

                elif word[counter] + ' ' + word[counter+1] + 'V' in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + "/"+tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                elif word[counter+1] + ' ' + word[counter+2] + 'V' in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + "/"+tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + ' ' + word[counter+2] + "/"+tag_list[backTrace[counter+2]])

                else:
                    jump = 0
                    tag_word.append(word[counter]+"/"+tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1]+"/"+tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2]+"/"+tag_list[backTrace[counter+2]])

            elif length > 3 and (counter <= len(word)-3 and tag_list[backTrace[counter]] == 'ADJ' and tag_list[backTrace[counter+1]] == 'ADJ' and tag_list[backTrace[counter+2]] == 'V'):
                if word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + 'V' in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                elif word[counter+1] + ' '+word[counter+2] + 'V' in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + ' ' + word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                else:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + "/" + tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

            elif length > 3 and (counter <= len(word)-3 and tag_list[backTrace[counter]] == 'ADJ' and tag_list[backTrace[counter+1]] == 'V' and tag_list[backTrace[counter+2]] == 'V'):
                if word[counter] + ' '+word[counter+1] + ' '+word[counter+2] + 'V' in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + ' '+word[counter+1] + ' ' + word[counter+2] + "/"+tag_list[backTrace[counter+2]])

                elif word[counter+1] + ' ' + word[counter+2] + 'V' in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + ' '+word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                elif word[counter] + ' ' + word[counter+1] + 'V' in lex_prob_hash:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + "/" + tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                else:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + "/" + tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

            elif length > 2 and (counter <= len(word)-2 and tag_list[backTrace[counter]] == 'ADJ' and tag_list[backTrace[counter+1]] == 'V'):
                if word[counter] + ' ' + word[counter+1] + 'V' in lex_prob_hash:
                    jump = 1
                    tag_word.append(word[counter] + ' ' + word[counter+1] + "/" + tag_list[backTrace[counter+1]])

                else:
                    jump = 1
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + "/" + tag_list[backTrace[counter+1]])

            elif length > 2 and (counter <= len(word)-2 and tag_list[backTrace[counter]] == 'V' and tag_list[backTrace[counter+1]] == 'V'):
                if word[counter] + ' ' + word[counter+1] + 'V' in lex_prob_hash:
                    jump = 1
                    tag_word.append(word[counter] + ' ' + word[counter+1] + "/" + tag_list[backTrace[counter+1]])
                else:
                    jump = 1
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + "/" + tag_list[backTrace[counter+1]])

            else:
                jump = 2
                tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])

            if jump == 0:
                counter += 3

            elif jump == 1:
                counter += 2

            elif jump == 2:
                counter += 1
                
        return tag_word


    def setLogLevel(self,lev):
        self.logger.setLevel(lev)
        
    def cleanText(self, text):
        for (reexp, substval) in self.cleanRes:
            text = reexp.sub(substval, text)
        return text
    
    def cleanSentences(self, sentences):
        slist = []
        for text in sentences:
            slist.append(self.cleanText(text))
        return slist
    
    def getWordList(self, otext, text, tags, pfield="pos", lfield="lem"):
        starting = 0
        idx = 0
        wlist = []
        for tag in tags:
            (form, pos) = tag.split('/',1)
            start = text.find(form, starting)
            if start >= 0:
                end = start + len(form)
                starting = end
            else:
                end = -1
            if (start >= 0) and (end >= 0):
                wform = otext[start:end]
            else:
                wform = form
            w = {'idx': idx,
                 'n': str(idx+1),
                 'form': wform,
                 pfield: pos,
                 lfield: form,
                 'start': start,
                 'end': end}
            wlist.append(w)
            idx += 1
        return wlist