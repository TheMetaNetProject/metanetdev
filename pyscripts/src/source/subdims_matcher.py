"""
.. module:: subdims_matcher
   :platform: Unix
   :synopsis: matches input LM source words to the correct IARPA source subdimension, given an IARPA source dimension
   
Main Routine: run1
   
Default usage: run1(input_LMs, input_dims)
 
Required Inputs: 
* input_LMs: a file of LM source words separated by whitespace or newlines
* input_dims: a file of IARPA souce dimensions separated by whitespace or
newlines;the n-th source dimension is assigned to the n-th LM source
word

(Optional Inputs; don't worry about these; they're set by default)
* master_dim_list: a two-level Python dictionary, where each entry
master_dim_list[dimension][subdimension] is a list of strings
with containing seed words for each IARPA subdimension
* BNC_mat: a matrix where each row is the semantic vector for a word in
a corpus
* BNC_vocab: a Python list containing the word labels for each row of
BNC_mat
 
Output:
* best_dims: a list of 3-tuples.  Each tuple contains:

    - the input source LM in the first position
    - the input IARPA source dimension in the second position
    - the predicted IARPA source subdimension in the third position

Uses precomputed cluster data stored in:

``/u/metanet/clustering/m4source/``

.. moduleauthor:: E.D. Gutierrez <edg@icsi.berkeley.edu>

"""
from nltk.corpus import stopwords
from sys import argv
import numpy
import scipy.spatial.distance
import scipy.io
import random
from nltk.stem.wordnet import WordNetLemmatizer
import nltk.stem.snowball
import csv
from gensim import corpora, models, similarities
# import
# from nltk import SnowballStemmer

# lang = 'english' #'english', 'russian', 'spanish'
agg_translation = False

def lemmatize(word, lang, lemm=True):
    if lemm:
        if lang == 'english':
            word = nltk.stem.snowball.EnglishStemmer(True).stem(WordNetLemmatizer().lemmatize(word))
        elif lang == 'spanish':
            word = nltk.stem.snowball.SpanishStemmer(True).stem(word)
        else:
            word = word.decode('utf-8')
            # nltk.stem.snowball.RussianStemmer(True).stem()
    else:
        pass
    return word.lower()

def file_to_list(filename, lang, lemm=True):
    file1 = open(filename, 'rb')
    list1 = []
    for line in file1:
        word1 = ''
        for word in line.split():
            if (lang == 'spanish') or (lang == 'english'):
                word1 += ' ' + lemmatize(word.decode('utf-8'), lang, lemm)
            else:
                word1 += ' ' + lemmatize(word, lang, lemm)
        list1.append(word1[1:])
    return list1

    
def file_to_dict(filename, langnum, lang, lemm=True):
    dim_list = {}
    with open(filename, 'r') as csvfile:
        for line in csvfile:  # reader = csv.reader(csvfile, delimiter = ',')
            count = 0
            row = line.split(',')
            try:
                dim_list[row[0].lower()][row[1].lower()] = []
            except:
                dim_list[row[0].lower()] = {}
                dim_list[row[0].lower()][row[1].lower()] = []
#            print row[0]+row[1]
            words = row[langnum].split('||')
            for word in words:
                if (lang == 'spanish') | (lang == 'english'):
                    dim_list[row[0].lower()][row[1].lower()].append(lemmatize(word.decode('utf-8'), lang, lemm))
                else:
                    dim_list[row[0].lower()][row[1].lower()].append(lemmatize(word, lang, lemm))
    return dim_list

def gendist(lsi_subdim, lsi_word, num_ft):
    dists = 1 - similarities.MatrixSimilarity(lsi_subdim, num_features = num_ft)[lsi_word][0]
    return dists[0]

# # DEFAULT GLOBAL VARIABLES
in_dir = '/u/metanet/clustering/m4source/'
# input_LMs_file = in_dir+'test_list_'+lang+'.txt' 
# input_dims_file = in_dir + 'test_list_dims_'+lang+'.txt'

