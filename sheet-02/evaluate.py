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
        # open file and read lines
        bm = dict()
        with open(file_name, "r") as file:
            for line in file:
                # create a dict containig a set with the ids as second
                # place
                h = line.split("\t")
                h[0] = h[0].lower().strip()
                h[1] = set([int(x.strip()) for x in h[1].split(" ")])
                bm[h[0]] = h[1]
        return bm

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
        pk = pr = ap = 0
        c = 0
        # test each benchmark
        for b_qu  in benchmark:
            # query records 
            iil = ii.process_query(b_qu)
            iil_id = [x for x, y in iil]
            # compute p@k
            pk += self.precision_at_k(iil_id, benchmark[b_qu], 3)
            pr += self.precision_at_k(iil_id, benchmark[b_qu],
            len(benchmark[b_qu]))
            ap += self.average_precision(iil_id, benchmark[b_qu])

            c += 1
        # mp@3, mp@r, map
        return [pk / c, pr / c, ap / c]

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
        if k == 0:
            return 0

        if k > len(result_ids):
            # iterate only till list end
            ki = len(result_ids)
        else:
            ki = k

        # check if result_ids are in the set of relevant_ids 
        hits = 0
        for r_id in range(0, ki):
            if result_ids[r_id] in relevant_ids:
                # count hits
                hits += 1
        return hits / k 

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
        # counter for computing
        ap = hits = total = 0
        for r_id in result_ids:
            total += 1
            if r_id in relevant_ids:
                # count hit, sum percent values
                hits += 1
                ap += hits / total
        return ap / len(relevant_ids)


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) < 3:
        print("""Usage: python3 evaluate.py """
              """<file> <benchmark> [<b>] [<k>]""")
        sys.exit()
    # check skaling parameter
    if len(sys.argv) < 4:
        b = 0
    elif len(sys.argv) < 5:
        b = argv[3]
        k = 0
    else:
        b = argv[3]
        k = argv[4]

    # inverted index
    ii = InvertedIndex()
    ii.build_from_file(sys.argv[1], b=0.75, k=1.75)
    # evaluation
    ev = Evaluate()
    bm = ev.read_benchmark(sys.argv[2])
    print(ev.evaluate(ii, bm))
