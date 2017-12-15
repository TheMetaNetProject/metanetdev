"""
.. module:: findmet
    :platform: Unix
    :synopsis: Metaphor extraction.

    This file takes a relation type, a verb-noun pair as a seed, and an output file
    name and generates metaphorical expressions based on a clustering algorithm. See
    the usage() function for more details.
    
    All of the cluster files and potential metaphor files have already been generated
    from a parsed Russian web blog corpus.
    
    Created on October 24, 2012

.. moduleauthor:: ChrisXie, Luca Gilardi <lucag@icsi.berkeley.edu>
"""

from __future__ import print_function

import sys, argparse
from codecs import open
from util import uwriter, Environment, derivations, update, uopen, dprint

from pprint import pprint, pformat

ustderr = uwriter(sys.stderr)

env = Environment({'BASE': '/u/metanet/corpolexica/RU/RU-WAC/Russian Metaphor Extraction',
                   'GW': '/u/metanet/Parsing/Results/GW',
                   'BNC': '/u/metanet/corpolexica/EN',
                   'DEMO': '/u/metanet/demo',
                   'SEED_DIR': '/u/metanet/extraction/seeds'})

def main():
    parser = create_parser()
    name_space = parser.parse_args()
    args = vars(name_space)

    language = args['language']
    rel_type = args['rel_type']
    verb_seed = args['verb']
    noun_seed = args['noun']
    output_file_name = args['output_file_name']

    # Potential metaphor files
    met_fname = {'en': {'verb-object': env("{BNC}/bnc-relations/DirectObjRels.txt-uniqed-sorted"),
                        'verb-subject': env("{BNC}/bnc-relations/SubjectRels.txt-uniqed-sorted")},
                 'es': {'verb-object': env("{GW}/es/dobj"),
                        'verb-subject': env("{GW}/es/subj")},
                 'ru': {'verb-object': env("{BASE}/verbObjUniq.txt"),
                        'verb-subject': env("{BASE}/verbSubjUniq.txt")}}

    search_metaphors(language, rel_type, verb_seed, noun_seed, open(met_fname[language][rel_type], encoding='utf-8'), output_file_name)


def read_clusters(iterable, op=None):
    """Returns a map cluster-name -> word-list.
    """
    return dict((r[0], op(r[1:]) if op else r[1:]) for r in iterable)

def reltype(sline):
    """Extracts a (rel_type, noun, verb) triple.
    """
    return ('verb-object', sline[2], sline[1]) if sline[0] == '-' else ('verb-subject', sline[0], sline[1])

cluster = dict(ru=(env('{BASE}/clusterslist_RU_uncollapsed_noun.txt'),
                   env('{BASE}/clusterslist_RU_uncollapsed_verb.txt')),
               es=(env('{DEMO}/clusters/es/Noun_Clusters_uncollapsed.utf8.txt'),
                   env('{DEMO}/clusters/es/Verb_Clusters_uncollapsed.utf8.txt')),
               en=(env('{DEMO}/clusters/en/Noun_Clusters.txt'),
                   env('{DEMO}/clusters/en/Verb_Clusters.txt')))

def build_metaphors(seeds, nclusters, vclusters):
    def find(seed, clusters):
        cnames = [cname for cname, words in clusters.items() if seed in words]
        return cnames[0] if cnames else None

    mm = dict()
    orphans = []
    for seed in seeds:
        reltype, nseed, vseed = seed
        nn, vn = find(nseed, nclusters), find(vseed, vclusters)
#         dprint(seed, nn, vn)
        if nn and vn: 
            new_nvpairs = dict(((n, v), seed) for n in nclusters[nn] for v in vclusters[vn])
#             assert(all((n, v) not in mm for n, v in new_nvpairs)), pformat((new_nvpairs, mm))
            # TODO: the following removes info about the seed if there's an <n, v> collision.
            mm.update(new_nvpairs)
        else:
            orphans.append(seed)
    return mm, orphans


class MetaphorBuilder(object):
    """Builds all possible metaphors from seeds and clusters.
    """
    def __init__(self, lang, nclusters, vclusters, seeds):
        metaphors, orphans = build_metaphors(seeds, nclusters, vclusters)
        update(self, metaphors=metaphors, orphans=orphans)

    def find(self, relations):
#        return [(n, v) for _, n, v in relations if (n, v) in self.metaphors]
        mm = self.metaphors
        return [(n, v) + mm[(n, v)] for n, v in relations if (n, v) in mm]
#        return [(nv, seed) for nv, seed in self.metaphors if nv in relations]

    def dump(self, stream=uwriter(sys.stderr)):
        for n, v in self.metaphors:
            print(u'{0[0]}.{0[1]} {1[0]}.{1[1]}'.format(n, v), file=stream)

def extended(tcluster):
    ext = set(tcluster)
    for w, _ in tcluster:
        ext.update((unicode(l.name.lower()), l.synset.pos) for l in derivations(w))
    return ext