def levstn(a, b):
    """ Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return (current[n] + .0000001) / numpy.max([n, m])


def avg_dist(vec, mat, dist, mean=numpy.mean, num_features = 1):
    def median_or_less(list1):
        list2 = numpy.zeros((len(list1), 1))
        counter = 0
        if len(list1) > 2:
            for item in list1:
                if item <= numpy.median(list1):
                    list2[counter] = item
                    counter += 1
            return list2[:counter]
        else:
            return list1
    if dist == levstn:
        d1 = numpy.zeros((len(mat), 1))
        for row in range(len(mat)):
            d1[row] = 1 - numpy.exp(-dist(mat[row], vec))
            if d1[row] < 1 - numpy.exp(-.2):
                d1[row] = -100
    elif dist == scipy.spatial.distance.cosine:
        d1 = numpy.zeros((mat.shape[0], 1))
        for row in range(mat.shape[0]):
            try:
                d1[row] = 1 - numpy.exp(-2 * dist(mat[row], vec))  # dist(mat[row,:], vec)
                if d1[row] < 1e-2:
                    d1[row] = -100
            except:
                d1[row] = 1 - numpy.exp(-2 * dist(mat, vec))  # dist(mat[row,:], vec)
                if d1[row] < 1e-2:
                    d1[row] = -100
    else:
        d1 = numpy.zeros((len(mat), 1))
        for row in range(len(mat)):
            d1[row] = 1 - numpy.exp(-2 * dist(mat[row], vec, num_ft = num_features))
            if d1[row] < 1e-2:
                d1[row] = -100
    d2 = mean(median_or_less(d1))  # (median_or_less(d1))))
    if numpy.isnan(d2):
#         print str(d2.shape[0])
        stop
    return d2

def populate_matrix(words, BNC_mat, BNC_vocab, lang, random_guess=False, verbose=False):
    if lang == 'english':
        BNC_mat.shape[1]
        out_mat = numpy.zeros((len(words), BNC_mat.shape[1]))
    else:
        out_mat = []
    count = 0
    for word in words:
        try:
            if lang == 'english':
                out_mat[count, :] = BNC_mat[BNC_vocab.index(word), :]
            elif len(BNC_vocab.doc2bow([word.encode('utf-8')])) > 0:
                out_mat.append(BNC_mat[[BNC_vocab.doc2bow([word.encode('utf-8')])]])
            else:
                raise TypeError
            count += 1
#            print "Subdim word found in BNC: " + str(word.encode('utf-8')) + '\n'
        except:
            if random_guess:
                out_mat[count, :] = BNC_mat[random.choice(range(200)), :]
                count += 1
            if verbose:
                print "Subdim word not found in BNC: " + str(word.encode('utf-8')) + '\t'
    if count == 0:
        if lang == 'english':
            out_mat[count, :] = BNC_mat[[(random.choice(range(1000)), 1)], :]
            count += 1
        else:
            out_mat.append(BNC_mat[[BNC_vocab.doc2bow([BNC_vocab.token2id.keys()[0]])]])
            
        if verbose:
            print 'No words found for subdim \n'
    try:
        return out_mat[:count, :]
    except:
        return out_mat
    
def create_dim_model(dims, BNC_mat, BNC_vocab, lang):
    dim_mat = {}
    for dim in dims:
#         print '\n\n' + dim + ':  \n'
        dim_mat[dim] = {}
        for subdim in dims[dim]:
            dim_mat[dim][subdim] = populate_matrix(dims[dim][subdim], BNC_mat, BNC_vocab, lang)    
    return dim_mat

def pick_subdim(word, dim, lang, IARPA_dim_mat, BNC_mat, master_dim_list, BNC_vocab, target, def_dist, verbose=False):
    wordfound = True
    try:
        if lang == 'english':
            vec = BNC_mat[BNC_vocab.index(word), :]  # or include some combination with the CM info here?
        else:
            ind1 = BNC_vocab.doc2bow([word.encode('utf-8')])
            if len(ind1) < 1:
                wordfound = False
            else:
                vec = BNC_mat[[ind1]]
    except:
        wordfound = False
    mindist = 1e10
    if wordfound:
        for subdim in master_dim_list[dim]:
     #       dist1, counter3 = 0 , 0, numpy.exp(-counter3) * 
            dist1 = avg_dist(vec, IARPA_dim_mat[dim][subdim], def_dist, num_features = len(BNC_vocab))
  #          counter3 += 1
            if verbose:
                print word + ' ' + subdim + ' ' + ("%.2f" % dist1) + '\n'
            if dist1 < mindist:
                best_dims = (word, dim, subdim)
                mindist = dist1
    else:
        if verbose:
            print "Word not found in BNC: ", word 
        for subdim in master_dim_list[dim]:
            dist1 = avg_dist(word, master_dim_list[dim][subdim], levstn, numpy.mean)
            if verbose:
                print word + ' ' + subdim + ' ' + ("%.2f" % dist1) + '\n'  
            if dist1 < mindist:
                best_dims = (word, dim, subdim)
                mindist = dist1
    if verbose:
        print '------------\n'
    if (wordfound == False) & (dist1 < 1e-1):
        wordfound = True
    return (best_dims, wordfound, mindist)

def subdim_match(lang, source, target, dim, verbose=False, in_dir='/u/metanet/clustering/m4source/'):
    """ Given an LM with the source concept identified.  Determine the best source dimension.
    """
    langnum = ['', '', 'english', 'russian', 'spanish'].index(lang)
    master_dim_list = file_to_dict(in_dir + 'master_dim_list_new.csv', langnum, lang)
    if lang == 'english':
        BNC_vocab = file_to_list(in_dir + 'lexicon_' + lang + '.txt', lang, lemm=False)
        BNC_mat = scipy.io.loadmat(in_dir + 'termtermmatrix_' + lang + '.mat')
        BNC_mat = BNC_mat['A']
        def_dist = scipy.spatial.distance.cosine
    else:
        BNC_vocab = corpora.Dictionary.load(in_dir + 'dictionary_' + lang + '.dict')
        BNC_mat = models.LsiModel.load(in_dir + 'model' + lang + '.lsi')
        def_dist = gendist
    IARPA_dim_mat = create_dim_model(master_dim_list, BNC_mat, BNC_vocab, lang)
    LMs_dim_mat = populate_matrix(source, BNC_mat, BNC_vocab, lang, random_guess=0)
    dist1 = 1e5
    for word in source.split():
        if lang == 'russian':
            word1 = lemmatize(word, lang, lemm=False)
        else:
            word1 = lemmatize(word.decode('utf-8'), lang, True)
        (a, b, c) = pick_subdim(word1, dim, lang, IARPA_dim_mat, BNC_mat, master_dim_list, BNC_vocab, target, def_dist, verbose)
        if word not in stopwords.words(lang):
            if c < dist1:
                best_dims = a
                wordfound = b
                dist1 = c
        else:
            if c < (dist1 - 2):
                best_dims = a
                wordfound = b
                dist1 = c
        if verbose:
            print word + ': ' + a[2] + ' ' + ("%.2f" % c) + '\n' 
    return (best_dims, wordfound)
