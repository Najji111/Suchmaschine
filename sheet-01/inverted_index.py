#!/bin/python3
"""
Copyright 2019, University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""

import re
import readline  # NOQA
import sys
import linecache

class InvertedIndex:
    """
    A simple inverted index as explained in lecture 1.
    """

    def __init__(self):
        """
        Creates an empty inverted index.
        """
        self.inverted_lists = {}  # The inverted lists of record ids.

    def read_from_file(self, file_name):
        """
        Constructs the inverted index from given file in linear time (linear in
        the number of words in the file). The expected format of the file is
        one record per line, in the format <title>TAB<description>.

        TODO: Make sure that each inverted list contains a particular record id
        at most once, even if the respective word occurs multiple times in the
        same record.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> sorted(ii.inverted_lists.items())
        [('a', [1, 2]), ('doc', [1, 2, 3]), ('film', [2]), ('movie', [1, 3])]
        """
        with open(file_name, "r") as file:
            record_id = 0
            for line in file:
                line = line.strip()
                record_id += 1

                for word in re.split("[^A-Za-z]+", line):
                    word = word.lower().strip()

                    # Ignore the word if it is empty.
                    if len(word) == 0:
                        continue

                    if word not in self.inverted_lists:
                        # The word is seen for first time, create a new list.
                        self.inverted_lists[word] = []
                        self.inverted_lists[word].append(record_id)
                    else:
                        if self.inverted_lists[word][-1] != record_id:
                            self.inverted_lists[word].append(record_id)

    def intersect(self, list1, list2):
        """
        Computes the intersection of the two given inverted lists in linear
        time (linear in the total number of elements in the two lists).

        >>> ii = InvertedIndex()
        >>> ii.intersect([1, 5, 7], [2, 4])
        []
        >>> ii.intersect([1, 2, 5, 7], [1, 3, 5, 6, 7, 9])
        [1, 5, 7]
        """
        i_sected = []
        l1 = l2 = 0
        # search until end of one list
        while l1 < len(list1) and l2 < len(list2):
            # increase lower
            if list1[l1] < list2[l2]:
                l1 += 1
            elif list1[l1] > list2[l2]:
                l2 += 1
            else:
                # if equal note and increase both
                i_sected.append(list1[l1])
                l1 += 1
                l2 += 1

        return i_sected

    def process_query(self, keywords):
        """
        Processes the given keyword query as follows: Fetches the inverted list
        for each of the keywords in the given query and computes the
        intersection of all inverted lists (which is empty, if there is a
        keyword in the query which has no inverted list in the index).

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> ii.process_query([])
        []
        >>> ii.process_query(["doc", "movie"])
        [1, 3]
        >>> ii.process_query(["doc", "movie", "comedy"])
        []
        """
        res = []
        # Convert a string to list
        if not isinstance(keywords, list):
            keywords = list(keywords.split(" "))
        # Search the inverdex index for each word and computed the results.
        for word in keywords:
            word = word.lower().strip()
            if self.inverted_lists.get(word) is None:
                return []
            elif len(res) == 0:
                res = self.inverted_lists[word]
                continue

            # intersect last result with current
            res = self.intersect(res,
                                 self.inverted_lists[word])

        return res

    def main(self, file_name):    
        """
        Reads line by line the file in argv[1]. Subsequent read keyword from std
        input, process query and print results until most three records.
        """
        self.read_from_file(file_name)

        res = []
        while True:
            word = str(input("Query: ")).lower().strip()
            res = self.process_query(word)
            
            # Print lines of the first three results.
            for i in range(1, 4):
                if i > len(res):
                    break
                print(linecache.getline(file_name, res[i-1]))
            # reset first time label
            b_first = False
        
        linecache.clearcache()


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) != 2:
        print("Usage: python3 inverted_index.py <file>")
        sys.exit()

    file_name = sys.argv[1]
    ii = InvertedIndex()
#    ii.read_from_file(file_name)

#    for word, inverted_list in ii.inverted_lists.items():
#        print("%d\t%s" % (len(inverted_list), word))

    ii.main(file_name)
    


