#!/usr/bin/python
# -*- coding: utf-8 -*-

""" provides a stemmer, a stopword list, and a method to clean the text from non-Farsi text.

The stemmer is a reimplementation of Ljiljana Dolamic & Jacques Savoy's stemmer:
http://members.unine.ch/jacques.savoy/clef/index.html

The stopword list is the normalized list of Ljiljana Dolamic & Jacques Savoy with some additional words.
"""

import re
import codecs
import regex

__author__ = "Aida Nematzadeh"
__email__ = "aida@cs.toronto.edu"
__credits__ = ["Ljiljana Dolamic", "Jacques Savoy"]




class Stemmer:

    def __init__(self, stopword_path):
        self.stopwords = self.read_stopwords(stopword_path)
            
    def read_stopwords(self,path):
        sw_file = codecs.open(path, 'r', encoding='utf-8')
        stopwords = set([])
        for line in sw_file:
            stopwords.add(line.strip())
        return stopwords
    
    def clean_text(self, text):
        "Remove anything other than Arabic letters in text \
        (such as punctuations, symbols, and numbers" 
        return regex.sub(ur"(\p{N}|[^\p{Arabic} \u200C])+", " ", text)

    
    def valid_word(self, word):
        word = self.clean_text(word)
        if len(word.strip()) == 0: return False
        
        if word in self.stopwords: return False
        
        word  = self.stem(word)
        if word in self.stopwords: return False
        
        if len(word) <=2 : return False
        return True



    def stem(self, word):
        "returns the stem of the word"

        word = self.remove_kasra(word)
        word = self.remove_suffix(word)
        word = self.remove_kasra(word)
        word = self.remove_nimfasele(word)
        return word.strip()

    def remove_nimfasele(self, word):
        return word.strip(u'\u200C')
    
    def remove_kasra(self, word):
        if len(word) < 5:
            return word
        return word.strip('\u0650')
    
    
    def lremove(self, word, pattern):
        "remove the string st from the end of the word"
        return re.sub('%s$' % pattern, u"", word)

    def remove_suffix(self, word):
        length = len(word)

        if length > 7:
            for ending in [u"آباد", u"باره", u"بندی",  u"بندي", u"ترین", u"ترين", u"ریزی",\
            u"ريزي", u"سازی", u"سازي", u"گیری", u"گيري", u"هایی", u"هايي"]:
                if word.endswith(ending):
                    return self.lremove(word, ending)

        if length > 6:
            for ending in [u"اند", u"ایم", u"ايم", u"شان", u"های", u"هاي"]:
                if word.endswith(ending):
                    return self.lremove(word, ending)
        
        if length > 5:
            if word.endswith(u"ان"):
                word = self.lremove(word, u"ان")
                return self.normalize(word)

            for ending in [u"ات", u"اش", u"ام", u"تر", u"را", u"ون", u"ها", u"هء", u"ین", u"ين"]:
                if word.endswith(ending):
                    return self.lremove(word, ending)

        if length > 3:
            for ending in [u"ت", u"ش", u"م", u"ه", u"ی", u"ي"]:
                if word.endswith(ending):
                    return word.strip(ending)

        return word

    def normalize(self, word):
        if len(word) < 4:
            return word

        for ending in [u"ت", u"ر", u"ش", u"گ", u"م", u"ى"]:
            word = word.strip(ending)
            
            if len(word) < 4: 
                return word

            if word.endswith(u"ی") or word.endswith(u"ي"):
                return word[:-1]

        return word