def tagged(words, tag):
    return [(w, tag) for w in words]

def test_m():
    from util import read_seed, N, V
    lang = 'en'
    rels = [(u'1', (u'debt', 'n'), (u'kill', 'v')),
            (u'1', (u'poverty', 'n'), (u'hurl', 'v'))]
    seeds = read_seed(uopen(env('{SEED_DIR}/{LANG}/{SEEDS}', SEEDS='seeds.ei', LANG=lang)))
    noun_file, verb_file = cluster[lang]
    def tag_ext(tag):
        return lambda words: extended(tagged(words, tag))
    nclusters = read_clusters(uopen(noun_file), tag_ext(N))
    vclusters = read_clusters(uopen(verb_file), tag_ext(V))
    m = MetaphorBuilder(lang, nclusters, vclusters, seeds)
    pprint(m.find(rels))
    
    
# =========================================
# Below is what remains of Chris Xie's code
# =========================================

# TODO: perhaps remove?

def search_metaphors_ex(language, rel_type, verb_seed, noun_seed, relations, debug=False):
    # Set the encoding scheme, cluster files, and potential metaphor files depending on the language
    encoding = 'utf-8'
    if language.lower() in ('russian', 'ru'):
        noun_cluster_file = env("{BASE}/clusterslist_RU_uncollapsed_noun.txt")
        verb_cluster_file = env("{BASE}/clusterslist_RU_uncollapsed_verb.txt")
    elif language.lower() in ('spanish', 'es'):
        noun_cluster_file = env("{DEMO}/clusters/es/Noun_Clusters_uncollapsed.utf8.txt")
        verb_cluster_file = env("{DEMO}/clusters/es/Verb_Clusters_uncollapsed.utf8.txt")
    elif language.lower() in ('english', 'en'):
        noun_cluster_file = env("{DEMO}/clusters/en/Noun_Clusters.txt")
        verb_cluster_file = env("{DEMO}/clusters/en/Verb_Clusters.txt")
    else:
        print >> ustderr, ">>> Language '{}' not recognized! Please input a language of choice: English, Russian, Spanish".format(language)
        sys.exit(0)

    N, V, S, A = 'nvsa'  # @UnusedVariable
    noun_clusters = dict((k, extended(tagged(v, N))) for k, v in parse_noun_cluster_file(noun_cluster_file, encoding).items())
    verb_clusters = dict((k, extended(tagged(v, V))) for k, v in parse_verb_cluster_file(verb_cluster_file, encoding).items())

#     print 'potential metaphors'
#     print '-' * 72
    metaphors = populate_potential_metaphor_list_ex(noun_clusters, verb_clusters, verb_seed, noun_seed, debug)
#     pprint(metaphors)
#     print 'relations'
#     print '-' * 72
#     pprint(relations)
    found = [(n, v) for _, n, v in relations if (n, v) in metaphors]
#     print '-' * 72
#     pprint(found)
    return found


def search_metaphors(language, rel_type, verb_seed, noun_seed, pfile, output_file_name=None):
    # Set the encoding scheme, cluster files, and potential metaphor files depending on the language
    if language.lower() in ('russian', 'ru'):
        encoding = 'utf-8'
        noun_cluster_file = env("{BASE}/clusterslist_RU_uncollapsed_noun.txt")
        verb_cluster_file = env("{BASE}/clusterslist_RU_uncollapsed_verb.txt")

    elif language.lower() in ('spanish', 'es'):
#        encoding = 'latin-1'
        encoding = 'utf-8'
        noun_cluster_file = env("{DEMO}/clusters/es/Noun_Clusters_uncollapsed.utf8.txt")
        verb_cluster_file = env("{DEMO}/clusters/es/Verb_Clusters_uncollapsed.utf8.txt")

    elif language.lower() in ('english', 'en'):
        encoding = 'utf-8'
        noun_cluster_file = env("{DEMO}/clusters/en/Noun_Clusters.txt")
        verb_cluster_file = env("{DEMO}/clusters/en/Verb_Clusters.txt")

    else:
        print >> ustderr, ">>> Language '{}' not recognized! Please input a language of choice: English, Russian, Spanish".format(language)
        sys.exit(0)

    noun_clusters = parse_noun_cluster_file(noun_cluster_file, encoding)
    verb_clusters = parse_verb_cluster_file(verb_cluster_file, encoding)
    potential_metaphors = populate_potential_metaphor_list(noun_clusters, verb_clusters, verb_seed, noun_seed)

    # Create an output file and write out discovered metaphors to file
    #    pfile = open(potential_met_file, 'r', encoding='utf-8')
    # Just for spanish stuff
#    pfile = open(potential_met_file, 'r', encoding=encoding)

    if output_file_name != None:
        if not output_file_name.endswith('.txt'):
            print >> ustderr, ">>> Output File name must have .txt extension!"
            sys.exit(1)
