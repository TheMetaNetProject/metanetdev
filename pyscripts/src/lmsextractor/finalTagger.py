import codecs
#"'.*',encoding=utf-8'"

def hmm_tagger(text,fpOne,fpTwo):
    import math

    #fpOne = codecs.open(repDir + '/bigramProb.txt','r','utf-8').read()
    #fpTwo = codecs.open(repDir + '/lexProb.txt','r','utf-8').read()

    tag_list = ['V','POSTP','IDEN','PART','ADR','POSNUM','PSUS','PR','N','ADJ','ADV','PREM','PREP','CONJ','PUNC','PRENUM','SUBR']

    sntnc_list = text.split(".")

    bigram_tag_prob = fpOne.split()
    bigram_tag_prob.remove(bigram_tag_prob[0])

    lex_prob = fpTwo.split("*")
    lex_prob.remove(lex_prob[0])

    firstWord = sntnc_list[0].split()[0]
    if firstWord[0] == u"﻿":
        sntnc_list.insert(0,sntnc_list[0][1:])
        sntnc_list.remove(sntnc_list[1])

    period = False
    if sntnc_list[-1] == u' ' or sntnc_list[-1] == '' :
        period = True
        sntnc_list.remove(sntnc_list[-1])

    tag_word = []
    for i in range(len(sntnc_list)):

        word = sntnc_list[i].split()

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
                s = lex_prob.index(word[0] + tag_list[i]) + 1
                z = math.log10(float(bigram_tag_prob[j])) + math.log10(float(lex_prob[s]))

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
                    score = lex_prob.index(word[j] + tag_list[k])+1
                    max_score = max(scoreTwo) + math.log10(float(lex_prob[score]))

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
                if word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + "V" in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + "/"+tag_list[backTrace[counter+2]])

                elif word[counter] + ' ' + word[counter+1] + 'V' in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + "/"+tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                elif word[counter+1] + ' ' + word[counter+2] + 'V' in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + "/"+tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + ' ' + word[counter+2] + "/"+tag_list[backTrace[counter+2]])

                else:
                    jump = 0
                    tag_word.append(word[counter]+"/"+tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1]+"/"+tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2]+"/"+tag_list[backTrace[counter+2]])

            elif length > 3 and (counter <= len(word)-3 and tag_list[backTrace[counter]] == 'ADJ' and tag_list[backTrace[counter+1]] == 'ADJ' and tag_list[backTrace[counter+2]] == 'V'):
                if word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + 'V' in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + ' ' + word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                elif word[counter+1] + ' '+word[counter+2] + 'V' in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + ' ' + word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                else:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + "/" + tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

            elif length > 3 and (counter <= len(word)-3 and tag_list[backTrace[counter]] == 'ADJ' and tag_list[backTrace[counter+1]] == 'V' and tag_list[backTrace[counter+2]] == 'V'):
                if word[counter] + ' '+word[counter+1] + ' '+word[counter+2] + 'V' in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + ' '+word[counter+1] + ' ' + word[counter+2] + "/"+tag_list[backTrace[counter+2]])

                elif word[counter+1] + ' ' + word[counter+2] + 'V' in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + ' '+word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                elif word[counter] + ' ' + word[counter+1] + 'V' in lex_prob:
                    jump = 0
                    tag_word.append(word[counter] + ' ' + word[counter+1] + "/" + tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

                else:
                    jump = 0
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + "/" + tag_list[backTrace[counter+1]])
                    tag_word.append(word[counter+2] + "/" + tag_list[backTrace[counter+2]])

            elif length > 2 and (counter <= len(word)-2 and tag_list[backTrace[counter]] == 'ADJ' and tag_list[backTrace[counter+1]] == 'V'):
                if word[counter] + ' ' + word[counter+1] + 'V' in lex_prob:
                    jump = 1
                    tag_word.append(word[counter] + ' ' + word[counter+1] + "/" + tag_list[backTrace[counter+1]])

                else:
                    jump = 1
                    tag_word.append(word[counter] + "/" + tag_list[backTrace[counter]])
                    tag_word.append(word[counter+1] + "/" + tag_list[backTrace[counter+1]])

            elif length > 2 and (counter <= len(word)-2 and tag_list[backTrace[counter]] == 'V' and tag_list[backTrace[counter+1]] == 'V'):
                if word[counter] + ' ' + word[counter+1] + 'V' in lex_prob:
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

        if period == True:
            tag_word.append("."+'/'+'PUNC')

        #    for i in tag_word:
        #        print i

    return tag_word
