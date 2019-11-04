#!/bin/python3
"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""
import readline  # NOQA
import re
import sys
import math


class InvertedIndex:
    """
    A simple inverted index that uses BM25 scores.
    """

    def __init__(self):
        """
        Creates an empty inverted index.
        """

        self.inverted_lists = {}  # The inverted lists of record ids.
        self.records = []  # The records, each in form (title, description).

    def build_from_file(self, file_name, b=None, k=None):
        """
        Construct the inverted index from the given file. The expected format
        of the file is one document per line, in the format
        <title>TAB<description>. Each entry in the inverted list associated to
        a word should contain a document id and a BM25 score. Compute the BM25
        scores as follows:

        (1) In a first pass, compute the inverted lists with tf scores (that
            is the number of occurrences of the word within the <title> and the
            <description> of a document). Further, compute the document length
            (DL) for each document (that is the number of words in the <title>
            and the <description> of a document). Afterwards, compute the
            average document length (AVDL).
        (2) In a second pass, iterate each inverted list and replace the tf
            scores by BM25 scores, defined as:
            BM25 = tf * (k+1) / (k * (1 - b + b * DL/AVDL) + tf) * log2(N/df),
            where N is the total number of documents and df is the number of
            documents that contains the word.

        On reading the file, use UTF-8 as the standard encoding. To split the
        texts into words, use the method introduced in the lecture. Make sure
        that you ignore empty words.

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.txt", b=0, k=float("inf"))
        >>> inv_lists = sorted(ii.inverted_lists.items())
        >>> [(w, [(i, '%.3f' % tf) for i, tf in l]) for w, l in inv_lists]
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, '0.415'), (2, '0.415'), (4, '0.415')]),
         ('animation', [(3, '2.000')]),
         ('film', [(2, '1.000'), (4, '1.000')]),
         ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
         ('non', [(2, '2.000')]),
         ('short', [(3, '1.000'), (4, '2.000')])]

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.txt", b=0.75, k=1.75)
        >>> inv_lists = sorted(ii.inverted_lists.items())
        >>> [(w, [(i, '%.3f' % tf) for i, tf in l]) for w, l in inv_lists]
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, '0.459'), (2, '0.402'), (4, '0.358')]),
         ('animation', [(3, '2.211')]),
         ('film', [(2, '0.969'), (4, '0.863')]),
         ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
         ('non', [(2, '1.938')]),
         ('short', [(3, '1.106'), (4, '1.313')])]
        """
        with open(file_name, "r") as file:
            record_id = 0
            # document length and its average (by words)
            dll = []
            dl = 0
            for line in file:
                line = line.strip()

                record_id += 1

                # Store the record as a tuple (title, description).
                self.records.append(tuple(line.split("\t")))

                for word in re.split("[^A-Za-z]+", line):
                    word = word.lower().strip()

                    # Ignore the word if it is empty.
                    if len(word) == 0:
                        continue
                    dl += 1

                    if word not in self.inverted_lists:
                        # The word is seen for first time, create a new list.
                        self.inverted_lists[word] = [[record_id, 1]]
                    elif self.inverted_lists[word][-1][0] != record_id:
                        # Make sure that the list contains the id at most once.
                        self.inverted_lists[word].append([record_id, 1])
                    else:  # count the occurence of the word in the record (tf)
                        self.inverted_lists[word][-1][1] = \
                            self.inverted_lists[word][-1][1] + 1

                # counter for average
                dll.append(dl)
                dl = 0

            avdl = sum(dll) / record_id
            for iil in self.inverted_lists.values():
                for ii in iil:
                    # claulate bm25, override the tf
                    if math.isinf(k):
                        helper = ii[1]
                    else:
                        helper = ii[1] * (k + 1) / \
                            (k * (1 - b + b * dll[ii[0]-1] / avdl) + ii[1])
                    ii[1] = helper * math.log2(record_id / len(iil))

    def merge(self, list1, list2):
        """
        Compute the union of the two given inverted lists in linear time
        (linear in the total number of entries in the two lists), where the
        entries in the inverted lists are postings of form (doc_id, bm25_score)
        and are expected to be sorted by doc_id, in ascending order.

        >>> ii = InvertedIndex()
        >>> l1 = ii.merge([(1, 2.1), (5, 3.2)], [(1, 1.7), (2, 1.3), (6, 3.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l1]
        [(1, '3.8'), (2, '1.3'), (5, '3.2'), (6, '3.3')]

        >>> l2 = ii.merge([(3, 1.7), (5, 3.2), (7, 4.1)], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (3, '1.7'), (5, '4.5'), (7, '4.1')]

        >>> l2 = ii.merge([], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (5, '1.3')]

        >>> l2 = ii.merge([(1, 2.3)], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3')]

        >>> l2 = ii.merge([], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        []
        """
        merged = []
        l1 = l2 = 0
        while l1 < len(list1) and l2 < len(list2):
            if list1[l1][0] < list2[l2][0]:
                merged.append(tuple(list1[l1]))
                l1 += 1
            elif list1[l1][0] > list2[l2][0]:
                merged.append(tuple(list2[l2]))
                l2 += 1
            else:  # sum the bm25 value and add to the record
                merged.append((list1[l1][0], list1[l1][1] + list2[l2][1]))
                l1 += 1
                l2 += 1

        # merge ends
        if l1 < len(list1):
            for x in list1[l1:len(list1)]:
                merged.append(x)
        elif l2 < len(list2):
            for x in list2[l2:len(list2)]:
                merged.append(x)
        return merged

    def process_query(self, keywords, use_refinements=False):
        """
        Process the given keyword query as follows: Fetch the inverted list for
        each of the keywords in the query and compute the union of all lists.
        Sort the resulting list by BM25 scores in descending order.

        This method returns _all_ results for the given query, not just the
        top 3!

        If you want to implement some ranking refinements, make these
        refinements optional (their use should be controllable via the
        use_refinements flag).

        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ... "foo": [(1, 0.2), (3, 0.6)],
        ... "bar": [(1, 0.4), (2, 0.7), (3, 0.5)],
        ... "baz": [(2, 0.1)]}
        >>> result = ii.process_query(["foo", "bar"], use_refinements=False)
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(3, '1.1'), (2, '0.7'), (1, '0.6')]
        """
        res = []
        # Convert a string to list
        if not isinstance(keywords, list):
            keywords = list(keywords.split(" "))
        # Search the inverdex index for each word and computed the results.
        for word in keywords:
            word = word.lower().strip()
            if self.inverted_lists.get(word) is None:
                continue
            elif len(res) == 0:
                res = self.inverted_lists[word]
                continue

            # intersect last result with current
            res = self.merge(res, self.inverted_lists[word])

        res.sort(key=lambda x: x[1], reverse=True)
        return res


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) < 2:
        print("Usage: python3 inverted_index.py <file> [<b>] [<k>]")
        sys.exit()

    ii = InvertedIndex()
    ii.build_from_file(sys.argv[1], b=0.75, k=1.75)

    res = []
    while True:
        word = str(input("Query: "))
        res = ii.process_query(word)
        print(res)
        # Print lines of the first three results.
        for index, bm25 in res:
            print(ii.records[index - 1])