#        output_file = open(output_file_name, 'w', encoding='utf-8')
        # Just for spanish stuff
        output_file = open(output_file_name, 'w', encoding=encoding)
        output_file.write("Original Seed is: " + verb_seed + " - " + noun_seed + "\n\n")
        output_file.write("Here are the discovered metaphors:\n")

    line = pfile.readline()

#    if output_file_name != None:
#        print "Searching for metaphors and saving to output file..."
#    else:
#        print "Searching for metaphors..."

    found = []
    index = 0
    while line != '':

        # Check for blank lines
        if line == '\n':
            line = pfile.readline()
            continue
        line = line.strip()

        # Only for Spanish and English Clusters
        if language.lower() != 'russian':
            line = line.split()
            if len(line) != 3:
                line = pfile.readline()
                continue
            l = line[2] + ' - ' + line[1]

        # Search potential metaphor list
        if l in potential_metaphors:
            if output_file_name != None:
                output_file.write("\t" + line + "\n")
            found.append(line)
            index += 1

        line = pfile.readline()
        # End while loop
#    print "Found {0} metaphors!".format(index)
    return found

    # End main()

def parse_noun_cluster_file(noun_cluster_file, encoding_scheme):
    # Populate the noun_cluster dictionary
    noun_clusters = {}
    nfile = open(noun_cluster_file, 'r', encoding=encoding_scheme)
    line = nfile.readline()
    while line != '':
        line = line.strip().split()
        noun_clusters[line[0]] = line[1:]
        line = nfile.readline()
    nfile.close()
    return noun_clusters

def parse_verb_cluster_file(verb_cluster_file, encoding_scheme):
    # Populate the verb_cluster dictionary
    verb_clusters = {}
    vfile = open(verb_cluster_file, 'r', encoding=encoding_scheme)
    line = vfile.readline()
    while line != '':
        line = line.strip().split()
        verb_clusters[line[0]] = line[1:]
        line = vfile.readline()
    vfile.close()
    return verb_clusters


def populate_potential_metaphor_list(noun_clusters, verb_clusters, verb_seed, noun_seed, debug=False):
    potential_metaphors = []
    verb_cluster_name = None
    noun_cluster_name = None

    # Search verb and noun clusters
    for cluster in verb_clusters.keys():
        if verb_seed in verb_clusters[cluster]:
            verb_cluster_name = cluster
            break

    for cluster in noun_clusters.keys():
        if noun_seed in noun_clusters[cluster]:
            noun_cluster_name = cluster
            break

    if verb_cluster_name and noun_cluster_name:
        # If they exist, store all combinations in potential metaphors list
        for _verb in verb_clusters[verb_cluster_name]:
            for _noun in noun_clusters[noun_cluster_name]:
                potential_metaphors.append(_verb + ' - ' + _noun)
    elif debug:
        print >> ustderr, u">>> Clusters for verb {} and/or noun {} don't exist".format(verb_seed, noun_seed)

    return potential_metaphors


def populate_potential_metaphor_list_ex(noun_clusters, verb_clusters, verb_seed, noun_seed, debug=False):
    potential_metaphors = set()
    verb_cluster_name = None
    noun_cluster_name = None

    # Search verb and noun clusters
    for cluster in verb_clusters.keys():
        if verb_seed in verb_clusters[cluster]:
            verb_cluster_name = cluster
            break

    for cluster in noun_clusters.keys():
        if noun_seed in noun_clusters[cluster]:
            noun_cluster_name = cluster
            break

    if verb_cluster_name and noun_cluster_name:
        # If they exist, store all combinations in potential metaphors list
        for v in verb_clusters[verb_cluster_name]:
            for n in noun_clusters[noun_cluster_name]:
                potential_metaphors.add((n, v))
    elif debug:
        print >> ustderr, u">>> Clusters for {} and/or {} don't exist".format(verb_seed, noun_seed)
#         pprint(noun_clusters, ustderr)
#         pprint(verb_clusters, ustderr)

    return potential_metaphors


def create_parser():
    """Creates a parser using the argparse module.
    """
    parser = argparse.ArgumentParser(description='Metaphor Search Using Metaphorical Seeds', epilog='--ChrisXie 2012.09.24')
    parser.add_argument('-l', '--language', required=True, choices=['english', 'spanish', 'russian'], dest='language', help='Required argument. Language must be one of the three choices and MUST BE LOWER CASE')
    parser.add_argument('-r', required=True, choices=['verb-subject', 'verb-object'], help='Required argument. Relation Type must be one of the two choices and MUST BE LOWER CASE', dest='rel_type')
    parser.add_argument('-v', '--verb', required=True, dest='verb', help='Required argument. Verb Seed')
    parser.add_argument('-n', '--noun', required=True, dest='noun', help='Required argument. Noun Seed')
    parser.add_argument('-o', '--output', dest='output_file_name', help='Optional argument. If this option is specified and an argument passed in, the output is written to a file created with this name in the current directory (or path, if specified). Please have the .txt extension at the end of the file name')

    return parser


if __name__ == "__main__":
    main()
#     test_m()
