"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""

import time
import readline  # NOQA
import sys

# Uncomment to use C version of prefix edit distance calculation.
# You have to install the module using the provided ped_c/setup.py
# first.
from ped_c import ped

class QGramIndex:
    """
    A QGram-Index.
    """

    def __init__(self, q):
        '''
        Creates an empty qgram index.
        '''

        self.q = q
        self.inverted_lists = {}  # The inverted lists
        self.padding = "$" * (q - 1)
        self.entity_name = []
        self.entity_score = []
        self.entity_left = []

        # monetoring
        self.num_merg = 0
        self.num_res = 0
        self.num_ped = 0

    def build_from_file(self, file_name):
        '''
        Builds the index from the given file (one line per entity, see ES5).

        The entity IDs are one-based (starting with one).

        The test expects the index to store tuples (<entity id>, <frequency>),
        for each q-gram, where <entity id> is the ID of the entity the
        q-gram appears in, and <frequency> is the number of times it appears
        in the entity.

        For example, the 3-gram "rei" appears 1 time in entity 1 ("frei") and
        one time in entity 2 ("brei"), so its inverted list is
        [(1, 1), (2, 1)].

        >>> qi = QGramIndex(3)
        >>> qi.build_from_file("test.tsv")
        >>> sorted(qi.inverted_lists.items())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('$$b', [(2, 1)]), ('$$f', [(1, 1)]), ('$br', [(2, 1)]),
         ('$fr', [(1, 1)]), ('bre', [(2, 1)]), ('fre', [(1, 1)]),
         ('rei', [(1, 1), (2, 1)])]
        '''

        # Code from lecture 5
        with open(file_name, "r") as file:
            entity_id = 0

            first_line = True
            for line in file:
                # skip header
                if first_line:
                    first_line = False
                    continue

                entity_id += 1
                # split entity
                e_name, e_score, rest_of_line = line.strip().split("\t", 2)
                e_name = e_name.lower()
                self.entity_name.append(e_name)
                self.entity_score.append(int(e_score))
                self.entity_left.append(rest_of_line)


                for qgram in self.compute_qgrams(e_name):
                    h = self.inverted_lists
                    if qgram not in self.inverted_lists:
                        # If qgram is seen for the first time, create new list.
                        h[qgram] = [(entity_id, 1)]
                    else:
                        if h[qgram][-1][0] != entity_id:
                           h[qgram].append((entity_id, 1))  
                        else:
                            freq = h[qgram][-1][1]
                            h[qgram][-1] = (entity_id, freq + 1)

    def normalize(self, word):
        '''
        Normalize the given string (remove non-word characters and lower case).

        >>> qi = QGramIndex(3)
        >>> qi.normalize("freiburg")
        'freiburg'
        >>> qi.normalize("Frei, burG !?!")
        'freiburg'
        '''

        low = word.lower()
        return ''.join([i for i in low if i.isalnum()])

    def compute_qgrams(self, word):
        '''
        Compute q-grams for padded version of given string.

        >>> qi = QGramIndex(3)
        >>> qi.compute_qgrams("freiburg")
        ['$$f', '$fr', 'fre', 'rei', 'eib', 'ibu', 'bur', 'urg']
        '''
        pad_word = self.padding + word
        # number of records
        
        qgram = [None] * len(word)
        for i in range(0, len(word)):
            # store all records
            qgram[i] = pad_word[i:i +  self.q] 
        
        return qgram

    def merge_lists(self, lists):
        '''
        Merges the given inverted lists. The tests assume that the
        inverted lists keep count of the entity ID in the list,
        for example, in the first test below, entity 3 appears
        1 time in the first list, and 2 times in the second list.
        After the merge, it occurs 3 times in the merged list.

        >>> qi = QGramIndex(3)
        >>> qi.merge_lists([[(1, 2), (3, 1), (5, 1)],
        ...                 [(2, 1), (3, 2), (9, 2)]])
        [(1, 2), (2, 1), (3, 3), (5, 1), (9, 2)]
        >>> qi.merge_lists([[(1, 2), (3, 1), (5, 1)], []])
        [(1, 2), (3, 1), (5, 1)]
        >>> qi.merge_lists([[], []])
        []
        '''
        if len(lists) == 0:
            return []

        res = lists[0]
        for l in lists[1:]:
            h = []
            res_l = len(res)
            l_l = len(l)
            l_i = res_i = 0 
            while l_i < l_l and res_i < res_l:
                # until one list ends merge the items
                if l[l_i][0] < res[res_i][0]:
                    h.append(l[l_i])
                    l_i += 1
                elif l[l_i][0] > res[res_i][0]:
                    h.append(res[res_i])
                    res_i += 1
                else:
                    # sum up the frequenze
                    # (entity_id, frequenz)
                    h.append((res[res_i][0], res[res_i][1] + l[l_i][1]))
                    res_i += 1
                    l_i += 1
            
            # append the last part of the longer list
            if l_i < l_l:
                h.extend(l[l_i:])
            else:
                h.extend(res[res_i:])
            res = h
        return res


    def find_matches(self, prefix, delta):
        '''
        Finds all entities y with PED(x, y) <= delta for a given integer delta
        and a given (normalized) prefix x.

        The test checks for a list of triples containing the entity ID,
        the PED distance and its score:

        [(entity id, PED, score), ...]

        The entity IDs are one-based (starting with 1).

        >>> qi = QGramIndex(3)
        >>> qi.build_from_file("test.tsv")
        >>> qi.find_matches("frei", 0)
        [(1, 0, 3)]
        >>> qi.find_matches("frei", 2)
        [(1, 0, 3), (2, 1, 2)]
        >>> qi.find_matches("freibu", 2)
        [(1, 2, 3)]
        '''
        # monitoring
        self.num_ped = 0

        qg_pre = self.compute_qgrams(prefix)
        
        # all enterys for the qgrams of the prefix
        qg_match = []
        for qg in qg_pre:
           if qg in self.inverted_lists:
               qg_match.append(self.inverted_lists[qg])

        # compute total freq
        self.num_merg = len(qg_match)
        qg_match = self.merge_lists(qg_match)

        min_freq = len(prefix) - self.q * delta
        res = []
        for qg in qg_match:
            # only enterys with high freq
            if qg[1] >= min_freq:
                entity_norml = self.normalize(self.entity_name[qg[0] -1])
                self.num_ped += 1
                pref_ped = ped(prefix, entity_norml, int(delta))
                
                if pref_ped <= delta:
                    # (entity_id, ped_val, entity_score
                    res.append((qg[0], pref_ped, self.entity_score[qg[0] - 1]))
        # monitoring
        self.num_res = len(res)
       
        return res

    def rank_matches(self, matches):
        '''
        Ranks the given list of (entity id, PED, s), where PED is the PED
        value and s is the popularity score of an entity.

        The test check for a list of triples containing the entity ID,
        the PED distance and its score:

        [(entity id, PED, score), ...]

        >>> qi = QGramIndex(3)
        >>> qi.rank_matches([(1, 0, 3), (2, 1, 2), (2, 1, 3), (1, 0, 2)])
        [(1, 0, 3), (1, 0, 2), (2, 1, 3), (2, 1, 2)]
        '''
        matches = sorted(matches, key=lambda x: (x[1], -x[2]))
        return matches


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) < 2:
        print("Usage: python3 %s <file>" % sys.argv[0])
        sys.exit()

    file_name = sys.argv[1]
     
    qg = QGramIndex(3)
    time1 = time.monotonic()
    qg.build_from_file(file_name)
    time1 = time.monotonic() - time1
    print("%f" % (time1 * 1000))    
    while True:
        # read input
        query = str(input("Query: "))
        query_n = qg.normalize(query)
       
        # compute match
        delta = len(query_n) / 4 - len(query_n) % 4 / 4
        time1 = time.monotonic()
        res = qg.find_matches(query_n, delta)
        time1 = time.monotonic() - time1
        res = qg.rank_matches(res)
        
        print("result for %s is" % (query))
        for i in range(0, len(res)):
            if i > 4 :
                break
        #    print(res)
            print(qg.entity_name[res[i][0] - 1], qg.entity_score[res[i][0] - 1],
            qg.entity_left[res[i][0] - 1], "\n")
        print("r-time: %f,\tmerges: %d,\t#res: %d,\t#ped: %d" % (time1 * 1000,
        qg.num_merg, qg.num_res, qg.num_ped))
