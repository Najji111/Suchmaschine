#!/bin/python3
"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""

import sys
from inverted_index import InvertedIndex  # NOQA


class Evaluate:
    """
    Class for evaluating the InvertedIndex class against a benchmark.
    """
    def __init__(self):
        self.records = []

    def read_benchmark(self, file_name):
        """
        Read a benchmark from the given file. The expected format of the file
        is one query per line, with the ids of all documents relevant for that
        query, like: <query>TAB<id1>WHITESPACE<id2>WHITESPACE<id3> ...

        >>> evaluate = Evaluate()
        >>> benchmark = evaluate.read_benchmark("example-benchmark.txt")
        >>> sorted(benchmark.items())
        [('animated film', {1, 3, 4}), ('short film', {3, 4})]
        """
        with open(file_name, "r") as file:
            for line in file:
                h1 = line.split("\t")
                h1[0] = h1[0].lower().strip()
                h1[1] = tuple([x.strip() for x in h1[1].split(" ")])
                self.records.append(tuple(h1))

    def evaluate(self, ii, benchmark, use_refinements=False, verbose=True):
        """
        Evaluate the given inverted index against the given benchmark as
        follows. Process each query in the benchmark with the given inverted
        index and compare the result list with the groundtruth in the
        benchmark. For each query, compute the measure P@3, P@R and AP as
        explained in the lecture. Aggregate the values to the three mean
        measures MP@3, MP@R and MAP and return them.

        Implement a parameter 'use_refinements' that controls the use of
        ranking refinements on calling the method process_query of your
        inverted index.

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.txt", b=0.75, k=1.75)
        >>> evaluator = Evaluate()
        >>> benchmark = evaluator.read_benchmark("example-benchmark.txt")
        >>> measures = evaluator.evaluate(ii, benchmark, use_refinements=False,
        ... verbose=False)
        >>> [round(x, 3) for x in measures]
        [0.667, 0.833, 0.694]
        """

        pass  # TODO: add your code

    def precision_at_k(self, result_ids, relevant_ids, k):
        """
        Compute the measure P@k for the given list of result ids as it was
        returned by the inverted index for a single query, and the given set of
        relevant document ids.

        Note that the relevant document ids are 1-based (as they reflect the
        line number in the dataset file).

        >>> evaluator = Evaluate()
        >>> evaluator.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=0)
        0
        >>> evaluator.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=4)
        0.75
        >>> evaluator.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=8)
        0.5
        """

    def average_precision(self, result_ids, relevant_ids):
        """
        Compute the average precision (AP) for the given list of result ids as
        it was returned by the inverted index for a single query, and the given
        set of relevant document ids.

        Note that the relevant document ids are 1-based (as they reflect the
        line number in the dataset file).

        >>> evaluator = Evaluate()
        >>> evaluator.average_precision([7, 17, 9, 42, 5], {5, 7, 12, 42})
        0.525
        """

        pass  # TODO: add your code


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) < 3:
        print("""Usage: python3 evaluate.py """
              """<file> <benchmark> [<b>] [<k>]""")
        sys.exit()
    
    ev = Evaluate()
    ev.read_benchmark(sys.argv[1])
