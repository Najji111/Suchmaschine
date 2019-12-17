"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""

import re
import sys
import math
import numpy
from scipy.sparse import csr_matrix
import scipy

class InvertedIndex:
    """
    An extended version of the inverted index of ES2 that uses Vector Space
    Models.

    For this exercise sheet, you can re-use your implementation from ES 2 or
    build upon the master solution for ES 2. In any case, the code skeleton
    below should be followed and all tests should be implemented.
    """

    def __init__(self):
        """
        Creates an empty inverted index.
        """

        # make sure numpy always prints floats with the same number of
        # digits
        numpy.set_printoptions(formatter={'float': lambda x: ("%.3f" % x)})
        self.inverted_lists = {}  # The inverted lists.
        self.docs = []  # The docs, each in form (title, description).
        self.doc_lengths = []  # The document lengths (= number of words).
        self.td_matrix = None

    def build_from_file(self, file_name, b=None, k=None):
        """
        Construct the inverted index from the given file. The expected format
        of the file is one document per line, in the format
        <title>TAB<description>. Each entry in the inverted list associated to
        a term should contain a document id and a BM25 score. Compute the BM25
        scores as follows:

        (1) In a first pass, compute the inverted lists with tf scores (that
            is the number of occurrences of the term within the <title> and the
            <description> of a document). Further, compute the document length
            (DL) for each document (that is the number of terms in the <title>
            and the <description> of a document). Afterwards, compute the
            average document length (AVDL).
        (2) In a second pass, iterate each inverted list and replace the tf
            scores by BM25 scores, defined as:
            BM25 = tf * (k+1) / (k * (1 - b + b * DL/AVDL) + tf) * log2(N/df),
            where N is the total number of documents and df is the number of
            documents that contains the term.

        On reading the file, use UTF-8 as the standard encoding. To split the
        texts into terms, use the method introduced in the lecture. Make sure
        that you ignore empty terms.

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

        b = DEFAULT_B if b is None else b
        k = DEFAULT_K if k is None else k

        # First pass: Compute (1) the inverted lists with tf scores and (2) the
        # document lengths.
        with open(file_name, "r", encoding="utf-8") as f:
            doc_id = 0
            for line in f:
                line = line.strip()

                dl = 0  # Compute the document length (number of words).
                doc_id += 1

                for word in re.split("[^A-Za-z]+", line):
                    word = word.lower().strip()

                    # Ignore the word if it is empty.
                    if len(word) == 0:
                        continue

                    dl += 1

                    if word not in self.inverted_lists:
                        # The word is seen for first time, create new list.
                        self.inverted_lists[word] = [(doc_id, 1)]
                        continue

                    # Get last posting to check if the doc was already seen.
                    last = self.inverted_lists[word][-1]
                    if last[0] == doc_id:
                        # The doc was already seen, increment tf by 1.
                        self.inverted_lists[word][-1] = (doc_id, last[1] + 1)
                    else:
                        # The doc was not already seen, set tf to 1.
                        self.inverted_lists[word].append((doc_id, 1))

                # Store the doc as a tuple (title, description).
                self.docs.append(tuple(line.split("\t")))

                # Register the document length.
                self.doc_lengths.append(dl)

        # Compute N (the total number of documents).
        n = len(self.docs)
        # Compute AVDL (the average document length).
        avdl = sum(self.doc_lengths) / n

        # Second pass: Iterate the inverted lists and replace the tf scores by
        # BM25 scores, defined as follows:
        # BM25 = tf * (k + 1) / (k * (1 - b + b * DL / AVDL) + tf) * log2(N/df)
        for word, inverted_list in self.inverted_lists.items():
            for i, (doc_id, tf) in enumerate(inverted_list):
                # Obtain the document length (dl) of the document.
                dl = self.doc_lengths[doc_id - 1]  # doc_id is 1-based.
                # Compute alpha = (1 - b + b * DL / AVDL).
                alpha = 1 - b + (b * dl / avdl)
                # Compute tf2 = tf * (k + 1) / (k * alpha + tf).
                tf2 = tf * (1 + (1 / k)) / (alpha + (tf / k)) if k > 0 else 1
                # Compute df (that is the length of the inverted list).
                df = len(self.inverted_lists[word])
                # Compute the BM25 score = tf' * log2(N/df).
                inverted_list[i] = (doc_id, tf2 * math.log(n / df, 2))

    def preprocessing_vsm(self, l2normalize=False):
        """
        Compute the sparse term-document matrix from the inverted lists
        computed by the build_from_file() method

        >>> ii = InvertedIndex() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> ii.build_from_file("example.txt", b=0, k=float("inf"))
        >>> ii.preprocessing_vsm()
        >>> print(numpy.round(sorted(ii.td_matrix.todense().tolist()), 3))
        [[0.000 0.000 0.000 0.000]
         [0.000 0.000 1.000 2.000]
         [0.000 0.000 2.000 0.000]
         [0.000 1.000 0.000 1.000]
         [0.000 2.000 0.000 0.000]
         [0.415 0.415 0.000 0.415]]

        Note: for the following test, L2 normalization is activated!
        >>> ii = InvertedIndex() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> ii.build_from_file("example.txt", b=0.75, k=1.75)
        >>> ii.preprocessing_vsm(l2normalize=True)
        >>> print(numpy.round(sorted(ii.td_matrix.todense().tolist()), 3))
        [[0.000 0.000 0.000 0.000]
         [0.000 0.000 0.447 0.815]
         [0.000 0.000 0.894 0.000]
         [0.000 0.440 0.000 0.535]
         [0.000 0.879 0.000 0.000]
         [1.000 0.182 0.000 0.222]]
        """

        """
        helper = numpy.zeros((len(self.inverted_lists), len(self.docs)))
        record_id = 0
        for key, val in self.inverted_lists.items():
            for doc_id, bm25 in val:
                # all word occurrence
                helper[record_id][doc_id - 1] = bm25
            record_id += 1
 
        # convert to csr
        self.td_matrix = csr_matrix(helper)
        """
    
        val = [] 
        row = [] 
        col = [] 
        
        num_col = 0
        for records_id, (keys, bms) in enumerate(self.inverted_lists.items()):
            for doc_id, bm25 in bms:
                if num_col < doc_id:
                    # max coll id is num of colls is num of documents
                    num_col = doc_id
                
                # all word occurrence
                if bm25 != 0:
                    val.append(bm25)
                    row.append(records_id)
                    col.append(doc_id - 1)
        # convert to csr
        self.td_matrix = csr_matrix((val, (row, col)), shape=(records_id + 1,
        num_col))

        if l2normalize:
            # compute l2-norme
            self.td_matrix = self.l2normalize_cols(self.td_matrix)

    def l2normalize_cols(self, td_matrix):
        """
        Normalizes the columns of the given term-document matrix with respect
        to the L2-norm.

        >>> ii = InvertedIndex() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> matrix = csr_matrix([
        ...  [1, 1, 0, 1, 0, 0],
        ...  [1, 0, 1, 1, 0, 0],
        ...  [1, 1, 1, 2, 1, 1],
        ...  [0, 0, 0, 1, 1, 1]
        ... ])
        >>> norm_matrix = ii.l2normalize_cols(matrix)
        >>> print(numpy.round(norm_matrix.todense().tolist(), 3))
        [[0.577 0.707 0.000 0.378 0.000 0.000]
         [0.577 0.000 0.707 0.378 0.000 0.000]
         [0.577 0.707 0.707 0.756 0.707 0.707]
         [0.000 0.000 0.000 0.378 0.707 0.707]]
        """
      
        # prepare matrix
        td_matrix = td_matrix.astype(float)
        # get indexes of the cells
        rows, cols = td_matrix.nonzero()

        ent_sum = scipy.zeros(td_matrix.shape[1])
        for row, col in zip(rows, cols):
            # sum up enteries by collumns
            ent_sum[col] += td_matrix[row, col]**2        

        # compute the l2-norme
        ent_sum = numpy.sqrt(ent_sum) / ent_sum 

        # write results back to matrix
        for row, col in zip(rows, cols):
            td_matrix[row, col] *= ent_sum[col]
        return td_matrix

    def process_query_vsm(self, keywords):
        """
        Process the given keyword query as in the process_query_vsm() method of
        ES2, but by using VSM.

        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ...   "foo": [(1, 0.2), (3, 0.6)],
        ...   "bar": [(1, 0.4), (2, 0.7), (3, 0.5)],
        ...   "baz": [(2, 0.1)]
        ... }
        >>> ii.preprocessing_vsm()
        >>> result = ii.process_query_vsm(["foo", "bar"])
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(3, '1.1'), (2, '0.7'), (1, '0.6')]

        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ...   "foo": [(1, 0.2), (3, 0.6)],
        ...   "bar": [(2, 0.4), (3, 0.1), (4, 0.8)]
        ... }
        >>> ii.preprocessing_vsm()
        >>> result = ii.process_query_vsm(["foo", "bar", "foo", "bar"])
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(4, '1.6'), (3, '1.4'), (2, '0.8'), (1, '0.4')]
        """

        if not keywords:
            return []

        val = []
        row = []
        for keyword in keywords:
            for ent_id, ent in enumerate(self.inverted_lists.keys()):
                # Fetch the inverted lists for each of the given keywords.
                if keyword == ent:
                    val.append(1)
                    row.append(ent_id)

        if len(val) == 0:
            return []

        # convert the matching key words in to vector 
        query = csr_matrix((val, ([0] * len(row), row)),
        shape=(1, len(self.inverted_lists.keys())))

        # compute the hit rate
        hit_rate = query.dot(self.td_matrix)

        rows, cols = hit_rate.nonzero()
        res = [None] * len(rows)
        for i, (row, col) in enumerate(zip(rows, cols)):
            res[i] = tuple((col + 1, hit_rate[row, col]))
        
        # Sort the postings by BM25 scores, in descending order.
        return sorted(res, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    # Parse the command line arguments.
    #
    # TODO: make sure that any normalization you are using above may
    # be enabled by an additional command line parameter, for example
    # --l2normalize. Per default, your application should use
    # no normalization and BM25 scores with b=0.75 and k=1.75 (see
    # the exercise sheet).
    if len(sys.argv) < 2:
        print("Usage: python3 inverted_index.py <file> [<b>] [<k>]")
        sys.exit()

    file_name = sys.argv[1]
    b = float(sys.argv[2]) if len(sys.argv) > 2 else None
    k = float(sys.argv[3]) if len(sys.argv) > 3 else None

    # Create a new inverted index from the given file.
    print("Reading from file '%s'." % file_name)
    ii = InvertedIndex()
    ii.build_from_file(file_name, b=b, k=k)
    print("Done")
    print("Building sparse term-document matrix.")
    ii.preprocessing_vsm(l2normalize=True)
    print("Done")

    while True:
        # Ask the user for a keyword query.
        query = input("\nYour keyword query: ")

        # Split the query into keywords.
        keywords = [x.lower().strip() for x in re.split("[^A-Za-z]+", query)]

        # Process the keywords.
        postings = ii.process_query_vsm(keywords)
